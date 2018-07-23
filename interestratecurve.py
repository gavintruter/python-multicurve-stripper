from daycountconvention import actual_365
from math import exp, log
from scipy.interpolate import interp1d

class InterestRateCurve(object):
    """
    Represents an interest rate curve.

    The interpolation is linear in log discount factors, i.e. piecewise-constant
    forwards, with Actual/365 year-fractions. Linear extrapolation is used after
    the last node, so that the final piecewise constant segment is extended.
    """

    def __init__(self, base_date, dates, dfs):
        """
        Creates an InterestRateCurve.

        Args:
            base_date: the date on which the curve applies, for which the discount factor is 1,
                e.g. date(2018, 7, 27)
            dates: a list of dates, in order, e.g. [date(2018, 10, 27), date(2019, 7, 27)].
            dfs: a list of discount factors, one for each date, e.g. [0.99, 0.98]
        """
        if len(dates) != len(dfs):
            raise ValueError("Curve cannot be created: dates and DFs are different lengths.")
        if sorted(dates) != dates:
            raise ValueError("Curve dates are not in order.")
        self._base_date = base_date
        self._dates = dates
        self._dfs = dfs
        yfs = [actual_365.yf(base_date, date) for date in dates]
        log_dfs = [log(df) for df in dfs]
        yfs.insert(0, 0.0)
        log_dfs.insert(0, 0.0)
        self._log_df = interp1d(yfs, log_dfs, fill_value="extrapolate")

    @property
    def base_date(self):
        return self._base_date

    @property
    def dates(self):
        return self._dates

    @property
    def dfs(self):
        return self._dfs

    def df(self, date):
        """Calculate the discount factor for the date."""
        if date < self._base_date:
            raise ValueError("Cannot get DF for date before base date.")
        return exp(self._log_df(actual_365.yf(self._base_date, date))[()])

    def forward(self, start_date, end_date, dcc):
        """Calculate the simple forward rate over the period, with the day-count convention."""
        return (self.df(start_date) / self.df(end_date) - 1.0) / dcc.yf(start_date, end_date)
