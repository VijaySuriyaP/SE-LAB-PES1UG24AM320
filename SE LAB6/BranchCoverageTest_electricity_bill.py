import pytest
from electricity_bill import energy_charge, late_fee, subsidy


# ---------- energy_charge ----------
def test_low_usage_domestic():
    assert energy_charge(50, "domestic") == 200            # 50*3 + 50


def test_mid_usage_domestic():
    assert energy_charge(200, "domestic") == 850           # 300 + 100*5 + 50


def test_high_usage_domestic():
    assert energy_charge(400, "domestic") == 1300 + 100 * 8 + 50   # 2150 -> no doubling


def test_high_usage_commercial():
    assert energy_charge(400, "commercial") == 4350        # (1300+100*8)*2 + 150


def test_low_usage_commercial():
    assert energy_charge(50, "commercial") == 450          # 50*3*2 + 150


def test_unknown_connection():
    with pytest.raises(ValueError, match="unknown connection"):
        energy_charge(100, "industrial")


def test_negative_units():
    with pytest.raises(ValueError, match="invalid units"):
        energy_charge(-5, "domestic")


def test_slab_boundaries():
    assert energy_charge(0, "domestic") == 50              # zero units
    assert energy_charge(100, "domestic") == 350           # top of slab 1
    assert energy_charge(101, "domestic") == 355           # first unit of slab 2
    assert energy_charge(300, "domestic") == 1350          # top of slab 2
    assert energy_charge(301, "domestic") == 1358          # first unit of slab 3


# ---------- late_fee ----------
def test_paid_on_time():
    assert late_fee(500, 0) == 0


def test_negative_days_late():
    assert late_fee(500, -3) == 0


def test_late_within_15_days():
    assert late_fee(500, 10) == 50


def test_late_exactly_15_days():
    assert late_fee(500, 15) == 50                         # boundary


def test_late_over_15_days_small_bill():
    assert late_fee(1000, 20) == 100                       # bill <= 2000 -> no surcharge


def test_late_over_15_days_bill_exactly_2000():
    assert late_fee(2000, 16) == 100                       # boundary of bill > 2000


def test_late_over_15_days_big_bill():
    assert late_fee(3000, 20) == 250                       # 100 + 3000//20


# ---------- subsidy ----------
def test_senior_low_usage_no_solar():
    assert subsidy(50, True, False) == 50


def test_senior_but_high_usage():
    assert subsidy(150, True, False) == 0                  # units > 100 -> no senior subsidy


def test_not_senior_low_usage():
    assert subsidy(50, False, False) == 0


def test_senior_boundary_100_units():
    assert subsidy(100, True, False) == 50


def test_senior_and_solar_low_usage():
    assert subsidy(50, True, True) == 150


def test_solar_mid_usage():
    assert subsidy(200, False, True) == 100                # solar, units <= 300


def test_solar_boundary_300_units():
    assert subsidy(300, False, True) == 100


def test_solar_high_usage_cancels_subsidy():
    assert subsidy(400, False, True) == 0
