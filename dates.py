from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, WEEKLY, WE

def is_business_day(date):
    """
    Returns true if the given date is a business day, and false otherwise.
    
    Only returns false for weekends. Public holidays are ignored by this function.
    """
    pass


def adjust_following(date):
    """Adjust the date according to the "Following" business day convention."""
    pass


def adjust_preceding(date):
    """Adjust the date according to the "Preceding" business day convention."""
    pass


def adjust_modified_following(date):
    """Adjust the date according to the "Modified Following" business day convention."""
    pass


def add_business_days(start_date, num_days):
    pass


def third_wednesday(year, month):
    """
    Returns the third Wednesday of the given month in the given year.

    Eurodollar futures expire on these date.

    Args:
        year: The year as an integer, e.g. 2020.
        month: The month as an integer, e.g. 3 for March.

    Returns:
        The third Wednesday as a date, e.g. date(2020, 3, 18)
    """
    return rrule(WEEKLY, dtstart=date(year, month, 1), byweekday=WE)[2].date()


def add_months_mod_foll(start_date, num_months):
    """Add the number of months to the date and adjust the result using "Modified Following"."""
    return adjust_modified_following(start_date + relativedelta(months=num_months))


def date_schedule(start_date, period_in_months, tenor_in_months):
    """
    Creates a schedule of business dates with the given start date, period and length.

    Args:
        start_date: The start of the first period as a date, e.g. date(2018, 7, 27)
        period_in_months: The number of months in each period, e.g. 3 for a quarterly schedule.
        tenor_in_months: The duration of the schedule as a number of months, e.g. 60 for a 5-year schedule.

    Returns:
        The result is a list of two-element tuples. Each tuple represents a period. The first element of
        the tuple is the start of the period, and the second is the end of the period. The end date of each
        period is the same as the start date of the next one.
    """
    if not is_business_day(start_date):
        raise ValueError("Start date is not a business day.")
    if period_in_months not in [1, 3, 6, 12]:
        raise ValueError("Periods should be monthly, quarterly, semi-annual or annual.")
    if tenor_in_months % period_in_months != 0:
        raise ValueError("Tenor (in months) is not a multiple of the period (in months).")
    date_list = [add_months_mod_foll(start_date, months_ahead) for months_ahead
                 in range(0, tenor_in_months + 1, period_in_months)]
    return list(zip(date_list[:-1], date_list[1:]))

