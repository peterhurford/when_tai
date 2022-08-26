import math
import random
import numpy as np
from scipy import stats


def normal_sample(low, high, interval):
    if low > high:
        raise ValueError('`high value` cannot be lower than `low value`')
    if low == high:
        return low
    else:
        mu = (high + low) / 2
        cdf_value = 0.5 + 0.5 * interval
        normed_sigma = stats.norm.ppf(cdf_value)
        sigma = (high - mu) / normed_sigma
        return np.random.normal(mu, sigma)

    
def lognormal_sample(low, high, interval):
    if low > high:
        raise ValueError('`high value` cannot be lower than `low value`')
    if low < 0:
        raise ValueError('lognormal_sample cannot handle negative values')
    if low == high:
        return low
    else:
        log_low = np.log(low)
        log_high = np.log(high)
        mu = (log_high + log_low) / 2
        cdf_value = 0.5 + 0.5 * interval
        normed_sigma = stats.norm.ppf(cdf_value)
        sigma = (log_high - mu) / normed_sigma
        return np.random.lognormal(mu, sigma)


def t_sample(low, high, t, interval):
    if low > high:
        raise ValueError('`high value` cannot be lower than `low value`')
    if low == high:
        return low
    else:
        mu = (high + low) / 2
        rangex = (high - low) / 2
        return np.random.standard_t(t) * rangex * 0.6/interval + mu


def log_t_sample(low, high, t, interval):
    if low > high:
        raise ValueError('`high value` cannot be lower than `low value`')
    if low < 0:
        raise ValueError('log_t_sample cannot handle negative values')
    if low == high:
        return low
    else:
        log_low = np.log(low)
        log_high = np.log(high)
        mu = (log_high + log_low) / 2
        rangex = (log_high - log_low) / 2
        return np.exp(np.random.standard_t(t) * rangex * 0.6/interval + mu)
    

def norm(x, y, lclip=None, rclip=None):
    return [x, y, 'norm', lclip, rclip]

def const(x):
    return [x, None, 'const', None, None]

def lognorm(x, y, lclip=None, rclip=None):
    return [x, y, 'log', lclip, rclip]

def weighted_lognorm(logs, weights, lclip=None, rclip=None):
    return [logs, weights, 'weighted_log', lclip, rclip]

def distributed_lognorm(logs, weights, lclip=None, rclip=None):
    return [logs, weights, 'distributed_log', lclip, rclip]

def tdist(x, y, t, lclip=None, rclip=None):
    return [x, y, 'tdist', t, lclip, rclip]

def log_tdist(x, y, t, lclip=None, rclip=None):
    return [x, y, 'log-tdist', t, lclip, rclip]


def sample(var, credibility=0.9):
    if callable(var):
        return var()

    if not isinstance(var, list) and not (len(var) == 5 or len(var) == 6):
        raise ValueError('input to sample is malformed - must be sample data')

    if var[2] == 'const':
        out = var[0]

    elif var[2] == 'norm':
        out = normal_sample(var[0], var[1], credibility)

    elif var[2] == 'log':
        out = lognormal_sample(var[0], var[1], credibility)

    elif var[2] == 'weighted_log':
        weights = var[1]
        sum_weights = sum(weights)
        if sum_weights <= 0.99 or sum_weights >= 1.01:
            raise ValueError('weighted_log weights don\'t sum to 1 - they sum to {}'.format(sum_weights))
        if len(weights) != len(var[0]):
            raise ValueError('weighted_log weights and distributions not same length')
        log_result = 0
        for i, log_data in enumerate(var[0]):
            log_value = lognormal_sample(log_data[0], log_data[1], credibility)
            weight = weights[i]
            log_result += log_value * weight
        out = log_result

    elif var[2] == 'distributed_log':
        weights = var[1]
        sum_weights = sum(weights)
        if sum_weights <= 0.99 or sum_weights >= 1.01:
            raise ValueError('distributed_log weights don\'t sum to 1 - they sum to {}'.format(sum_weights))
        if len(weights) != len(var[0]):
            raise ValueError('distributed_log weights and distributions not same length')
        r_ = random.random()
        weights = np.cumsum(weights)
        done = False
        for i, log_data in enumerate(var[0]):
            if not done:
                weight = weights[i]
                if r_ <= weight:
                    out = lognormal_sample(log_data[0], log_data[1], credibility)
                    done = True

    elif var[2] == 'tdist':
        out = t_sample(var[0], var[1], var[3], credibility)

    elif var[2] == 'log-tdist':
        out = log_t_sample(var[0], var[1], var[3], credibility)

    else:
        raise ValueError('{} sampler not found'.format(var[2]))

    if var[2] == 'tdist' or var[2] == 'log-tdist':
        lclip = var[4]
        rclip = var[5]
    else:
        lclip = var[3]
        rclip = var[4]

    if lclip and out < lclip:
        out = lclip
    if rclip and out > rclip:
        out = rclip

    return out


