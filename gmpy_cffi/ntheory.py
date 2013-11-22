import sys

from gmpy_cffi.interface import gmp
from gmpy_cffi.mpz import mpz, _new_mpz


PY3 = sys.version_info >= (3, 0)


if PY3:
    long = int
    xrange = range


def is_prime(x, n=25):
    """
    is_prime(x[, n=25]) -> bool

    Return True if x is _probably_ prime, else False if x is
    definately composite. x is checked for small divisors and up
    to n Miller-Rabin tests are performed.
    """

    if isinstance(x, mpz):
        pass
    elif isinstance(x, (int, long)):
        x = mpz(x)
    else:
        raise TypeError('is_prime() expected integer x got %s' % type(x))

    if not (isinstance(n, int) and n <= sys.maxsize):
        raise TypeError('is_prime() expected integer n got %s' % type(n))

    if n <= 0:
        raise ValueError("is_prime repitition count must be positive")

    return gmp.mpz_probab_prime_p(x._mpz, n) != 0


def next_prime(x):
    """
    next_prime(x) -> mpz

    Return the next _probable_ prime number > x.
    """

    if isinstance(x, mpz):
        pass
    elif isinstance(x, (int, long)):
        x = mpz(x)
    else:
        raise TypeError('next_prime() expected integer x got %s' % type(x))

    res = _new_mpz()
    gmp.mpz_nextprime(res, x._mpz)
    return mpz._from_c_mpz(res)


def gcd(a, b):
    """
    gcd(a, b) -> mpz

    Return the greatest common denominator of integers a and b.
    """

    if isinstance(a, mpz):
        pass
    elif isinstance(a, (int, long)):
        a = mpz(a)
    else:
        raise TypeError('gcd() expected integer a got %s' % type(a))

    if isinstance(b, mpz):
        pass
    elif isinstance(b, (int, long)):
        b = mpz(b)
    else:
        raise TypeError('gcd() expected integer b got %s' % type(b))

    res = _new_mpz()
    gmp.mpz_gcd(res, a._mpz, b._mpz)
    return mpz._from_c_mpz(res)


def gcdext(a, b):
    """
    gcdext(a, b) - > tuple

    Return a 3-element tuple (g,s,t) such that
        g == gcd(a,b) and g == a*s + b*t
    """
    if isinstance(a, mpz):
        pass
    elif isinstance(a, (int, long)):
        a = mpz(a)
    else:
        raise TypeError('gcdex() expected integer a got %s' % type(a))

    if isinstance(b, mpz):
        pass
    elif isinstance(b, (int, long)):
        b = mpz(b)
    else:
        raise TypeError('gcdex() expected integer b got %s' % type(b))

    mpz_g, mpz_s, mpz_t = _new_mpz(), _new_mpz(), _new_mpz()
    gmp.mpz_gcdext(mpz_g, mpz_s, mpz_t, a._mpz, b._mpz)
    return (mpz._from_c_mpz(mpz_g), mpz._from_c_mpz(mpz_s), mpz._from_c_mpz(mpz_t))


def lcm(a, b):
    """
    lcm(a, b) -> mpz

    Return the lowest common multiple of integers a and b.
    """

    if isinstance(a, mpz):
        pass
    elif isinstance(a, (int, long)):
        a = mpz(a)
    else:
        raise TypeError('lcm() expected integer a got %s' % type(a))

    if isinstance(b, mpz):
        pass
    elif isinstance(b, (int, long)):
        b = mpz(b)
    else:
        raise TypeError('lcm() expected integer b got %s' % type(b))

    res = _new_mpz()
    gmp.mpz_lcm(res, a._mpz, b._mpz)
    return mpz._from_c_mpz(res)


def invert(x, m):
    """
    invert(x, m) -> mpz

    Return y such that x*y == 1 (mod m). Raises ZeroDivisionError if no
    inverse exists.
    """
    if isinstance(x, mpz):
        pass
    elif isinstance(x, (int, long)):
        x = mpz(x)
    else:
        raise TypeError('invert() expected integer x got %s' % type(x))

    if isinstance(m, mpz):
        pass
    elif isinstance(m, (int, long)):
        m = mpz(m)
    else:
        raise TypeError('lcm() expected integer m got %s' % type(m))

    res = _new_mpz()
    if gmp.mpz_invert(res, x._mpz, m._mpz) == 0:
        raise ZeroDivisionError
    return mpz._from_c_mpz(res)