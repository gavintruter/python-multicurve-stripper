from scipy.optimize import root
from instruments import OisBasisSwap
from interestratecurve import InterestRateCurve


def _is_eurodollar_future_and_price(input):
    return isinstance(input, tuple)


def _node_date(input):
    if _is_eurodollar_future_and_price(input):
        return input[0].end_date
    else:
        return input.end_date


def _scalar_objective_function(input, libor_curve, ois_curve):
    if _is_eurodollar_future_and_price(input):
        return input[0].price(libor_curve) - input[1]
    else:
        return input.value(libor_curve, ois_curve)


def strip_libor_curve(base_date, inputs):
    """
    Strips a Libor curve from market data.

    Args:
        base_date: the date on which the curve is stripped.
        inputs: a list of any combination of LiborDeposits, fair InterestRateSwaps,
            and/or two-element tuples where the first element is a
            EurodollarFuture and the second element is its market price.

    Returns:
        An InterestRateCurve that, when used as both the Libor and the OIS curves,
        gives values of zero to the input LiborDeposits and InterestRateSwaps,
        and fair prices of the Eurodollar futures that match their market prices.
    """
    dates = sorted([_node_date(input) for input in inputs])

    def make_curve(dfs):
        return InterestRateCurve(base_date, dates, dfs)

    def vector_objective_function(dfs):
        curve = make_curve(dfs)
        return [_scalar_objective_function(input, curve, curve) for input in inputs]

    sol = root(vector_objective_function, [1.0] * len(inputs))
    if sol.success:
        return make_curve(sol.x)
    else:
        raise ValueError("Could not strip Libor curve: " + sol.message)


def _is_ois_input(input):
    return isinstance(input, OisBasisSwap)
    

def strip_libor_and_ois_curves(base_date, inputs):
    pass
