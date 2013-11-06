import sys
import logging

from gmpy_cffi.interface import gmp, ffi
from gmpy_cffi.mpz import _pylong_to_mpz, mpz, _mpz_to_str, _new_mpz, _del_mpz, MAX_UI


if sys.version > '3':
    long = int
    xrange = range


cache_size = _incache = 100
_cache = []


def _init_cache():
    for _ in xrange(cache_size):
        mpq = ffi.new("mpq_t")
        gmp.mpq_init(mpq)
        _cache.append(mpq)
_init_cache()


def _new_mpq():
    """Return an initialized mpq_t."""
    global _incache

    if _incache:
#        logging.debug('_from_cache: %d', _incache)
        _incache -= 1
        return _cache[_incache]
    else:
#        logging.debug('_new_mpq')
        mpq = ffi.new("mpq_t")
        gmp.mpq_init(mpq)
        return mpq


def _del_mpq(mpq):
    global _incache

    if _incache < cache_size:
#        logging.debug('_to_cache: %d', _incache)
        _cache[_incache] = mpq
        _incache += 1
    else:
#        logging.debug('_del_mpq')
        gmp.mpq_clear(mpq)


def _mpq_to_str(a, base):
    l = (gmp.mpz_sizeinbase(gmp.mpq_numref(a), base) +
         gmp.mpz_sizeinbase(gmp.mpq_denref(a), base) + 3)
    p = ffi.new('char[]', l)
    gmp.mpq_get_str(ffi.NULL, base, a)
    gmp.mpq_get_str(p, base, a)
    return ffi.string(p)


def _str_to_mpq(s, base, a):
    if base == 0 or 2 <= base <= 62:
        if gmp.mpq_set_str(a, s, base) == -1:
            raise ValueError("Can't create mpq from %s with base %s" % (s, base))
    else:
        raise ValueError('base must be 0 or 2..62, not %s' % base)


