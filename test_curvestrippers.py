import pytest
from pytest import approx
from curvestrippers import strip_libor_curve, strip_libor_and_ois_curves
from datetime import date
from daycountconvention import actual_360
from instruments import EurodollarFuture, InterestRateSwap, LiborDeposit, OisBasisSwap

@pytest.mark.xfail
class TestStripLiborCurve:

    def test_without_edf(self):
        base_date = date(2018, 7, 16)
        notional = 1e6
        spot_start_date = date(2018, 7, 18)
        libor = LiborDeposit(notional, spot_start_date, 3, 0.0150)
        swap_1y = InterestRateSwap(notional, spot_start_date, 12, 0.0250)
        swap_5y = InterestRateSwap(notional, spot_start_date, 60, 0.0300)
        inputs = [libor, swap_1y, swap_5y]
        libor_curve = strip_libor_curve(base_date, inputs)
        assert(libor.value(libor_curve, libor_curve) == approx(0.0, abs=1e-4))
        assert(swap_1y.value(libor_curve, libor_curve) == approx(0.0, abs=1e-4))
        assert(swap_5y.value(libor_curve, libor_curve) == approx(0.0, abs=1e-4))

    def test_with_edf(self):
        base_date = date(2018, 7, 13)
        notional = 1e7
        spot_start_date = date(2018, 7, 17)
        libor = LiborDeposit(notional, spot_start_date, 3, 0.0090)
        edf_1 = EurodollarFuture(2018, 9)
        edf_price_1 = 98.5
        edf_2 = EurodollarFuture(2018, 12)
        edf_price_2 = 98.3
        edf_3 = EurodollarFuture(2019, 6)
        edf_price_3 = 97.9
        swap_10y = InterestRateSwap(notional, spot_start_date, 120, 0.0350)
        inputs = [libor, (edf_1, edf_price_1), (edf_2, edf_price_2), (edf_3, edf_price_3), swap_10y]
        libor_curve = strip_libor_curve(base_date, inputs)
        assert(libor.value(libor_curve, libor_curve) == approx(0.0))
        assert(edf_1.price(libor_curve) == approx(edf_price_1))
        assert(edf_2.price(libor_curve) == approx(edf_price_2))
        assert(edf_3.price(libor_curve) == approx(edf_price_3))
        assert(swap_10y.value(libor_curve, libor_curve) == approx(0.0, abs=1e-4))


@pytest.mark.xfail
class TestStripLiborAndOisCurves:

    def test_basic(self):
        base_date = date(2018, 7, 16)
        notional = 1e6
        spot_start_date = date(2018, 7, 18)
        libor = LiborDeposit(notional, spot_start_date, 3, 0.0150)
        edf = EurodollarFuture(2019, 12)
        edf_price = 98.40
        edf_input = (edf, edf_price)
        swap_1y = InterestRateSwap(notional, spot_start_date, 12, 0.0250)
        swap_5y = InterestRateSwap(notional, spot_start_date, 60, 0.0300)
        ois_basis_swap_3m = OisBasisSwap(notional, spot_start_date, 3, 0.0005)
        ois_basis_swap_2y = OisBasisSwap(notional, spot_start_date, 24, 0.0020)
        ois_basis_swap_5y = OisBasisSwap(notional, spot_start_date, 60, 0.0030)
        inputs = [libor, edf_input, swap_1y, swap_5y, ois_basis_swap_3m, ois_basis_swap_2y, ois_basis_swap_5y]
        libor_curve, ois_curve = strip_libor_and_ois_curves(base_date, inputs)
        assert(len(libor_curve.dates) == 4)
        assert(len(ois_curve.dates) == 3)
        assert(libor.value(libor_curve, ois_curve) == approx(0.0, abs=1e-4))
        assert(edf.price(libor_curve) == approx(edf_price))
        assert(swap_1y.value(libor_curve, ois_curve) == approx(0.0, abs=1e-4))
        assert(swap_5y.value(libor_curve, ois_curve) == approx(0.0, abs=1e-4))
        assert(ois_basis_swap_3m.value(libor_curve, ois_curve) == approx(0.0, abs=1e-4))
        assert(ois_basis_swap_2y.value(libor_curve, ois_curve) == approx(0.0, abs=1e-4))
        assert(ois_basis_swap_5y.value(libor_curve, ois_curve) == approx(0.0, abs=1e-4))

        # Check that the order of the inputs does not matter.
        permuted_inputs = [ois_basis_swap_2y, swap_5y, ois_basis_swap_3m, libor, ois_basis_swap_5y, swap_1y, edf_input]
        libor_curve_2, ois_curve_2 = strip_libor_and_ois_curves(base_date, permuted_inputs)
        assert(libor_curve_2.dates == libor_curve.dates)
        assert(libor_curve_2.dfs == approx(libor_curve.dfs))
        assert(ois_curve_2.dates == ois_curve.dates)
        assert(ois_curve_2.dfs == approx(ois_curve.dfs))
