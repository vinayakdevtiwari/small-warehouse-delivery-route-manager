"""SQLite persistence and safe, transactional service functions for the PBL.

This is a local-first educational app using simulated seed data. All stock/order
mutations are performed in transactions to avoid accidentally double-reserving
stock when an order is placed.
"""
from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from typing import Any

from unit2_graphs.adjacency_list import AdjacencyListGraph
from unit2_graphs.dijkstra import dijkstra_shortest_path
from unit1_trees.priority_queue import PriorityQueue
from unit3_dynamic_programming.knapsack import Parcel, knapsack_01
from unit4_backtracking.tsp_branch_bound import tsp_branch_and_bound

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = Path(os.environ.get("WAREHOUSE_DB_PATH", ROOT / "data" / "warehouse_manager.sqlite3"))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH, timeout=10, isolation_level=None)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 10000")
    return connection


def init_db() -> None:
    """Create tables and seed small simulated data once."""
    with connect() as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS locations (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                kind TEXT NOT NULL CHECK(kind IN ('warehouse','depot','customer','outlet'))
            );
            CREATE TABLE IF NOT EXISTS warehouses (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                location_id TEXT NOT NULL UNIQUE REFERENCES locations(id)
            );
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                unit_weight INTEGER NOT NULL CHECK(unit_weight > 0),
                unit_value REAL NOT NULL CHECK(unit_value >= 0)
            );
            CREATE TABLE IF NOT EXISTS stock (
                warehouse_id INTEGER NOT NULL REFERENCES warehouses(id),
                product_id INTEGER NOT NULL REFERENCES products(id),
                quantity INTEGER NOT NULL CHECK(quantity >= 0),
                PRIMARY KEY (warehouse_id, product_id)
            );
            CREATE TABLE IF NOT EXISTS routes (
                source_id TEXT NOT NULL REFERENCES locations(id),
                destination_id TEXT NOT NULL REFERENCES locations(id),
                distance REAL NOT NULL CHECK(distance >= 0),
                PRIMARY KEY(source_id, destination_id),
                CHECK(source_id < destination_id)
            );
            CREATE TABLE IF NOT EXISTS orders (
                id TEXT PRIMARY KEY,
                product_id INTEGER NOT NULL REFERENCES products(id),
                quantity INTEGER NOT NULL CHECK(quantity > 0),
                destination_id TEXT NOT NULL REFERENCES locations(id),
                priority INTEGER NOT NULL CHECK(priority BETWEEN 1 AND 3),
                status TEXT NOT NULL CHECK(status IN ('Confirmed','Dispatched','Delivered','Cancelled')),
                created_at TEXT NOT NULL,
                assigned_warehouse_id INTEGER NOT NULL REFERENCES warehouses(id),
                route_json TEXT NOT NULL,
                distance REAL NOT NULL CHECK(distance >= 0),
                payload_weight INTEGER NOT NULL CHECK(payload_weight > 0),
                order_value REAL NOT NULL CHECK(order_value >= 0)
            );
        """)
        if db.execute("SELECT COUNT(*) FROM locations").fetchone()[0] == 0:
            locations = [
                ("WH_NORTH", "North Warehouse", "warehouse"),
                ("WH_CENTRAL", "Central Warehouse", "warehouse"),
                ("WH_SOUTH", "South Warehouse", "warehouse"),
                ("DEPOT_EAST", "East Depot", "depot"),
                ("HUB_ALPHA", "Customer Hub Alpha", "customer"),
                ("HUB_BETA", "Customer Hub Beta", "customer"),
                ("OUTLET_1", "Retail Outlet 1", "outlet"),
                ("OUTLET_2", "Retail Outlet 2", "outlet"),
                ("CUSTOMER_C", "Customer C", "customer"),
                ("CUSTOMER_D", "Customer D", "customer"),
            ]
            db.executemany("INSERT INTO locations VALUES (?,?,?)", locations)
        if db.execute("SELECT COUNT(*) FROM warehouses").fetchone()[0] == 0:
            db.executemany(
                "INSERT INTO warehouses(id,name,location_id) VALUES (?,?,?)",
                [(1, "North Warehouse", "WH_NORTH"),
                 (2, "Central Warehouse", "WH_CENTRAL"),
                 (3, "South Warehouse", "WH_SOUTH")]
            )
        if db.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
            products = [
                (1001, "Shipping Box", "Packaging", 2, 120.0),
                (1002, "Laptop", "Electronics", 5, 50000.0),
                (1003, "Monitor", "Electronics", 8, 12000.0),
                (1004, "Packing Tape", "Packaging", 1, 90.0),
                (1005, "Digital Camera", "Electronics", 3, 28000.0),
                (1006, "Printer", "Office", 7, 9000.0),
                (1007, "Bubble Wrap Roll", "Packaging", 2, 250.0),
                (1008, "Barcode Scanner", "Equipment", 1, 3500.0),
            ]
            db.executemany("INSERT INTO products VALUES (?,?,?,?,?)", products)
        if db.execute("SELECT COUNT(*) FROM stock").fetchone()[0] == 0:
            stock = [
                (1, 1001, 45), (1, 1002, 8), (1, 1003, 10), (1, 1004, 60),
                (1, 1005, 4), (1, 1006, 6), (1, 1007, 22), (1, 1008, 12),
                (2, 1001, 30), (2, 1002, 12), (2, 1003, 6), (2, 1004, 40),
                (2, 1005, 7), (2, 1006, 9), (2, 1007, 18), (2, 1008, 15),
                (3, 1001, 25), (3, 1002, 5), (3, 1003, 8), (3, 1004, 50),
                (3, 1005, 3), (3, 1006, 5), (3, 1007, 24), (3, 1008, 10),
            ]
            db.executemany("INSERT INTO stock VALUES (?,?,?)", stock)
        if db.execute("SELECT COUNT(*) FROM routes").fetchone()[0] == 0:
            routes = [
                ("WH_CENTRAL", "WH_NORTH", 5.0),
                ("WH_CENTRAL", "WH_SOUTH", 6.0),
                ("DEPOT_EAST", "WH_CENTRAL", 3.0),
                ("DEPOT_EAST", "WH_NORTH", 4.0),
                ("DEPOT_EAST", "HUB_ALPHA", 4.0),
                ("HUB_ALPHA", "HUB_BETA", 6.0),
                ("HUB_ALPHA", "OUTLET_1", 3.0),
                ("CUSTOMER_C", "HUB_ALPHA", 2.0),
                ("CUSTOMER_C", "OUTLET_1", 5.0),
                ("CUSTOMER_D", "HUB_BETA", 3.0),
                ("CUSTOMER_D", "OUTLET_2", 5.0),
                ("HUB_BETA", "OUTLET_2", 3.0),
                ("HUB_BETA", "WH_SOUTH", 5.0),
                ("OUTLET_1", "WH_NORTH", 6.0),
                ("OUTLET_2", "WH_CENTRAL", 4.0),
                ("OUTLET_2", "WH_SOUTH", 2.0),
            ]
            # Store undirected routes using a canonical pair so the graph does
            # not receive duplicate edges when rebuilding its adjacency list.
            routes = [(min(a, b), max(a, b), d) for a, b, d in routes]
            routes = list({(a, b): (a, b, d) for a, b, d in routes}.values())
            db.executemany("INSERT INTO routes VALUES (?,?,?)", routes)


def list_locations(kind: str | None = None) -> list[dict[str, Any]]:
    with connect() as db:
        if kind:
            rows = db.execute("SELECT * FROM locations WHERE kind=? ORDER BY name", (kind,)).fetchall()
        else:
            rows = db.execute("SELECT * FROM locations ORDER BY kind,name").fetchall()
        return [dict(row) for row in rows]


def list_warehouses() -> list[dict[str, Any]]:
    with connect() as db:
        rows = db.execute("SELECT * FROM warehouses ORDER BY id").fetchall()
        return [dict(row) for row in rows]


def list_products() -> list[dict[str, Any]]:
    with connect() as db:
        rows = db.execute("SELECT * FROM products ORDER BY id").fetchall()
        return [dict(row) for row in rows]


def get_product(product_id: int) -> dict[str, Any] | None:
    with connect() as db:
        row = db.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
        return dict(row) if row else None


def get_stock(product_id: int | None = None) -> list[dict[str, Any]]:
    query = """SELECT w.id AS warehouse_id, w.name AS warehouse, p.id AS product_id,
                      p.name AS product, p.category, p.unit_weight, p.unit_value,
                      s.quantity, (s.quantity*p.unit_weight) AS available_weight
               FROM stock s JOIN warehouses w ON w.id=s.warehouse_id
               JOIN products p ON p.id=s.product_id"""
    params: tuple[Any, ...] = ()
    if product_id is not None:
        query += " WHERE p.id=?"
        params = (product_id,)
    query += " ORDER BY w.id,p.id"
    with connect() as db:
        return [dict(r) for r in db.execute(query, params).fetchall()]


def list_routes() -> list[dict[str, Any]]:
    with connect() as db:
        return [dict(r) for r in db.execute(
            """SELECT r.source_id, a.name AS source, r.destination_id, b.name AS destination,
                      r.distance
               FROM routes r JOIN locations a ON a.id=r.source_id
               JOIN locations b ON b.id=r.destination_id ORDER BY a.name,b.name"""
        ).fetchall()]


def build_graph() -> AdjacencyListGraph[str]:
    graph: AdjacencyListGraph[str] = AdjacencyListGraph(directed=False)
    with connect() as db:
        vertices = db.execute("SELECT id FROM locations ORDER BY id").fetchall()
        routes = db.execute("SELECT source_id,destination_id,distance FROM routes").fetchall()
    for row in vertices:
        graph.add_vertex(row["id"])
    for row in routes:
        graph.add_edge(row["source_id"], row["destination_id"], float(row["distance"]))
    return graph


def list_orders(status: str | None = None, warehouse_id: int | None = None) -> list[dict[str, Any]]:
    query = """SELECT o.*, p.name AS product_name, w.name AS warehouse_name,
                      l.name AS destination_name
               FROM orders o JOIN products p ON p.id=o.product_id
               JOIN warehouses w ON w.id=o.assigned_warehouse_id
               JOIN locations l ON l.id=o.destination_id"""
    where: list[str] = []
    params: list[Any] = []
    if status:
        where.append("o.status=?")
        params.append(status)
    if warehouse_id is not None:
        where.append("o.assigned_warehouse_id=?")
        params.append(warehouse_id)
    if where:
        query += " WHERE " + " AND ".join(where)
    query += " ORDER BY o.created_at DESC"
    with connect() as db:
        return [dict(r) for r in db.execute(query, params).fetchall()]


def place_order(product_id: int, quantity: int, destination_id: str, priority: int) -> dict[str, Any]:
    """Choose nearest warehouse with enough stock, reserve it atomically, and record the route."""
    if quantity <= 0:
        raise ValueError("Quantity must be at least 1.")
    if priority not in (1, 2, 3):
        raise ValueError("Priority must be 1 (Urgent), 2 (High) or 3 (Normal).")
    graph = build_graph()
    if destination_id not in graph.vertices:
        raise ValueError("Select a valid delivery destination.")

    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            product = db.execute("SELECT * FROM products WHERE id=?", (product_id,)).fetchone()
            if product is None:
                raise ValueError("Product ID does not exist.")
            candidates = db.execute(
                """SELECT w.id, w.name, w.location_id, s.quantity
                   FROM warehouses w JOIN stock s ON s.warehouse_id=w.id
                   WHERE s.product_id=? AND s.quantity>=?
                   ORDER BY w.id""",
                (product_id, quantity),
            ).fetchall()
            possible: list[tuple[float, int, str, str, list[str]]] = []
            for warehouse in candidates:
                path, distance = dijkstra_shortest_path(graph, warehouse["location_id"], destination_id)
                if path and distance != float("inf"):
                    possible.append((distance, int(warehouse["id"]), warehouse["name"],
                                     warehouse["location_id"], path))
            if not possible:
                any_stock = db.execute(
                    "SELECT COALESCE(MAX(quantity),0) FROM stock WHERE product_id=?", (product_id,)
                ).fetchone()[0]
                if any_stock < quantity:
                    raise ValueError(f"Insufficient stock. Maximum available at any single warehouse: {any_stock}.")
                raise ValueError("No delivery route connects the eligible warehouses to this destination.")
            distance, warehouse_id, warehouse_name, source_id, path = min(possible, key=lambda x: (x[0], x[1]))
            db.execute(
                "UPDATE stock SET quantity=quantity-? WHERE warehouse_id=? AND product_id=? AND quantity>=?",
                (quantity, warehouse_id, product_id, quantity),
            )
            if db.execute("SELECT changes()").fetchone()[0] != 1:
                raise ValueError("Stock changed concurrently; please try placing the order again.")
            order_id = "ORD-" + uuid4().hex[:8].upper()
            payload_weight = int(product["unit_weight"]) * quantity
            order_value = float(product["unit_value"]) * quantity
            created_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
            db.execute(
                """INSERT INTO orders
                   (id,product_id,quantity,destination_id,priority,status,created_at,
                    assigned_warehouse_id,route_json,distance,payload_weight,order_value)
                   VALUES (?,?,?,?,?,'Confirmed',?,?,?,?,?,?)""",
                (order_id, product_id, quantity, destination_id, priority, created_at,
                 warehouse_id, json.dumps(path), distance, payload_weight, order_value),
            )
            db.commit()
            return {
                "id": order_id, "warehouse": warehouse_name, "route": path,
                "distance": distance, "payload_weight": payload_weight,
                "order_value": order_value, "status": "Confirmed",
            }
        except Exception:
            db.rollback()
            raise


def transition_order(order_id: str, target_status: str) -> None:
    allowed = {"Confirmed": {"Dispatched", "Cancelled"}, "Dispatched": {"Delivered"}}
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            row = db.execute("SELECT * FROM orders WHERE id=?", (order_id,)).fetchone()
            if row is None:
                raise ValueError("Order was not found.")
            current = row["status"]
            if target_status not in allowed.get(current, set()):
                raise ValueError(f"Cannot change order from {current} to {target_status}.")
            if target_status == "Cancelled":
                db.execute(
                    "UPDATE stock SET quantity=quantity+? WHERE warehouse_id=? AND product_id=?",
                    (row["quantity"], row["assigned_warehouse_id"], row["product_id"]),
                )
            db.execute("UPDATE orders SET status=? WHERE id=?", (target_status, order_id))
            db.commit()
        except Exception:
            db.rollback()
            raise


def dispatch_queue(warehouse_id: int | None = None) -> list[dict[str, Any]]:
    """Use the existing stable priority queue, then return orders in dispatch order."""
    orders = list_orders(status="Confirmed", warehouse_id=warehouse_id)
    queue: PriorityQueue[dict[str, Any]] = PriorityQueue()
    for order in orders:
        queue.enqueue(order, int(order["priority"]))
    ordered: list[dict[str, Any]] = []
    while not queue.is_empty():
        ordered.append(queue.dequeue().item)
    return ordered


def knapsack_plan(warehouse_id: int, capacity: int) -> dict[str, Any]:
    """Select confirmed orders for one warehouse using 0/1 Knapsack."""
    if capacity < 0:
        raise ValueError("Capacity cannot be negative.")
    orders = dispatch_queue(warehouse_id)
    parcels = [
        Parcel(order_id=o["id"], weight=int(o["payload_weight"]), value=float(o["order_value"]))
        for o in orders
    ]
    value, selected, table = knapsack_01(parcels, int(capacity))
    selected_ids = {p.order_id for p in selected}
    selected_orders = [o for o in orders if o["id"] in selected_ids]
    return {
        "capacity": int(capacity), "value": value,
        "selected": selected_orders,
        "total_weight": sum(int(o["payload_weight"]) for o in selected_orders),
        "all_candidates": orders,
    }


def optimize_multi_stop_tour(start_id: str, stop_ids: list[str]) -> tuple[list[str], float]:
    """Use Dijkstra distances to build a complete stop graph, then run Unit 4 TSP B&B."""
    selected = list(dict.fromkeys([start_id] + [s for s in stop_ids if s != start_id]))
    if len(selected) < 2:
        raise ValueError("Choose at least one stop in addition to the starting warehouse.")
    if len(selected) > 7:
        raise ValueError("Branch & Bound TSP is exponential; choose no more than 6 delivery stops plus the start.")
    road_graph = build_graph()
    complete: dict[str, dict[str, float]] = {node: {} for node in selected}
    for source in selected:
        if source not in road_graph.vertices:
            raise ValueError(f"Unknown location: {source}")
        distances, _ = __import__("unit2_graphs.dijkstra", fromlist=["dijkstra"]).dijkstra(road_graph, source)
        for destination in selected:
            if source != destination:
                distance = distances.get(destination, float("inf"))
                if distance == float("inf"):
                    raise ValueError(f"No route connects {source} to {destination}.")
                complete[source][destination] = distance
    route, distance = tsp_branch_and_bound(complete, start_id)
    return [str(x) for x in route], float(distance)


def add_stock(warehouse_id: int, product_id: int, delta: int) -> int:
    """Adjust inventory safely; negative adjustments cannot exceed available stock."""
    if delta == 0:
        raise ValueError("Stock adjustment cannot be zero.")
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            row = db.execute(
                "SELECT quantity FROM stock WHERE warehouse_id=? AND product_id=?",
                (warehouse_id, product_id),
            ).fetchone()
            if row is None:
                raise ValueError("Stock record does not exist.")
            new_quantity = int(row["quantity"]) + delta
            if new_quantity < 0:
                raise ValueError("Stock cannot become negative.")
            db.execute(
                "UPDATE stock SET quantity=? WHERE warehouse_id=? AND product_id=?",
                (new_quantity, warehouse_id, product_id),
            )
            db.commit()
            return new_quantity
        except Exception:
            db.rollback()
            raise


def add_product(product_id: int, name: str, category: str, unit_weight: int, unit_value: float,
                initial_stock: dict[int, int]) -> None:
    if product_id <= 0 or not name.strip() or not category.strip():
        raise ValueError("Enter a positive product ID, product name and category.")
    if unit_weight <= 0 or unit_value < 0:
        raise ValueError("Weight must be positive and value cannot be negative.")
    if any(q < 0 for q in initial_stock.values()):
        raise ValueError("Initial stock cannot be negative.")
    with connect() as db:
        db.execute("BEGIN IMMEDIATE")
        try:
            db.execute(
                "INSERT INTO products(id,name,category,unit_weight,unit_value) VALUES (?,?,?,?,?)",
                (product_id, name.strip(), category.strip(), unit_weight, unit_value),
            )
            for warehouse_id, quantity in initial_stock.items():
                db.execute(
                    "INSERT INTO stock(warehouse_id,product_id,quantity) VALUES (?,?,?)",
                    (warehouse_id, product_id, quantity),
                )
            db.commit()
        except sqlite3.IntegrityError as exc:
            db.rollback()
            raise ValueError("Product ID already exists or an inventory entry is invalid.") from exc
        except Exception:
            db.rollback()
            raise


def dashboard_metrics() -> dict[str, Any]:
    with connect() as db:
        products = db.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        warehouses = db.execute("SELECT COUNT(*) FROM warehouses").fetchone()[0]
        locations = db.execute("SELECT COUNT(*) FROM locations").fetchone()[0]
        stock_units = db.execute("SELECT COALESCE(SUM(quantity),0) FROM stock").fetchone()[0]
        status_rows = db.execute("SELECT status,COUNT(*) AS count FROM orders GROUP BY status").fetchall()
        return {
            "products": products, "warehouses": warehouses,
            "locations": locations, "stock_units": stock_units,
            "orders_by_status": {r["status"]: r["count"] for r in status_rows},
        }
