import unittest
from src.corporate_finance.advanced import dupont_analysis, capital_intensity, working_capital_metrics, stress_test, peer_percentile, investment_screen


class TestAdvancedAnalytics(unittest.TestCase):
    def setUp(self):
        self.data = {
            'company': 'TestCo', 'period': 'FY2026', 'revenue': 1000, 'previous_revenue': 900,
            'ebitda': 250, 'ebit': 200, 'net_income': 120, 'total_assets': 2000, 'equity': 1000,
            'current_assets': 600, 'current_liabilities': 400, 'inventory': 100, 'cash': 150,
            'total_debt': 500, 'operating_cash_flow': 220, 'capex': 80, 'interest_expense': 25,
        }

    def test_dupont(self):
        result = dupont_analysis(0.12, 0.5, 2.0)
        self.assertAlmostEqual(result['roe'], 12.0)

    def test_capital_intensity(self):
        result = capital_intensity(1000, 2000, 80)
        self.assertEqual(result['asset_intensity'], 2.0)
        self.assertEqual(result['capex_to_revenue'], 0.08)

    def test_working_capital(self):
        result = working_capital_metrics(600, 400, 100, 150, 1000)
        self.assertEqual(result['net_working_capital'], 200)
        self.assertEqual(result['working_capital_ratio'], 1.5)

    def test_stress_grid(self):
        result = stress_test(self.data, [-0.1, 0], [-0.02, 0])
        self.assertEqual(len(result), 4)
        self.assertLess(result[0]['revenue'], self.data['revenue'])

    def test_peer_percentile(self):
        self.assertEqual(peer_percentile([1, 2, 3, 4], 3), 75.0)

    def test_investment_screen(self):
        result = investment_screen({'revenue_growth': 0.2, 'ebitda_margin': 0.3, 'fcf_margin': 0.15, 'net_debt_to_ebitda': 1.0, 'current_ratio': 2.0, 'interest_coverage': 10.0, 'free_cash_flow': 100})
        self.assertEqual(result['label'], 'Strong fundamentals')


if __name__ == '__main__':
    unittest.main()
