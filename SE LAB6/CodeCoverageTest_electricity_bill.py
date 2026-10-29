import pytest
from electricity_bill import energy_charge, late_fee, subsidy


# ---------- energy_charge ----------
def test_low_usage_domestic():
    assert energy_charge(50, "domestic") == 200            # 50*3 + 50


def test_mid_usage_domestic():
    assert energy_charge(200, "domestic") == 850           # 300 + 100*5 + 50


def test_high_usage_commercial():
    assert energy_charge(400, "commercial") == 4350        # (1300+100*8)*2 + 150


def test_unknown_connection():
    with pytest.raises(ValueError):
        energy_charge(100, "industrial")


def test_negative_units():
    with pytest.raises(ValueError):
        energy_charge(-5, "domestic")


# ---------- late_fee ----------
def test_paid_on_time():
    assert late_fee(500, 0) == 0


def test_late_within_15_days():
    assert late_fee(500, 10) == 50


def test_late_over_15_days_big_bill():
    assert late_fee(3000, 20) == 250                       # 100 + 3000//20


# ---------- subsidy ----------
def test_senior_and_solar_low_usage():
    assert subsidy(50, True, True) == 150


def test_solar_high_usage_cancels_subsidy():
    assert subsidy(400, False, True) == 0
