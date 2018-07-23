"""
Strips Libor and OIS curves from market data, and uses them to find the value
of a forward-starting swap.
"""

from datetime import date
from curvestrippers import strip_libor_and_ois_curves
from dates import add_business_days, add_months_mod_foll
from instruments import LiborDeposit, EurodollarFuture, InterestRateSwap, OisBasisSwap

notional = 100
base_date = date(2018, 7, 27)
spot_start_date = add_business_days(base_date, 2)
inputs = [LiborDeposit(notional, spot_start_date, 3, 0.0170),
          (EurodollarFuture(2018, 9), 98.10),
          (EurodollarFuture(2018, 12), 97.90),
          (EurodollarFuture(2019, 3), 97.80),
          (EurodollarFuture(2019, 6), 97.70),
          (EurodollarFuture(2019, 9), 97.60),
          (EurodollarFuture(2019, 12), 97.50),
          (EurodollarFuture(2020, 3), 97.45),
          (EurodollarFuture(2020, 6), 97.40),
          InterestRateSwap(notional, spot_start_date, 36, 0.0250),
          InterestRateSwap(notional, spot_start_date, 48, 0.0260),
          InterestRateSwap(notional, spot_start_date, 60, 0.0270),
          InterestRateSwap(notional, spot_start_date, 72, 0.0280),
          InterestRateSwap(notional, spot_start_date, 84, 0.0285),
          InterestRateSwap(notional, spot_start_date, 96, 0.0290),
          InterestRateSwap(notional, spot_start_date, 108, 0.0289),
          InterestRateSwap(notional, spot_start_date, 120, 0.0295),
          OisBasisSwap(notional, spot_start_date, 12, 0.0010),
          OisBasisSwap(notional, spot_start_date, 24, 0.0012),
          OisBasisSwap(notional, spot_start_date, 36, 0.0016),
          OisBasisSwap(notional, spot_start_date, 48, 0.0020),
          OisBasisSwap(notional, spot_start_date, 60, 0.0022),
          OisBasisSwap(notional, spot_start_date, 72, 0.0025),
          OisBasisSwap(notional, spot_start_date, 84, 0.0026),
          OisBasisSwap(notional, spot_start_date, 96, 0.0027),
          OisBasisSwap(notional, spot_start_date, 108, 0.0029),
          OisBasisSwap(notional, spot_start_date, 120, 0.0030)]
libor_curve, ois_curve = strip_libor_and_ois_curves(base_date, inputs)

two_years_ahead = add_months_mod_foll(spot_start_date, 24)
new_swap_2y_5y = InterestRateSwap(-50 * 1e6, two_years_ahead, 60, 0.0305)
print('Value of short USD50m 2y5y forward-starting swap:')
print(new_swap_2y_5y.value(libor_curve, ois_curve))
