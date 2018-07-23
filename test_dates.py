import pytest
from datetime import date
from dates import (is_business_day, adjust_following, adjust_preceding,
                   adjust_modified_following, add_business_days, third_wednesday,
                   add_months_mod_foll, date_schedule)

wednesday = date(2018, 7, 11)
thursday = date(2018, 7, 12)
friday = date(2018, 7, 13)
saturday = date(2018, 7, 14)
sunday = date(2018, 7, 15)
monday = date(2018, 7, 16)
tuesday = date(2018, 7, 17)

friday_eom = date(2018, 9, 28)
saturday_eom = date(2018, 9, 29)
sunday_eom = date(2018, 9, 30)
monday_eom = date(2018, 10, 1)


@pytest.mark.xfail
def test_is_business_day():
    assert(is_business_day(friday))
    assert(not is_business_day(saturday))
    assert(not is_business_day(sunday))
    assert(is_business_day(monday))


@pytest.mark.xfail
def test_adjust_following():
    assert(adjust_following(friday) == friday)
    assert(adjust_following(saturday) == monday)
    assert(adjust_following(sunday) == monday)
    assert(adjust_following(monday) == monday)
    assert(adjust_following(saturday_eom) == monday_eom)
    assert(adjust_following(sunday_eom) == monday_eom)


@pytest.mark.xfail
def test_adjust_modified_following():
    assert(adjust_modified_following(friday) == friday)
    assert(adjust_modified_following(saturday) == monday)
    assert(adjust_modified_following(sunday) == monday)
    assert(adjust_modified_following(monday) == monday)
    assert(adjust_modified_following(friday_eom) == friday_eom)
    assert(adjust_modified_following(saturday_eom) == friday_eom)
    assert(adjust_modified_following(sunday_eom) == friday_eom)
    assert(adjust_modified_following(monday_eom) == monday_eom)


@pytest.mark.xfail
def test_add_business_days_usual():
    assert(add_business_days(wednesday, 1) == thursday)
    assert(add_business_days(wednesday, 2) == friday)
    assert(add_business_days(wednesday, 3) == monday)
    assert(add_business_days(wednesday, 4) == tuesday)
    assert(add_business_days(thursday, 1) == friday)
    assert(add_business_days(thursday, 2) == monday)


@pytest.mark.xfail
def test_add_business_days_on_weekends():
    with pytest.raises(ValueError):
        add_business_days(saturday, 1)
    with pytest.raises(ValueError):
        add_business_days(sunday, 3)


@pytest.mark.xfail
def test_add_business_days_zero_days():
    assert(add_business_days(wednesday, 0) == wednesday)
    assert(add_business_days(friday, 0) == friday)
    with pytest.raises(ValueError):
        add_business_days(saturday, 0)
    with pytest.raises(ValueError):
        add_business_days(sunday, 0)


@pytest.mark.xfail
def test_add_business_days_negative_days():
    with pytest.raises(ValueError):
        add_business_days(wednesday, -1)
    with pytest.raises(ValueError):
        add_business_days(friday, -2)


@pytest.mark.xfail
def test_add_months_mod_foll():
    assert(add_months_mod_foll(date(2018, 7, 26), 3) == date(2018, 10, 26))
    assert(add_months_mod_foll(date(2018, 7, 27), 3) == date(2018, 10, 29))
    assert(add_months_mod_foll(date(2018, 6, 29), 3) == date(2018, 9, 28))
    assert(add_months_mod_foll(date(2018, 6, 29), 1) == date(2018, 7, 30))


@pytest.mark.xfail
def test_date_schedule_1():
    start_date = date(2018, 7, 13)
    period_in_months = 6
    tenor_in_months = 12
    six_months = date(2019, 1, 14)
    one_year = date(2019, 7, 15)
    assert(date_schedule(start_date, period_in_months, tenor_in_months)
           == [(start_date, six_months), (six_months, one_year)])


@pytest.mark.xfail
def test_date_schedule_2():
    start_date = date(2018, 10, 1)
    period_in_months = 3
    tenor_in_months = 12
    d1 = date(2019, 1, 1)
    d2 = date(2019, 4, 1)
    d3 = date(2019, 7, 1)
    d4 = date(2019, 10, 1)
    assert(date_schedule(start_date, period_in_months, tenor_in_months)
           == [(start_date, d1), (d1, d2), (d2, d3), (d3, d4)])


@pytest.mark.xfail
def test_date_schedule_mf():
    start_date = date(2018, 6, 29)
    period_in_months = 3
    tenor_in_months = 24
    d1 = date(2018, 9, 28)
    d2 = date(2018, 12, 31)
    d3 = date(2019, 3, 29)
    d4 = date(2019, 6, 28)
    d5 = date(2019, 9, 30)
    d6 = date(2019, 12, 30)
    d7 = date(2020, 3, 30)
    d8 = date(2020, 6, 29)
    assert(date_schedule(start_date, period_in_months, tenor_in_months)
           == [(start_date, d1), (d1, d2), (d2, d3), (d3, d4),
               (d4, d5), (d5, d6), (d6, d7), (d7, d8)])


def test_third_wednesday():
    assert(third_wednesday(2018, 7) == date(2018, 7, 18))
    assert(third_wednesday(2018, 8) == date(2018, 8, 15))
    assert(third_wednesday(2018, 9) == date(2018, 9, 19))
    assert(third_wednesday(2018, 10) == date(2018, 10, 17))
    assert(third_wednesday(2018, 11) == date(2018, 11, 21))
    assert(third_wednesday(2019, 1) == date(2019, 1, 16))
