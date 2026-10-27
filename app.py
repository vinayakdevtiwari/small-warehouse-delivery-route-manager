"""Streamlit UI for Small Warehouse and Delivery Route Manager.

Run with: streamlit run app.py
All initial locations, distances, inventory and prices are simulated academic
examples. The app does not claim real-time maps, GPS or traffic data.
"""
from __future__ import annotations

import streamlit as st
import pandas as pd

from warehouse_app.database import (
    add_product, add_stock, build_graph, dashboard_metrics, dispatch_queue,
    get_product, get_stock, init_db, knapsack_plan, list_locations, list_orders,
    list_products, list_routes, list_warehouses, optimize_multi_stop_tour,
    place_order, transition_order,
)
from unit2_graphs.dijkstra import dijkstra_shortest_path
from unit3_dynamic_programming.knapsack import Parcel, knapsack_01
from unit4_backtracking.graph_coloring import color_graph
from unit4_backtracking.hamiltonian_cycle import find_hamiltonian_cycle
from unit4_backtracking.n_queens import solve_n_queens
from unit4_backtracking.sum_of_subsets import sum_of_subsets
from unit5_advanced.b_tree import BTree
from unit5_advanced.b_plus_tree import BPlusTree
from unit5_advanced.binomial_heap import BinomialHeap
from unit5_advanced.fibonacci_heap import FibonacciHeap
from unit5_advanced.red_black_tree import RedBlackTree

