"""Integration tests for order, inventory, routing and capacity workflow."""
from __future__ import annotations
import tempfile
import unittest
from pathlib import Path

from warehouse_app import database as services


class ServiceWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.original_path = services.DB_PATH
        services.DB_PATH = Path(self.temp.name) / "workflow.sqlite3"
        services.init_db()

    def tearDown(self):
        services.DB_PATH = self.original_path
        self.temp.cleanup()

    def total_stock(self, product_id: int) -> int:
        return sum(row["quantity"] for row in services.get_stock(product_id))

    def test_order_routes_reserves_then_cancel_restores_stock(self):
        before = self.total_stock(1001)
        result = services.place_order(1001, 2, "HUB_ALPHA", 2)
        self.assertTrue(result["route"])
        self.assertEqual(result["route"][0], {"North Warehouse": "WH_NORTH",
                                             "Central Warehouse": "WH_CENTRAL",
                                             "South Warehouse": "WH_SOUTH"}[result["warehouse"]])
        self.assertEqual(result["route"][-1], "HUB_ALPHA")
        self.assertLess(result["distance"], float("inf"))
        self.assertEqual(self.total_stock(1001), before - 2)
        services.transition_order(result["id"], "Cancelled")
        self.assertEqual(self.total_stock(1001), before)
        self.assertEqual(services.list_orders(status="Cancelled")[0]["id"], result["id"])

    def test_dispatch_queue_prioritizes_lower_number(self):
        services.place_order(1001, 1, "HUB_ALPHA", 3)
        services.place_order(1004, 1, "HUB_ALPHA", 1)
        queue = services.dispatch_queue()
        self.assertGreaterEqual(len(queue), 2)
        priorities = [row["priority"] for row in queue]
        self.assertEqual(priorities, sorted(priorities))

    def test_knapsack_respects_capacity(self):
        first = services.place_order(1001, 1, "HUB_ALPHA", 1)
        services.place_order(1004, 1, "HUB_ALPHA", 2)
        orders = services.list_orders(status="Confirmed")
        warehouse_id = next(o["assigned_warehouse_id"] for o in orders if o["id"] == first["id"])
        plan = services.knapsack_plan(warehouse_id, capacity=2)
        self.assertLessEqual(plan["total_weight"], 2)
        self.assertTrue(plan["selected"])

    def test_multi_stop_tour_returns_to_start(self):
        route, distance = services.optimize_multi_stop_tour("WH_CENTRAL", ["HUB_ALPHA", "OUTLET_2"])
        self.assertEqual(route[0], "WH_CENTRAL")
        self.assertEqual(route[-1], "WH_CENTRAL")
        self.assertEqual(set(route[:-1]), {"WH_CENTRAL", "HUB_ALPHA", "OUTLET_2"})
        self.assertGreater(distance, 0)


if __name__ == "__main__":
    unittest.main()
