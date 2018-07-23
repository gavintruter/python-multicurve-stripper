class Actual360DayCountConvention:
    """Represents the Actual/360 day-count convention."""

    def yf(self, start_date, end_date):
        """Calculates the year-fraction between the given dates."""
        return (end_date - start_date).days / 360.0


class Actual365DayCountConvention:
    """Represents the Actual/365 Fixed day-count convention."""

    def yf(self, start_date, end_date):
        """Calculates the year-fraction between the given dates."""
        return (end_date - start_date).days / 365.0


class Thirty360DayCountConvention:
    """Represents the 30/360 Bonds Basis day-count convention."""

    def yf(self, start_date, end_date):
        """Calculates the year-fraction between the given dates."""
        (y1, m1, d1) = (start_date.year, start_date.month, start_date.day)
        (y2, m2, d2) = (end_date.year, end_date.month, end_date.day)
        d1 = min(d1, 30)
        if d1 == 30:
            d2 = min(d2, 30)
        return (360.0*(y2 - y1) + 30.0*(m2 - m1) + (d2 - d1)) / 360.0


"""Variable representing the Actual/360 day-count convention."""
actual_360 = Actual360DayCountConvention()


"""Variable representing the Actual/365 Fixed day-count convention."""
actual_365 = Actual365DayCountConvention()


"""Variable representing the 30/360 Bonds Basis day-count convention."""
thirty_360 = Thirty360DayCountConvention()
