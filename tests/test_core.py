import unittest

from src.corporate_finance.core import FinancialSnapshot, analyze_dict


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.data = {
            "company": "Test Co",
            "period": "FY2026",
            "previous_revenue": 100,
            "revenue": 120,
            "ebitda": 24,
            "ebit": 18,
            "net_income": 12,
            "total_assets": 200,
            "equity": 80,
            "current_assets": 90,
            "current_liabilities": 60,
            "inventory": 20,
            "cash": 30,
            "total_debt": 100,
            "operating_cash_flow": 25,
            "capex": 10,
            "interest_expense": 6,
        }

    def test_key_metrics(self):
        result = analyze_dict(self.data)
        metrics = result["metrics"]
        self.assertAlmostEqual(metrics["revenue_growth"], 0.2)
        self.assertAlmostEqual(metrics["ebitda_margin"], 0.2)
        self.assertAlmostEqual(metrics["current_ratio"], 1.5)
        self.assertAlmostEqual(metrics["free_cash_flow"], 15.0)
        self.assertAlmostEqual(metrics["interest_coverage"], 3.0)

    def test_risk_flags(self):
        data = dict(self.data)
        data.update({"current_liabilities": 120, "interest_expense": 12, "cash": 5, "capex": 50})
        result = analyze_dict(data)
        codes = {flag["code"] for flag in result["risk_flags"]}
        self.assertIn("LIQUIDITY", codes)
        self.assertIn("INTEREST_BURDEN", codes)
        self.assertIn("CASH_GENERATION", codes)

    def test_missing_required_field(self):
        data = dict(self.data)
        del data["revenue"]
        with self.assertRaises(ValueError):
            FinancialSnapshot.from_dict(data)

    def test_zero_denominator_is_null(self):
        data = dict(self.data)
        data["equity"] = 0
        result = analyze_dict(data)
        self.assertIsNone(result["metrics"]["roe"])


if __name__ == "__main__":
    unittest.main()