def event_occurs(p):
    return random.random() < p


def numerize(oom_num):
    oom_num = int(oom_num)
    ooms = ['thousand', 'million', 'billion', 'trillion', 'quadrillion', 'quintillion', 'sextillion', 'septillion', 'octillion', 'nonillion', 'decillion']

    if oom_num == 0:
        return 'one'
    elif oom_num == 1:
        return 'ten'
    elif oom_num == 2:
        return 'hundred'
    elif oom_num > 35:
        return numerize(oom_num - 33) + ' decillion'
    elif oom_num < 0:
        return numerize(-oom_num) + 'th'
    elif oom_num % 3 == 0:
        return 'one ' + ooms[(oom_num // 3) - 1]
    else:
        return str(10 ** (oom_num % 3)) + ' ' + ooms[(oom_num // 3) - 1]


def format_gb(gb):
    if gb >= 1000:
        tb = np.round(gb / 1000)
    else:
        return str(gb) + ' GB'
    
    if tb >= 1000:
        pb = np.round(tb / 1000)
    else:
        return str(tb) + ' TB'

    if pb >= 10000:
        return numerize(math.log10(pb)) + ' PB'
    else:
        return str(pb) + ' PB'
    

def get_percentiles(data, percentiles=[1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99], reverse=False, digits=None):
    percentile_labels = list(reversed(percentiles)) if reverse else percentiles
    percentiles = np.percentile(data, percentiles)
    if digits is not None:
        percentiles = np.round(percentiles, digits)
    return dict(list(zip(percentile_labels, percentiles)))


def get_log_percentiles(data, percentiles, reverse=False, display=True, digits=1):
    percentiles = get_percentiles(data, percentiles=percentiles, reverse=reverse, digits=digits)
    if display:
        return dict([(k, '10^{} (~{})'.format(np.round(np.log10(v), digits), numerize(np.log10(v)))) for k, v in percentiles.items()])
    else:
        return dict([(k, np.round(np.log10(v), digits)) for k, v in percentiles.items()])


def plot_tai(plt, years, cost_of_tai_collector, willingness_collector):
    cost = np.log10(np.array(cost_of_tai_collector))
    willingness = np.log10(np.array(willingness_collector))
    plt.plot(years[:len(cost)], cost, label='Cost of TAI')
    plt.plot(years[:len(willingness)], willingness, label='Willingness to pay for TAI')
    plt.legend()
    plt.ylabel('log $')
    return plt


def savitzky_golay(y, window_size, order, deriv=0, rate=1):
    r"""Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techniques.
    Parameters
    ----------
    y : array_like, shape (N,)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv: int
        the order of the derivative to compute (default = 0 means only smoothing)
    Returns
    -------
    ys : ndarray, shape (N)
        the smoothed signal (or it's n-th derivative).
    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.
    Examples
    --------
    t = np.linspace(-4, 4, 500)
    y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    ysg = savitzky_golay(y, window_size=31, order=4)
    import matplotlib.pyplot as plt
    plt.plot(t, y, label='Noisy signal')
    plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    plt.plot(t, ysg, 'r', label='Filtered signal')
    plt.legend()
    plt.show()
    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    """    
    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError:
        raise ValueError("window_size and order have to be of type int")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 2:
        raise TypeError("window_size is too small for the polynomials order")
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    # precompute coefficients
    b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
    m = np.linalg.pinv(b).A[deriv] * rate**deriv * math.factorial(deriv)
    # pad the signal at the extremes with
    # values taken from the signal itself
    firstvals = y[0] - np.abs( y[1:half_window+1][::-1] - y[0] )
    lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])
    y = np.concatenate((firstvals, y, lastvals))
    return np.convolve( m[::-1], y, mode='valid')


million = 1000000                   # 10^6
billion = 1000 * million            # 10^9
trillion = 1000 * billion           # 10^12
quadrillion = 1000 * trillion       # 10^15
quintillion = 1000 * quadrillion    # 10^18
sextillion = 1000 * quintillion     # 10^21
septillion = 1000 * sextillion      # 10^24
octillion = 1000 * septillion       # 10^27
nonillion = 1000 * octillion        # 10^30
decillion = 1000 * nonillion        # 10^33
    
print('Loaded')
