"""Unit tests for live provider parsers."""

from datetime import date
from decimal import Decimal

from src.collectors.almeezan.parser import (
    parse_alias_config as parse_almeezan_aliases,
)
from src.collectors.almeezan.parser import (
    parse_almeezan_fund_prices_html,
)
from src.collectors.almeezan.parser import (
    resolve_fund_symbol as resolve_almeezan_symbol,
)
from src.collectors.mufap.parser import (
    parse_alias_config,
    parse_mufap_nav_html,
    resolve_fund_symbol,
)
from src.collectors.psx.parser import parse_psx_eod_series
from src.collectors.sbp.parser import parse_sbp_homepage, parse_world_bank_inflation

MUFAP_HTML = """
<html><body>
<table>
<tr>
  <th>Sector</th><th>AMC</th><th>Fund</th><th>Category</th>
  <th>NAV</th><th>Validity Date</th>
</tr>
<tr>
  <td>Open-End Funds</td>
  <td>Al Meezan Investment Management Limited</td>
  <td>Meezan Islamic Fund</td>
  <td>Shariah Compliant Equity</td>
  <td>92.15</td>
  <td>Aug 12, 2026</td>
</tr>
<tr>
  <td>Open-End Funds</td>
  <td>ABL Asset Management</td>
  <td>ABL Cash Fund</td>
  <td>Money Market</td>
  <td>11.20</td>
  <td>Aug 12, 2026</td>
</tr>
</table>
</body></html>
"""

ALMEEZAN_HTML = """
<html><body>
<table class="table">
<thead>
<tr>
  <th>Funds Category</th><th>Launch Date</th><th>Validity Date</th>
  <th>Repurchase (Rs.)</th><th>Offer (Rs.)</th><th>NAV (Rs.)</th>
  <th>M. Fee (%)</th><th>Trustee Fee (%)</th><th>Regulatory. Fee (%)</th>
  <th>Levies and Taxes</th><th>Transaction Expenses</th>
  <th>Third Party Expenses</th><th>Other Expenses</th>
  <th>TER with Levies</th><th>TER without Levies</th>
  <th>MTD Return</th><th>FYTD Return</th><th>CYTD Return</th>
  <th>FY25 (%) Return</th><th>FY24 (%) Return</th><th>Since Inception Return</th>
</tr>
</thead>
<tbody>
<tr>
  <td colspan="6" class="table-head">Equity Funds</td>
  <td colspan="16" class="table-head"></td>
</tr>
<tr>
  <td>Meezan Islamic Fund</td><td>8 Aug 2003</td><td>14 Sep 2026</td>
  <td>156.0864</td><td>159.6763</td><td>0.0000</td>
  <td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td>
  <td>-5.30</td><td>-8.50</td><td>-7.10</td><td>30</td><td>40</td><td>100</td>
</tr>
<tr>
  <td colspan="6" class="table-head">Money Market Funds</td>
  <td colspan="16" class="table-head"></td>
</tr>
<tr>
  <td>Meezan Cash Fund</td><td>15 Jun 2009</td><td>14 Sep 2026</td>
  <td>0.0000</td><td>0.0000</td><td>52.6734</td>
  <td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td>
  <td>9.81</td><td>9.95</td><td>9.50</td><td>20</td><td>18</td><td>200</td>
</tr>
</tbody>
</table>
</body></html>
"""

SBP_HTML = """
<html><body>
<h4>SBP Policy Rate &amp; Interest Rate Corridor Facilities</h4>
<p>SBP Policy Rate 11.50% p.a.</p>
<h4>USD/ PKR Rates</h4>
<p>As on 13-Aug - 2026</p>
<p>M2M Revaluation Rate</p>
<h4>277.6522</h4>
</body></html>
"""


def test_parse_mufap_nav_html_and_aliases() -> None:
    rows = parse_mufap_nav_html(MUFAP_HTML)
    assert len(rows) == 2
    assert rows[0]["name"] == "Meezan Islamic Fund"
    assert rows[0]["nav"] == "92.15"
    assert rows[0]["is_shariah"] is True
    aliases = parse_alias_config({"MIF": ["Meezan Islamic Fund"]})
    assert resolve_fund_symbol(rows[0]["name"], aliases, {}) == "MIF"
    assert resolve_fund_symbol(rows[1]["name"], aliases, {}) is None


def test_parse_almeezan_fund_prices_html() -> None:
    rows = parse_almeezan_fund_prices_html(ALMEEZAN_HTML)
    assert len(rows) == 2
    equity = rows[0]
    assert equity["name"] == "Meezan Islamic Fund"
    assert equity["offer"] == "159.6763"
    assert equity["repurchase"] == "156.0864"
    assert equity["date"] == "2026-09-14"
    assert equity["fytd_return"] == "-8.50"
    assert Decimal(equity["nav"]) > 0
    cash = rows[1]
    assert cash["name"] == "Meezan Cash Fund"
    assert cash["nav"] == "52.6734"
    aliases = parse_almeezan_aliases(
        {"MIF": ["Meezan Islamic Fund"], "MCF": ["Meezan Cash Fund"]}
    )
    assert resolve_almeezan_symbol(equity["name"], aliases, {}) == "MIF"
    assert resolve_almeezan_symbol(cash["name"], aliases, {}) == "MCF"


def test_parse_psx_eod_series() -> None:
    payload = {
        "status": 1,
        "data": [
            [1786492800, 385.5, 1000, 380.0],
            [1000000000, 10.0, 1, 10.0],
        ],
    }
    rows = parse_psx_eod_series("ENGRO", payload, history_days=365)
    assert len(rows) == 1
    assert rows[0]["symbol"] == "ENGRO"
    assert rows[0]["close"] == 385.5


def test_parse_sbp_homepage_and_world_bank() -> None:
    rows = parse_sbp_homepage(SBP_HTML, today=date(2026, 8, 13))
    names = {row["indicator_name"]: row["value"] for row in rows}
    assert names["policy rate"] == "11.50"
    assert names["usd pkr"] == "277.6522"
    inflation = parse_world_bank_inflation(
        [
            {},
            [
                {"date": "2024", "value": 12.6},
                {"date": "2023", "value": None},
            ],
        ]
    )
    assert inflation[0]["indicator_name"] == "inflation cpi"
    assert inflation[0]["value"] == 12.6
