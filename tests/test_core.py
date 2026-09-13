import unittest

from src.corporate_finance.core import FinancialSnapshot, analyze_dict, scenario_analysis


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.data = {
            "company": "Test Co", "period": "FY2026", "previous_revenue": 100,
            "revenue": 120, "ebitda": 24, "ebit": 18, "net_income": 12,
            "total_assets": 200, "equity": 80, "current_assets": 90,
            "current_liabilities": 60, "inventory": 20, "cash": 30,
            "total_debt": 100, "operating_cash_flow": 25, "capex": 10,
            "interest_expense": 6,
        }

    def test_key_metrics(self):
        result = analyze_dict(self.data); metrics = result["metrics"]
        self.assertAlmostEqual(metrics["revenue_growth"], 0.2)
        self.assertAlmostEqual(metrics["ebitda_margin"], 0.2)
        self.assertAlmostEqual(metrics["current_ratio"], 1.5)
        self.assertAlmostEqual(metrics["free_cash_flow"], 15.0)
        self.assertAlmostEqual(metrics["interest_coverage"], 3.0)
        self.assertIn(result["health_grade"], {"A", "B", "C", "D", "E"})

    def test_risk_flags(self):
        data = dict(self.data)
        data.update({"current_liabilities": 120, "interest_expense": 12, "cash": 5, "capex": 50})
        codes = {f["code"] for f in analyze_dict(data)["risk_flags"]}
        self.assertIn("LIQUIDITY", codes); self.assertIn("INTEREST_BURDEN", codes); self.assertIn("CASH_GENERATION", codes)

    def test_negative_equity_is_supported(self):
        data = dict(self.data); data["equity"] = -5
        result = analyze_dict(data)
        self.assertIsNone(result["metrics"]["roe"])
        self.assertIn("NEGATIVE_EQUITY", {f["code"] for f in result["risk_flags"]})

    def test_scenario_analysis_changes_metrics(self):
        result = scenario_analysis(self.data, revenue_change=-0.10, margin_change=-0.02, interest_change=0.25)
        self.assertLess(result["metrics"]["revenue_growth"], self.data["revenue"] / self.data["previous_revenue"] - 1)
        self.assertEqual(result["scenario"]["revenue_change"], -0.10)

    def test_missing_required_field(self):
        data = dict(self.data); del data["revenue"]
        with self.assertRaises(ValueError): FinancialSnapshot.from_dict(data)

    def test_zero_denominator_is_null(self):
        data = dict(self.data); data["equity"] = 0
        self.assertIsNone(analyze_dict(data)["metrics"]["roe"])


if __name__ == "__main__":
    unittest.main()
