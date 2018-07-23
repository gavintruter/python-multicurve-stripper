import pytest
from datetime import date
from daycountconvention import actual_360, thirty_360
from instruments import LiborDeposit, EurodollarFuture, InterestRateSwap, OisBasisSwap
from interestratecurve import InterestRateCurve

# Define curves for use in all the tests
@pytest.fixture
def test_curves():
    base_date = date(2018, 7, 13)
    libor_dates = [date(2018, 10, 15), date(2019, 1, 15), date(2019, 7, 15)]
    libor_dfs = [0.9950, 0.9880, 0.9750]
    libor_curve = InterestRateCurve(base_date, libor_dates, libor_dfs)
    ois_dates = [date(2018, 7, 15)] + libor_dates
    ois_dfs = [0.9999, 0.9945, 0.9900, 0.9800]
    ois_curve = InterestRateCurve(base_date, ois_dates, ois_dfs)
    return libor_curve, ois_curve


@pytest.mark.xfail
class TestLiborDeposit:

    def test_basic(self):
        notional = 1e6
        start_date = date(2018, 7, 9)
        tenor_in_months = 3
        rate = 0.05
        libor_deposit = LiborDeposit(notional, start_date, tenor_in_months, rate)
        end_date = date(2018, 10, 9)
        known_df = 1.0 / (1.0 + rate * actual_360.yf(start_date, end_date))
        libor_curve = InterestRateCurve(start_date, [end_date], [known_df])
        ois_curve = InterestRateCurve(start_date, [end_date], [1.0])
        assert(abs(libor_deposit.value(libor_curve, ois_curve)) < 1e-6)



@pytest.mark.xfail
class TestEurodollarFutures:

    def test_basic(self):
        year = 2019
        month = 6
        edf = EurodollarFuture(year, month)

        base_date = date(2018, 7, 13)
        start_date = date(2019, 6, 19)
        end_date = date(2019, 9, 19)
        start_df = 0.90
        rate = 0.0150
        end_df = start_df / (1.0 + rate * 92.0 / 360.0)
        libor_curve = InterestRateCurve(base_date, [start_date, end_date],
                                        [start_df, end_df])
        assert(abs(edf.price(libor_curve) - 98.5) < 1e-9)


@pytest.mark.xfail
class TestInterestRateSwap:

    def test_floating_leg_same_curve(self, test_curves):
        notional = 1e6
        start_date = date(2018, 10, 1)
        tenor_in_months = 60
        fixed_rate = 0.0;
        swap = InterestRateSwap(notional, start_date, tenor_in_months, fixed_rate)
        end_date = swap.fixed_flows[-1].end_date

        libor_curve, ois_curve = test_curves

        actual_value = swap.value(libor_curve, libor_curve)
        expected_value = notional * (libor_curve.df(start_date) - libor_curve.df(end_date))
        assert(abs(actual_value - expected_value) < 1e-9)

        actual_value = swap.value(ois_curve, ois_curve)
        expected_value = notional * (ois_curve.df(start_date) - ois_curve.df(end_date))
        assert(abs(actual_value - expected_value) < 1e-9)

    def test_fixed_leg(self, test_curves):
        notional = 1e6
        start_date = date(2018, 7, 31)
        tenor_in_months = 12
        fixed_rate = 0.05
        swap = InterestRateSwap(-notional, start_date, tenor_in_months, fixed_rate)  # Receive fixed
        libor_curve, ois_curve = test_curves
        zero_curve = InterestRateCurve(date(2018, 7, 13), [date(2019, 7, 13)], [1.0])

        # Note that no date adjustment, so the year-fractions are 0.5.

        actual_value = swap.value(zero_curve, libor_curve)
        expected_value = notional * fixed_rate * 0.5 * (libor_curve.df(date(2019, 1, 31))
                                                        + libor_curve.df(date(2019, 7, 31)))
        assert(abs(actual_value - expected_value) < 1e-9)

        actual_value = swap.value(zero_curve, ois_curve)
        expected_value = notional * fixed_rate * 0.5 * (ois_curve.df(date(2019, 1, 31))
                                                        + ois_curve.df(date(2019, 7, 31)))
        assert(abs(actual_value - expected_value) < 1e-9)

    def test_basic(self, test_curves):
        notional = 1e6
        start_date = date(2018, 7, 13)
        tenor_in_months = 6
        fixed_rate = 0.02
        swap = InterestRateSwap(notional, start_date, tenor_in_months, fixed_rate)

        libor_curve, ois_curve = test_curves

        d1 = date(2018, 10, 15)
        d2 = date(2019, 1, 14)
        fixed_leg_value = (notional * fixed_rate * thirty_360.yf(start_date, d2)
                           * ois_curve.df(d2))
        forward1 = libor_curve.forward(start_date, d1, actual_360)
        yf1 = actual_360.yf(start_date, d1)
        forward2 = libor_curve.forward(d1, d2, actual_360)
        yf2 = actual_360.yf(d1, d2)
        libor_leg_value = notional * (forward1 * yf1 * ois_curve.df(d1)
                                      + forward2 * yf2 * ois_curve.df(d2))
        swap_value = libor_leg_value - fixed_leg_value
        assert(abs(swap.value(libor_curve, ois_curve) - swap_value) < 1e-9)

        # Multiply notional by -10, double fixed rate.
        swap2 = InterestRateSwap(-10.0 * notional, start_date, tenor_in_months, 2.0 * fixed_rate)
        swap_value2 = -10.0 * (swap_value - fixed_leg_value)
        assert(abs(swap2.value(libor_curve, ois_curve) - swap_value2) < 1e-9)
        

@pytest.mark.xfail
class TestOisBasisSwap:

    def test_zero_value_for_same_curve(self, test_curves):
        notional = 1e7
        start_date = date(2018, 7, 31)
        tenor = 36
        ois_leg_spread = 0.0
        swap = OisBasisSwap(notional, start_date, tenor, ois_leg_spread)

        libor_curve, ois_curve = test_curves

        assert(abs(swap.value(libor_curve, libor_curve)) < 1e-9)
        assert(abs(swap.value(ois_curve, ois_curve)) < 1e-9)

    def test_single_period(self, test_curves):
        notional = 1e8
        start_date = date(2018, 7, 16)
        tenor = 3
        ois_leg_spread = 0.0020
        swap = OisBasisSwap(notional, start_date, tenor, ois_leg_spread)

        libor_curve, ois_curve = test_curves

        end_date = date(2018, 10, 16)
        libor_forward = libor_curve.forward(start_date, end_date, actual_360)
        ois_forward = ois_curve.forward(start_date, end_date, actual_360)
        yf = actual_360.yf(start_date, end_date)
        expected_value = (notional * (libor_forward - ois_forward - ois_leg_spread)
                          * yf * ois_curve.df(end_date))

        actual_value = swap.value(libor_curve, ois_curve)
        assert(abs(actual_value - expected_value) < 1e-9)