st.set_page_config(
    page_title="WarehouseFlow | DSA-II",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #f5f7fb 0%, #eef3fa 100%); }
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 1500px; }
    .hero {
        padding: 1.45rem 1.7rem; border-radius: 18px; color: white;
        background: linear-gradient(115deg, #14213d 0%, #243b67 58%, #087e8b 100%);
        margin-bottom: 1.2rem;
    }
    .hero h1 { margin: 0; font-size: 2.1rem; color: #ffffff; }
    .hero p { margin: .45rem 0 0; color: #e1e9f4; font-size: 1rem; }
    .small-note { color: #68758a; font-size: .87rem; }
    .route-pill {
        display:inline-block; padding:.45rem .75rem; background:#e3f5f2;
        color:#075e54; border-radius:999px; margin:.2rem .25rem .2rem 0;
        font-weight:600; border:1px solid #b7e3dc;
    }
    div[data-testid="stMetric"] { background:#ffffff; border:1px solid #e4e9f2;
        padding: .85rem 1rem; border-radius: 14px; box-shadow:0 3px 14px #15294b0a; }
    div[data-testid="stForm"] { background:#ffffff; border:1px solid #e4e9f2;
        padding:1rem 1.15rem; border-radius:14px; }
    .section-caption { color:#60708a; margin-top:-.4rem; }
</style>
""", unsafe_allow_html=True)

init_db()
products = list_products()
warehouses = list_warehouses()
locations = list_locations()
location_names = {item["id"]: item["name"] for item in locations}
warehouse_names = {item["id"]: item["name"] for item in warehouses}
product_names = {item["id"]: f'{item["id"]} — {item["name"]}' for item in products}
location_ids = [item["id"] for item in locations]

# Rebuild in-memory DSA indexes from authoritative SQLite records on each run.
# The database remains the source of truth; indexes are fast, disposable views.
rb_index = RedBlackTree[int, dict]()
bplus_index = BPlusTree[int, dict](order=4)
btree_index = BTree[int, dict](minimum_degree=2)
for product in products:
    pid = int(product["id"])
    rb_index.insert(pid, product)
    bplus_index.insert(pid, product)
    btree_index.insert(pid, product)

with st.sidebar:
    st.markdown("## 📦 WarehouseFlow")
    st.caption("Small Warehouse & Delivery Route Manager")
    st.divider()
    st.markdown("**Project scope**")
    st.write("Inventory · Dispatch · Weighted routes · Capacity planning")
    st.markdown("**DSA focus**")
    st.write("BST/RB/B+ Tree · Priority Queue · Dijkstra · Knapsack · Backtracking")
    st.divider()
    st.caption("DSA-II academic project")
    st.caption("Simulated data; no live traffic or GPS.")

st.markdown("""
<div class="hero">
  <h1>WarehouseFlow</h1>
  <p>Inventory intelligence, priority-based dispatch and cost-aware delivery routing — powered by DSA-II.</p>
</div>
""", unsafe_allow_html=True)

tab_dashboard, tab_inventory, tab_orders, tab_dispatch, tab_routes, tab_capacity, tab_lab = st.tabs([
    "Overview", "Inventory", "Create Order", "Dispatch", "Route Planner", "Vehicle Capacity", "DSA Lab"
])

# ---------------------------------------------------------------------------
# Overview
# ---------------------------------------------------------------------------
with tab_dashboard:
    metrics = dashboard_metrics()
    status_counts = metrics["orders_by_status"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Products", metrics["products"])
    c2.metric("Warehouses", metrics["warehouses"])
    c3.metric("Network Locations", metrics["locations"])
    c4.metric("Units in Stock", f'{metrics["stock_units"]:,}')
    st.subheader("Operations snapshot")
    order_cols = st.columns(4)
    for col, status in zip(order_cols, ["Confirmed", "Dispatched", "Delivered", "Cancelled"]):
        col.metric(status, status_counts.get(status, 0))
    left, right = st.columns([1.15, 1])
    with left:
        st.markdown("### Inventory by warehouse")
        stock_rows = get_stock()
        stock_df = pd.DataFrame(stock_rows)
        if not stock_df.empty:
            summary = stock_df.groupby("warehouse", as_index=False).agg(
                SKU_Count=("product_id", "nunique"), Total_Units=("quantity", "sum")
            )
            st.dataframe(summary, use_container_width=True, hide_index=True)
    with right:
        st.markdown("### Recent orders")
        recent = list_orders()[:6]
        if recent:
            recent_df = pd.DataFrame([{
                "Order": o["id"], "Product": o["product_name"], "Destination": o["destination_name"],
                "Status": o["status"], "Distance (km)": round(o["distance"], 1)
            } for o in recent])
            st.dataframe(recent_df, use_container_width=True, hide_index=True)
        else:
            st.info("No orders yet. Create a simulated order to see the workflow.")
    st.markdown("### System workflow")
    steps = st.columns(5)
    for col, number, label, desc in [
        (steps[0], "01", "Inventory", "Find product and stock"),
        (steps[1], "02", "Warehouse", "Eligible stock + route"),
        (steps[2], "03", "Dijkstra", "Lowest-distance path"),
        (steps[3], "04", "Priority Queue", "Order dispatch sequence"),
        (steps[4], "05", "Knapsack", "Vehicle load selection"),
    ]:
        with col:
            st.markdown(f"**{number} · {label}**")
            st.caption(desc)
    st.caption("All values and connections are simulated examples for demonstrating DSA concepts.")

# ---------------------------------------------------------------------------
# Inventory and Unit 5 indexes
# ---------------------------------------------------------------------------
with tab_inventory:
    st.subheader("Inventory & Product Index")
    st.markdown('<p class="section-caption">SQLite stores the records; B+ Tree and Red-Black Tree demonstrate Unit 5 indexing.</p>', unsafe_allow_html=True)
    search_col, range_col = st.columns(2)
    with search_col:
        with st.form("product_search_form"):
            selected_pid = st.number_input("Search Product ID", min_value=1, value=1001, step=1)
            search_submit = st.form_submit_button("Search indexes", use_container_width=True)
        if search_submit:
            try:
                bplus_product = bplus_index.search(int(selected_pid))
                rb_product = rb_index.search(int(selected_pid))
                st.success("Product found in both B+ Tree and Red-Black Tree.")
                st.json({
                    "Product ID": bplus_product["id"],
                    "Name": bplus_product["name"],
                    "Category": bplus_product["category"],
                    "Unit weight (kg)": bplus_product["unit_weight"],
                    "Unit value (₹)": bplus_product["unit_value"],
                    "Indexes agree": bplus_product == rb_product,
                })
                product_stock = get_stock(int(selected_pid))
                st.dataframe(pd.DataFrame([{
                    "Warehouse": row["warehouse"], "Quantity": row["quantity"],
                    "Available payload (kg)": row["available_weight"]
                } for row in product_stock]), use_container_width=True, hide_index=True)
            except KeyError:
                st.error("No product exists with that ID.")
    with range_col:
        st.markdown("#### B+ Tree range query")
        range_a, range_b = st.columns(2)
        low = range_a.number_input("Minimum ID", min_value=1, value=1001, step=1, key="range_low")
        high = range_b.number_input("Maximum ID", min_value=1, value=1008, step=1, key="range_high")
        if st.button("List products in range", use_container_width=True):
            if low > high:
                st.error("Minimum ID must be <= maximum ID.")
            else:
                result = bplus_index.range_search(int(low), int(high))
                st.dataframe(pd.DataFrame([{
                    "ID": k, "Product": v["name"], "Category": v["category"],
                    "Weight (kg)": v["unit_weight"], "Unit value (₹)": v["unit_value"]
                } for k, v in result]), use_container_width=True, hide_index=True)
    st.divider()
    st.markdown("### Stock by warehouse")
    stock = get_stock()
    st.dataframe(pd.DataFrame([{
        "Warehouse": r["warehouse"], "Product ID": r["product_id"], "Product": r["product"],
        "Category": r["category"], "Quantity": r["quantity"], "Unit Weight (kg)": r["unit_weight"],
        "Units' Payload (kg)": r["available_weight"]
    } for r in stock]), use_container_width=True, hide_index=True)
    with st.expander("Add a product"):
        with st.form("add_product_form", clear_on_submit=True):
            a, b, c = st.columns(3)
            new_pid = a.number_input("New Product ID", min_value=1, value=2001, step=1)
            new_name = b.text_input("Product name")
            new_category = c.text_input("Category", value="General")
            d, e = st.columns(2)
            new_weight = d.number_input("Unit weight (kg)", min_value=1, value=1, step=1)
            new_value = e.number_input("Unit value (₹)", min_value=0.0, value=100.0, step=50.0)
            st.caption("Set opening stock for each warehouse. Zero is allowed.")
            opening_stock = {}
            stock_cols = st.columns(3)
            for col, warehouse in zip(stock_cols, warehouses):
                opening_stock[int(warehouse["id"])] = col.number_input(
                    warehouse["name"], min_value=0, value=0, step=1, key=f'newstock_{warehouse["id"]}'
                )
            add_product_submit = st.form_submit_button("Add product", type="primary")
        if add_product_submit:
            try:
                add_product(int(new_pid), new_name, new_category, int(new_weight), float(new_value),
                            {k: int(v) for k, v in opening_stock.items()})
                st.success("Product added. Indexes will rebuild from the database on rerun.")
                st.rerun()
            except Exception as exc:
                st.error(str(exc))
    with st.expander("Adjust stock"):
        with st.form("adjust_stock_form"):
            stock_product = st.selectbox("Product", products, format_func=lambda p: product_names[p["id"]], key="adjust_pid")
            stock_wh = st.selectbox("Warehouse", warehouses, format_func=lambda w: w["name"], key="adjust_wh")
            delta = st.number_input("Quantity change (+ receive stock, − remove stock)", min_value=-10000, max_value=10000, value=5, step=1)
            adjust_submit = st.form_submit_button("Apply stock adjustment")
        if adjust_submit:
            try:
                new_qty = add_stock(int(stock_wh["id"]), int(stock_product["id"]), int(delta))
                st.success(f'Stock updated. New quantity at {stock_wh["name"]}: {new_qty}')
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

# ---------------------------------------------------------------------------
# Create order
# ---------------------------------------------------------------------------
with tab_orders:
    st.subheader("Create a delivery order")
    st.write("The app checks available stock at each warehouse, computes a Dijkstra route to the destination and selects the nearest eligible warehouse.")
    with st.form("place_order_form", clear_on_submit=True):
        p_col, q_col = st.columns([2, 1])
        selected_product = p_col.selectbox("Product", products, format_func=lambda p: product_names[p["id"]])
        quantity = q_col.number_input("Quantity", min_value=1, max_value=10000, value=1, step=1)
        destination_options = [x for x in locations if x["kind"] in ("customer", "outlet")]
        destination = st.selectbox("Delivery destination", destination_options,
                                   format_func=lambda x: f'{x["name"]} · {x["id"]}')
        priority_label = st.radio("Order priority", ["Urgent", "High", "Normal"], horizontal=True)
        priority = {"Urgent": 1, "High": 2, "Normal": 3}[priority_label]
        st.caption("Stock is reserved transactionally when the order is confirmed. Failed orders do not reduce stock.")
        submit_order = st.form_submit_button("Find warehouse & place order", type="primary", use_container_width=True)
    if submit_order:
        try:
            outcome = place_order(int(selected_product["id"]), int(quantity), destination["id"], priority)
            st.success(f'Order {outcome["id"]} confirmed from {outcome["warehouse"]}.')
            path_names = [location_names.get(node, node) for node in outcome["route"]]
            st.markdown("**Dijkstra route**")
            st.markdown(" ".join([f'<span class="route-pill">{name}</span>' for name in path_names]), unsafe_allow_html=True)
            x, y, z = st.columns(3)
            x.metric("Route distance", f'{outcome["distance"]:.1f} km')
            y.metric("Reserved payload", f'{outcome["payload_weight"]} kg')
            z.metric("Order value", f'₹{outcome["order_value"]:,.0f}')
            st.info("The order is now in the Confirmed dispatch queue. Its reserved stock has been deducted from available inventory.")
        except Exception as exc:
            st.error(str(exc))
    st.divider()
    st.markdown("### Order history")
    all_orders = list_orders()
    if all_orders:
        st.dataframe(pd.DataFrame([{
            "Order ID": o["id"], "Product": o["product_name"], "Qty": o["quantity"],
            "Warehouse": o["warehouse_name"], "Destination": o["destination_name"],
            "Priority": {1:"Urgent", 2:"High", 3:"Normal"}[o["priority"]],
            "Status": o["status"], "Distance (km)": round(o["distance"], 1),
            "Payload (kg)": o["payload_weight"], "Value (₹)": o["order_value"],
            "Created": o["created_at"]
        } for o in all_orders]), use_container_width=True, hide_index=True)
    else:
        st.info("Orders will appear here after successful placement.")

# ---------------------------------------------------------------------------
# Dispatch queue and status flow
# ---------------------------------------------------------------------------
with tab_dispatch:
    st.subheader("Priority-based dispatch queue")
    st.markdown('<p class="section-caption">Unit 1 Binary Heap / Priority Queue: 1 = urgent, 2 = high, 3 = normal. Equal-priority orders preserve arrival order in the queue implementation.</p>', unsafe_allow_html=True)
    warehouse_filter_options = [{"id": 0, "name": "All warehouses"}] + warehouses
    selected_wh_filter = st.selectbox("Filter queue by warehouse", warehouse_filter_options,
                                      format_func=lambda x: x["name"], key="dispatch_wh_filter")
    filter_id = None if selected_wh_filter["id"] == 0 else int(selected_wh_filter["id"])
    queue_orders = dispatch_queue(filter_id)
    if queue_orders:
        queue_table = []
        for idx, order in enumerate(queue_orders, start=1):
            queue_table.append({
                "Queue position": idx, "Order": order["id"], "Priority": {1:"Urgent",2:"High",3:"Normal"}[order["priority"]],
                "Product": order["product_name"], "Qty": order["quantity"],
                "Warehouse": order["warehouse_name"], "Destination": order["destination_name"],
                "Payload (kg)": order["payload_weight"], "Distance (km)": round(order["distance"], 1)
            })
        st.dataframe(pd.DataFrame(queue_table), use_container_width=True, hide_index=True)
        st.markdown("#### Dispatch confirmed orders")
        for order in queue_orders:
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 2, 1])
                c1.markdown(f'**{order["id"]}** · {order["product_name"]} × {order["quantity"]}')
                c2.caption(f'{order["warehouse_name"]} → {order["destination_name"]} · {order["distance"]:.1f} km')
                if c3.button("Dispatch", key=f'dispatch_{order["id"]}', type="primary"):
                    try:
                        transition_order(order["id"], "Dispatched")
                        st.success(f'{order["id"]} dispatched.')
                        st.rerun()
                    except Exception as exc:
                        st.error(str(exc))
    else:
        st.info("No confirmed orders are waiting for dispatch.")
    st.divider()
    st.markdown("### Dispatched shipments")
    dispatched = list_orders(status="Dispatched")
    if dispatched:
        for order in dispatched:
            c1, c2, c3 = st.columns([3, 2, 1])
            c1.write(f'**{order["id"]}** · {order["product_name"]} → {order["destination_name"]}')
            c2.caption(f'{order["distance"]:.1f} km · {order["payload_weight"]} kg')
            if c3.button("Mark delivered", key=f'deliver_{order["id"]}'):
                try:
                    transition_order(order["id"], "Delivered")
                    st.success(f'{order["id"]} marked delivered.')
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
    else:
        st.caption("No shipments currently marked Dispatched.")
    with st.expander("Cancel a confirmed order"):
        confirmed = list_orders(status="Confirmed")
        if confirmed:
            cancellation = st.selectbox("Confirmed order", confirmed,
                                        format_func=lambda o: f'{o["id"]} · {o["product_name"]}',
                                        key="cancel_order_pick")
            if st.button("Cancel and return reserved stock", key="cancel_order_button"):
                try:
                    transition_order(cancellation["id"], "Cancelled")
                    st.success("Order cancelled and stock returned.")
                    st.rerun()
                except Exception as exc:
                    st.error(str(exc))
        else:
            st.caption("There are no confirmed orders available to cancel.")

# ---------------------------------------------------------------------------
# Route explorer and Unit 4 TSP
# ---------------------------------------------------------------------------
with tab_routes:
    st.subheader("Delivery Network & Route Planner")
    st.caption("Weighted edges represent simulated road distances in kilometres.")
    with st.expander("Inspect route connections"):
        st.dataframe(pd.DataFrame(list_routes()), use_container_width=True, hide_index=True)
    graph = build_graph()
    c1, c2 = st.columns(2)
    with c1:
        with st.form("single_route_form"):
            start_location = st.selectbox("Starting location", locations,
                                          index=next((i for i,x in enumerate(locations) if x["kind"]=="warehouse"),0),
                                          format_func=lambda x: f'{x["name"]} ({x["id"]})')
            destination_location = st.selectbox("Destination", locations,
                                                 index=next((i for i,x in enumerate(locations) if x["kind"]=="customer"),0),
                                                 format_func=lambda x: f'{x["name"]} ({x["id"]})',
                                                 key="single_dest")
            route_submit = st.form_submit_button("Calculate shortest route", type="primary", use_container_width=True)
        if route_submit:
            try:
                path, distance = dijkstra_shortest_path(graph, start_location["id"], destination_location["id"])
                if not path:
                    st.error("The destination is unreachable from this start.")
                else:
                    st.success(f"Shortest route: {distance:.1f} km")
                    st.markdown(" → ".join(location_names.get(p,p) for p in path))
                    st.caption(f"{len(path)-1} road segments · Dijkstra · non-negative weights")
            except Exception as exc:
                st.error(str(exc))
    with c2:
        st.markdown("#### Multi-stop tour (Unit 4 · TSP)")
        st.caption("Branch & Bound finds the lowest-distance closed tour for a small set of chosen stops. The tour returns to its start.")
        start_wh = st.selectbox("Tour start", warehouses,
                                format_func=lambda x: f'{x["name"]} ({x["location_id"]})', key="tsp_start")
        potential_stops = [x for x in locations if x["id"] != start_wh["location_id"]]
        tour_stops = st.multiselect("Delivery stops (select 1–6)", potential_stops,
                                    format_func=lambda x: f'{x["name"]} ({x["id"]})', key="tsp_stops")
        if st.button("Optimize multi-stop tour", type="primary", use_container_width=True):
            try:
                route, distance = optimize_multi_stop_tour(start_wh["location_id"], [x["id"] for x in tour_stops])
                st.success(f"Best closed tour: {distance:.1f} km")
                st.markdown(" → ".join(location_names.get(p,p) for p in route))
                st.caption("TSP uses shortest-path distances between selected stops. It is exponential, so the app limits the number of stops.")
            except Exception as exc:
                st.error(str(exc))
    st.divider()
    st.markdown("#### Reachability")
    with st.expander("Check if one location can reach another"):
        reach_a = st.selectbox("From", locations, format_func=lambda x: x["name"], key="reach_a")
        reach_b = st.selectbox("To", locations, format_func=lambda x: x["name"], key="reach_b")
        if st.button("Check reachability"):
            path, distance = dijkstra_shortest_path(graph, reach_a["id"], reach_b["id"])
            if path:
                st.success(f"Reachable: {distance:.1f} km via {' → '.join(location_names.get(p,p) for p in path)}")
            else:
                st.warning("No route connects these locations.")

# ---------------------------------------------------------------------------
# Vehicle capacity / Knapsack
# ---------------------------------------------------------------------------
with tab_capacity:
    st.subheader("Vehicle Capacity Planner")
    st.write("The 0/1 Knapsack algorithm selects the highest-value combination of confirmed orders for a single warehouse and vehicle capacity.")
    planner_wh = st.selectbox("Dispatching warehouse", warehouses,
                              format_func=lambda x: x["name"], key="capacity_wh")
    capacity = st.number_input("Vehicle capacity (kg)", min_value=1, max_value=10000, value=25, step=1)
    plan = knapsack_plan(int(planner_wh["id"]), int(capacity))
    if not plan["all_candidates"]:
        st.info("There are no confirmed orders assigned to this warehouse. Create orders first.")
    else:
        a, b, c = st.columns(3)
        a.metric("Eligible orders", len(plan["all_candidates"]))
        b.metric("Selected payload", f'{plan["total_weight"]} / {capacity} kg')
        c.metric("Selected order value", f'₹{plan["value"]:,.0f}')
        selected_ids = {o["id"] for o in plan["selected"]}
        show_rows = []
        for order in plan["all_candidates"]:
            show_rows.append({
                "Selected": "✓" if order["id"] in selected_ids else "—",
                "Order": order["id"], "Product": order["product_name"], "Quantity": order["quantity"],
                "Weight (kg)": order["payload_weight"], "Value (₹)": order["order_value"],
                "Priority": {1:"Urgent",2:"High",3:"Normal"}[order["priority"]]
            })
        st.dataframe(pd.DataFrame(show_rows), use_container_width=True, hide_index=True)
        if plan["selected"]:
            if st.button("Dispatch selected orders", type="primary", use_container_width=True):
                try:
                    for order in plan["selected"]:
                        transition_order(order["id"], "Dispatched")
                    st.success(f'{len(plan["selected"])} selected orders dispatched. Other orders remain Confirmed.')
                    st.rerun()
                except Exception as exc:
                    st.error(f"Some orders may already have changed status; refresh and recheck. Details: {exc}")
        else:
            st.warning("No order fits the selected vehicle capacity.")
    st.caption("For a small integer-capacity demonstrator, the 0/1 Knapsack DP runs in O(n × capacity) time and space.")

# ---------------------------------------------------------------------------
# Unit 4/5 demonstrations - keep non-core algorithms explainable, not forced.
# ---------------------------------------------------------------------------
with tab_lab:
    st.subheader("DSA-II Concept Lab")
    st.write("Standalone demonstrations for relevant and syllabus-focused algorithms. These are educational examples; only explicitly labelled application features affect inventory/orders.")
    lab4, lab5 = st.tabs(["Unit 4 · Backtracking & Branch & Bound", "Unit 5 · Advanced Structures"])
    with lab4:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Graph Colouring")
            st.caption("Use colours as dispatch slots for zones with explicit conflict constraints.")
            if st.button("Run sample slot colouring", key="lab_colour"):
                conflict_graph = {
                    "North Zone": ["Central Zone"],
                    "Central Zone": ["North Zone", "South Zone"],
                    "South Zone": ["Central Zone"],
                    "Remote Zone": [],
                }
                result = color_graph(conflict_graph, ["Morning", "Afternoon"])
                st.json(result if result is not None else {"result": "No feasible colouring"})
            st.markdown("#### Sum of Subsets")
            st.caption("Find exact-weight package combinations. Knapsack remains the best-value capacity feature.")
            subset_weights = st.text_input("Parcel weights (comma-separated kg)", "2,3,5,7,8", key="subset_weights")
            subset_target = st.number_input("Exact target weight (kg)", min_value=0, value=10, step=1, key="subset_target")
            if st.button("Find exact-weight subsets", key="lab_subset"):
                try:
                    weights = [int(x.strip()) for x in subset_weights.split(",") if x.strip()]
                    st.json(sum_of_subsets(weights, int(subset_target)))
                except Exception as exc:
                    st.error(str(exc))
        with col2:
            st.markdown("#### Hamiltonian Cycle")
            st.caption("Checks whether a closed cycle can visit every listed vertex once. It does not minimize distance.")
            if st.button("Find sample Hamiltonian cycle", key="lab_hamiltonian"):
                adjacency = {"Warehouse":["A","C"],"A":["Warehouse","B"],"B":["A","C"],"C":["B","Warehouse"]}
                st.write(find_hamiltonian_cycle(adjacency, "Warehouse"))
            st.markdown("#### N-Queens")
            st.caption("A Unit 4 backtracking demonstration, not a warehouse feature.")
            n = st.number_input("Board size n", min_value=1, max_value=10, value=4, step=1)
            if st.button("Solve N-Queens", key="lab_queens"):
                solutions = solve_n_queens(int(n))
                st.write(f"Solutions: {len(solutions)}")
                if solutions:
                    st.write("First solution (column index per row):", solutions[0])
            st.markdown("#### TSP with Branch & Bound")
            st.caption("The operational multi-stop route planner uses this algorithm in the Route Planner tab.")
            st.info("Select 1–6 stops in Route Planner to optimize a closed tour.")

    with lab5:
        st.markdown("#### Inventory indexes")
        st.caption("The product search and range-query feature above uses a Red-Black Tree and B+ Tree. The B-Tree is demonstrated here for comparison.")
        a, b = st.columns(2)
        with a:
            lookup_id = st.number_input("B-Tree product lookup ID", min_value=1, value=1004, step=1)
            if st.button("Search B-Tree", key="lab_btree"):
                try:
                    item = btree_index.search(int(lookup_id))
                    st.json({"id": item["id"], "name": item["name"], "category": item["category"]})
                except KeyError:
                    st.error("Product not found in B-Tree index.")
        with b:
            if st.button("Compare index sizes", key="lab_index_sizes"):
                st.json({"products indexed": len(products), "Red-Black Tree": rb_index.size,
                         "B+ Tree leaves/range queries": len(list(bplus_index.items())),
                         "B-Tree": btree_index.size})
        st.divider()
        st.markdown("#### Binomial Heap and Fibonacci Heap")
        st.caption("Advanced Unit 5 priority-queue demonstrations. The actual dispatch queue uses the existing stable binary-heap PriorityQueue.")
        if st.button("Run heap extraction demo", key="lab_heaps"):
            entries = [(3, "ORD-C"), (1, "ORD-A"), (2, "ORD-B"), (1, "ORD-D")]
            binomial = BinomialHeap[tuple[int, str]]()
            fibonacci = FibonacciHeap[tuple[int, str]]()
            for entry in entries:
                binomial.insert(entry)
                fibonacci.insert(entry)
            st.json({
                "Binomial Heap extraction order": [binomial.extract_min() for _ in range(len(binomial))],
                "Fibonacci Heap extraction order": [fibonacci.extract_min() for _ in range(len(fibonacci))],
            })
        st.info("Red-Black Tree: balanced lookup index. B-Tree: multi-key search tree. B+ Tree: records in linked leaves and efficient ordered range scan. Binomial/Fibonacci heaps: advanced min-priority queues.")

st.divider()
st.caption("WarehouseFlow · DSA-II CCSE0301 · Academic prototype using simulated records. No live GPS, traffic feeds, or external logistics services are connected.")
