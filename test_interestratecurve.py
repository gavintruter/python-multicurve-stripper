import pytest
from math import log
from datetime import date, timedelta
from daycountconvention import actual_365, actual_360
from interestratecurve import InterestRateCurve

def test_basic():
    base_date = date(2018, 7, 9)
    three_months = date(2018, 10, 9)
    one_year = date(2019, 7, 9)
    dates = [three_months, one_year]
    dfs = [0.98, 0.90]
    curve = InterestRateCurve(base_date, dates, dfs)
    with pytest.raises(ValueError):
        curve.df(base_date + timedelta(days=-1))
    assert(curve.df(base_date) == 1.0)
    assert(curve.df(three_months) == 0.98)
    assert(curve.df(one_year) == 0.90)

    # Two periods within the same PWC period must have the same rate.
    date1 = date(2018, 7, 15)
    date2 = date(2018, 8, 15)
    date3 = date(2018, 8, 30)
    rate1 = -log(curve.df(date2) / curve.df(date1)) / actual_365.yf(date1, date2)
    rate2 = -log(curve.df(date3) / curve.df(date2)) / actual_365.yf(date2, date3)
    assert(abs(rate1 - rate2) < 1e-6)

    # And the same over the last period, which goes from
    # the *second-last* date onwards.
    date1 = date(2019, 3, 9)
    date2 = one_year
    date3 = date(2019, 12, 9)
    rate1 = -log(curve.df(date2) / curve.df(date1)) / actual_365.yf(date1, date2)
    rate2 = -log(curve.df(date3) / curve.df(date2)) / actual_365.yf(date2, date3)
    assert(abs(rate1 - rate2) < 1e-6)

def test_forward():
    base_date = date(2018, 7, 13)
    dates = [date(2018, 10, 1), date(2019, 1, 1)]
    dfs = [0.97, 0.95]
    curve = InterestRateCurve(base_date, dates, dfs)

    start_date = date(2018, 8, 15)
    end_date = date(2018, 10, 15)
    start_df = curve.df(start_date)
    end_df = curve.df(end_date)
    forward = curve.forward(start_date, end_date, actual_360)
    yf = actual_360.yf(start_date, end_date)
    assert(abs(start_df / (1.0 + forward * yf) - end_df) < 1e-9)
