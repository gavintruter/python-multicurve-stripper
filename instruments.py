from dates import third_wednesday, add_months_mod_foll, date_schedule
from daycountconvention import actual_360, thirty_360

class LiborDeposit:
    """Represents Libor deposits."""

    def __init__(self, notional, start_date, tenor_in_months, rate):
        """Creates a Libor deposit."""
        self.start_date = start_date
        self.flow_on_start_date = -notional
        self.end_date = add_months_mod_foll(start_date, tenor_in_months)
        year_fraction = actual_360.yf(start_date, self.end_date)
        self.flow_on_end_date = notional * (1.0 + rate * year_fraction)

    def value(self, libor_curve, ois_curve):
        return (self.flow_on_start_date * libor_curve.df(self.start_date)
                + self.flow_on_end_date * libor_curve.df(self.end_date))


class EurodollarFuture:
    """"Represents a Eurodollar futures contract."""

    def __init__(self, year, month):
        """Creates a Eurodollar futures contract.

        Args:
            year: The expiry year as an integer, e.g. 2020.
            month: The expiry month as an integer, e.g. 3 for March.

        Returns:
            A EurodollarFuture. Its start date will be the expiry date, which is the
            third Wednesday of the expiry month. (The last trading day is two business
            days before that.)
        """
        pass

    def price(self, libor_curve):
        """Returns the fair futures price, with no convexity adjustment."""
        pass


class _FixedFlow:
    """ Represents a fixed interest flow on a swap. Not meant to be used by itself."""

    def __init__(self, notional, fixed_rate, start_date, end_date, dcc):
        self.amount = notional * fixed_rate * dcc.yf(start_date, end_date)
        self.end_date = end_date

    def value(self, libor_curve, ois_curve):
        return self.amount * ois_curve.df(self.end_date)


class _LiborFlow:
    """ Represents a Libor interest flow on a swap. Not meant to be used by itself."""

    def __init__(self, notional, start_date, end_date, dcc):
        pass
    
    def value(self, libor_curve, ois_curve):
        pass


class InterestRateSwap:
    """Represents a standard USD interest rate swap."""

    def __init__(self, notional, swap_start_date, tenor_in_months, fixed_rate):
        """
        Creates a standard USD interest rate swap.

        Args:
            notional: the notional of the swap. Positive for long (paying fixed) and negative
                for short (receiving fixed).
            swap_start_date: the effective date of the swap, which is usually two business days
                after the trade date.
            tenor_in_months: the length of the swap, e.g. 60 for a 5-year swap.
            fixed_rate: the rate paid on the fixed leg of the swap.

        Returns:
            An InterestRateSwap. The fixed flows are semi-annual and use the 30/360 day-count
            convention. The Libor flows are quarterly.
        """
        self.fixed_flows = [_FixedFlow(-notional, fixed_rate, start_date, end_date, thirty_360)
                            for (start_date, end_date) in date_schedule(swap_start_date, 6, tenor_in_months)]
        self.libor_flows = [_LiborFlow(notional, start_date, end_date, actual_360)
                            for (start_date, end_date) in date_schedule(swap_start_date, 3, tenor_in_months)]
        self.end_date = self.libor_flows[-1].end_date # Should be the same as the end date of the last fixed period.

    def value(self, libor_curve, ois_curve):
        """The value of the swap."""
        return (sum([fixed_flow.value(libor_curve, ois_curve) for fixed_flow in self.fixed_flows])
                + sum([libor_flow.value(libor_curve, ois_curve) for libor_flow in self.libor_flows]))


class _OisFlow:
    """ Represents an OIS-based interest flow on a swap. Not meant to be used by itself."""

    def __init__(self, notional, spread, start_date, end_date, dcc):
        self.multiple = notional * dcc.yf(start_date, end_date)
        self.spread = spread
        self.start_date = start_date
        self.end_date = end_date
        self.dcc = dcc

    def value(self, libor_curve, ois_curve):
        forward = ois_curve.forward(self.start_date, self.end_date, self.dcc)
        return self.multiple * (forward + self.spread) * ois_curve.df(self.end_date)


class OisBasisSwap:
    pass