class mpq(object):
    _mpq_str = None

    def __init__(self, *args):
        """
        mpq() -> mpq(0,1)

             If no argument is given, return mpq(0,1).

        mpq(n) -> mpq

             Return an 'mpq' object with a numeric value n. Decimal and
             Fraction values are converted exactly.

        mpq(n,m) -> mpq

             Return an 'mpq' object with a numeric value n/m.

        mpq(s[, base=10]) -> mpq

             Return an 'mpq' object from a string s made up of digits in
             the given base. s may be made up of two numbers in the same
             base separated by a '/' character.
        """

        #TODO kwargs (base)

        if len(args) == 1 and isinstance(args[0], self.__class__):
            self._mpq = args[0]._mpq
            return

        a = self._mpq = ffi.gc(_new_mpq(), _del_mpq)

        if len(args) == 0:
            gmp.mpq_set_ui(a, 0, 1)
        elif len(args) == 1:
            if isinstance(args[0], float):
                gmp.mpq_set_d(a, args[0])
            elif isinstance(args[0], (int, long)):
                if -sys.maxsize - 1 <= args[0] <= sys.maxsize:
                    gmp.mpq_set_si(a, args[0], 1)
                elif sys.maxsize < args[0] <= MAX_UI:
                    gmp.mpq_set_ui(a, args[0], 1)
                else:
                    assert isinstance(args[0], long)
                    tmp = _new_mpz()
                    _pylong_to_mpz(args[0], tmp)
                    gmp.mpq_set_z(a, tmp)
                    _del_mpz(tmp)
            elif isinstance(args[0], mpz):
                gmp.mpq_set_z(a, args[0]._mpz)
            elif isinstance(args[0], str):
                _str_to_mpq(args[0], 10, a)
            else:
                raise TypeError('mpq() requires numeric or string argument')
        elif len(args) == 2:
            if isinstance(args[0], str):
                _str_to_mpq(args[0], args[1], a)
            elif all(isinstance(arg, (int, long, mpz)) for arg in args):
                # Set Numerator
                if isinstance(args[0], mpz):
                    gmp.mpq_set_num(a, args[0]._mpz)
                else:
                    num = _new_mpz()
                    if -sys.maxsize - 1 <= args[0] <= sys.maxsize:
                        gmp.mpz_set_si(num, args[0])
                    elif sys.maxsize < args[0] <= MAX_UI:
                        gmp.mpz_set_ui(num, args[0])
                    else:
                        assert isinstance(args[0], long)
                        _pylong_to_mpz(args[0], num)
                    gmp.mpq_set_num(a, num)
                    _del_mpz(num)

                # Set Denominator
                if args[1] == 0:
                    raise ZeroDivisionError("zero denominator in 'mpq'")

                if isinstance(args[1], mpz):
                    gmp.mpq_set_den(a, args[1]._mpz)
                else:
                    den = _new_mpz()
                    if -sys.maxsize - 1 <= args[1] <= sys.maxsize:
                        gmp.mpz_set_si(den, args[1])
                    elif sys.maxsize < args[1] <= MAX_UI:
                        gmp.mpz_set_ui(den, args[1])
                    else:
                        assert isinstance(args[1], long)
                        _pylong_to_mpz(args[1], den)
                    gmp.mpq_set_den(a, den)
                    _del_mpz(den)
            else:
                raise NotImplementedError
        else:
            raise TypeError("mpq() requires 0, 1 or 2 arguments")

        # TODO only canonicalize when required (e.g. optimize mpq(42))
        gmp.mpq_canonicalize(a)

    @classmethod
    def _from_c_mpq(cls, mpq):
        inst = object.__new__(cls)
        inst._mpq = ffi.gc(mpq, _del_mpq)
        return inst

    def __str__(self):
        if self._mpq_str is None:
            self._mpq_str = _mpq_to_str(self._mpq, 10)
        return self._mpq_str

    def __repr__(self):
        tmp = ("%s" % self).split('/')
        if len(tmp) == 1:
            tmp.append('1')
        return "mpq(%s,%s)" % tuple(tmp)

    def __hex__(self):
        tmp = '0x' + _mpq_to_str(abs(self)._mpq, 16).replace('/', '/0x')
        return tmp if self >= 0 else '-' + tmp

    def __oct__(self):
        tmp = '0' + _mpq_to_str(abs(self._mpq), 16).replace('/', '/0')
        return tmp if self >= 0 else '-' + tmp

    def __add__(self, other):
        res = _new_mpq()
        if isinstance(other, mpq):
            gmp.mpq_add(res, self._mpq, other._mpq)
        else:
            raise NotImplementedError
        return mpq._from_c_mpq(res)

    def __sub__(self, other):
        res = _new_mpq()
        if isinstance(other, mpq):
            gmp.mpq_sub(res, self._mpq, other._mpq)
        else:
            raise NotImplementedError
        return mpq._from_c_mpq(res)

    def __rsub__(self, other):
        raise NotImplementedError

    def __mul__(self, other):
        res = _new_mpq()
        if isinstance(other, mpq):
            gmp.mpq_mul(res, self._mpq, other._mpq)
        else:
            raise NotImplementedError
        return mpq._from_c_mpq(res)

    def __floordiv__(self, other):
        raise NotImplementedError

    def __rfloordiv__(self, other):
        raise NotImplementedError

    def __mod__(self, other):
        raise NotImplementedError

    def __rmod__(self, other):
        raise NotImplementedError

    def __divmod__(self, other):
        raise NotImplementedError

    def __rdivmod__(self, other):
        raise NotImplementedError

    def __lshift__(self, other):
        raise NotImplementedError

    def __rlshift__(self, other):
        raise NotImplementedError

    def __rshift__(self, other):
        raise NotImplementedError

    def __rrshift__(self, other):
        raise NotImplementedError

    def __cmp__(self, other):
        if isinstance(other, mpq):
            res = gmp.mpq_cmp(self._mpq, other._mpq)
        elif isinstance(other, (int, long)):
            tmp_mpz = _new_mpz()
            tmp_mpq = _new_mpq()
            if -sys.maxsize - 1 <= other <= sys.maxsize:
                gmp.mpz_set_si(tmp_mpz, other)
            elif sys.maxsize < other <= MAX_UI:
                gmp.mpz_set_ui(tmp_mpz, other)
            else:
                _pylong_to_mpz(other, tmp_mpz)
            gmp.mpq_set_z(tmp_mpq, tmp_mpz)
            res = gmp.mpq_cmp(self._mpq, tmp_mpq)
            _del_mpz(tmp_mpz)
            _del_mpq(tmp_mpq)
        else:
            raise TypeError("Can't compare mpq with '%s'" % type(other))
        return res

    def __int__(self):
        res = _new_mpz()
        num = _new_mpz()
        den = _new_mpz()

        gmp.mpq_get_num(num, self._mpq)
        gmp.mpq_get_den(den, self._mpq)

        gmp.mpz_tdiv_q(res, num, den)

        _del_mpz(num)
        _del_mpz(den)
        return int(mpz._from_c_mpz(res))

    def __long__(self):
        res = _new_mpz()
        num = _new_mpz()
        den = _new_mpz()

        gmp.mpq_get_num(num, self._mpq)
        gmp.mpq_get_den(den, self._mpq)

        gmp.mpz_tdiv_q(res, num, den)

        _del_mpz(num)
        _del_mpz(den)
        return long(mpz._from_c_mpz(res))

    def __float__(self):
        return gmp.mpq_get_d(self._mpq)

    def __complex__(self):
        float(self) + 0j

    def __abs__(self):
        res = _new_mpq()
        gmp.mpq_abs(res, self._mpq)
        return mpq._from_c_mpq(res)

    def __neg__(self):
        res = _new_mpq()
        gmp.mpq_neg(res, self._mpq)
        return mpq._from_c_mpq(res)

    def __pos__(self):
        return self

    def __invert__(self):
        raise NotImplementedError

    def __and__(self, other):
        raise NotImplementedError

    def __or__(self, other):
        raise NotImplementedError

    def __xor__(self, other):
        raise NotImplementedError

    def __nonzero__(self):
        raise NotImplementedError

    def __pow__(self, other, modulo=None):
        raise NotImplementedError

    def __rpow__(self, other):
        raise NotImplementedError