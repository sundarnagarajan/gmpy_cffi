from __future__ import division

import sys
import pytest
from gmpy_cffi import mpz, MAX_UI


PY3 = sys.version.startswith('3')


if PY3:
    long = int


invalids = [(), [], set(), dict(), lambda x: x**2]


class TestInit(object):
    small_ints = [-1, 0, 1, 123, -9876, sys.maxsize, -sys.maxsize - 1]
    big_ints = [sys.maxsize + 1, -sys.maxsize - 2, 2 * sys.maxsize + 1, 2 * sys.maxsize + 2]

    @pytest.mark.parametrize('n', small_ints + big_ints)
    def test_init_int(self, n):
        assert mpz(n) == n

    @pytest.mark.parametrize('f', [0.0, 1.0, 1.5, 1e15 + 0.9])
    def test_init_float(self, f):
        assert mpz(f) == int(f)
        assert mpz(-f) == int(-f)

    @pytest.mark.parametrize('n', small_ints + big_ints)
    def test_init_decimal_str(self, n):
        assert mpz(str(n), 10) == n
        assert mpz(str(n)) == n
        assert mpz(str(n), 0) == n
        assert mpz(hex(n).rstrip('L'), 0) == n
        if PY3:
            assert mpz(oct(n).rstrip('L').replace('0o', '0'), 0) == n
        else:
            assert mpz(oct(n).rstrip('L'), 0) == n

    @pytest.mark.parametrize('n', small_ints + big_ints)
    def test_init_hex_str(self, n):
        assert mpz("%x" % n, 16) == n
        assert mpz("%#x" % n, 0) == n

    @pytest.mark.parametrize(('n', 'base'), [('0x1', 16), ('g', 16), ('a', 10)])
    def test_init_invalid_str(self, n, base):
        with pytest.raises(ValueError):
            mpz(n, base)

    @pytest.mark.parametrize(('n', 'base'), [('0', -1), ('0', 1), ('0', 63), (0, 10)])
    def test_init_invalid_base(self, n, base):
        with pytest.raises(ValueError):
            mpz(n, base)

    @pytest.mark.parametrize('type_', [int, float, mpz, str])
    def test_init_type(self, type_):
        assert mpz(type_(1)) == 1

    @pytest.mark.parametrize('n', invalids)
    def test_init_invalid(self, n):
        with pytest.raises(TypeError):
            mpz(n)


class TestMath(object):
    numbers = [-1, 0, 1, sys.maxsize, -sys.maxsize - 1, MAX_UI, MAX_UI + 1]

    @pytest.mark.parametrize('b', numbers)
    def test_add(self, b):
        assert mpz(1) + mpz(b) == mpz(1 + b)
        assert mpz(1) + b == mpz(1 + b)

    @pytest.mark.parametrize('b', numbers)
    def test_radd(self, b):
        assert b + mpz(1) == mpz(b + 1)

    @pytest.mark.parametrize('b', numbers)
    def test_sub(self, b):
        assert mpz(1) - mpz(b) == mpz(1 - b)
        assert mpz(1) - b == mpz(1 - b)

    @pytest.mark.parametrize('b', numbers)
    def test_rsub(self, b):
        assert b - mpz(1) == mpz(b - 1)

    @pytest.mark.parametrize('b', numbers)
    def test_mul(self, b):
        assert mpz(2) * mpz(b) == mpz(2 * b)
        assert mpz(2) * b == mpz(2 * b)

    @pytest.mark.parametrize('b', numbers)
    def test_rmul(self, b):
        assert b * mpz(2) == mpz(b * 2)

    @pytest.mark.parametrize('b', numbers)
    def test_floordiv(self, b):
        if b != 0:
            assert mpz(2) // mpz(b) == mpz(2 // b)
            assert mpz(2) // b == mpz(2 // b)
        else:
            with pytest.raises(ZeroDivisionError):
                mpz(2) // mpz(b)
            with pytest.raises(ZeroDivisionError):
                mpz(2) // b

    @pytest.mark.parametrize('b', numbers)
    def test_rfloordiv(self, b):
        assert b // mpz(2) == mpz(b // 2)

    def test_rfloordiv_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            1 // mpz(0)

    @pytest.mark.xfail(reason='__truediv__ needs mpf')
    def test_truediv(self):
        assert mpz(3) / mpz(2) == 1.5

    @pytest.mark.parametrize('b', numbers)
    def test_mod(self, b):
        if b != 0:
            assert mpz(2) % mpz(b) == mpz(2 % b)
            assert mpz(2) % b == mpz(2 % b)
        else:
            with pytest.raises(ZeroDivisionError):
                mpz(2) % mpz(b)
            with pytest.raises(ZeroDivisionError):
                mpz(2) % b

    @pytest.mark.parametrize('b', numbers)
    def test_rmod(self, b):
        assert b % mpz(2) == mpz(b % 2)

    def test_rmod_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            1 % mpz(0)

    @pytest.mark.parametrize('b', numbers)
    def test_divmod(self, b):
        if b != 0:
            assert divmod(mpz(2), mpz(b)) == tuple(map(mpz, divmod(2, b)))
            assert divmod(mpz(2), b) == tuple(map(mpz, divmod(2, b)))
        else:
            with pytest.raises(ZeroDivisionError):
                divmod(mpz(2), mpz(b))
            with pytest.raises(ZeroDivisionError):
                divmod(mpz(2), b)

    @pytest.mark.parametrize('b', numbers)
    def test_rdivmod(self, b):
        assert divmod(b, mpz(2)) == tuple(map(mpz, divmod(b, 2)))

    def test_rdivmod_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            divmod(1, mpz(0))

    @pytest.mark.parametrize('b', [0, 2, 1 << 16])
    def test_shifts(self, b):
        assert mpz(1) << mpz(b) == mpz(1 << b)
        assert mpz(1) << b == mpz(1 << b)
        assert mpz(1 << 100) >> mpz(b) == mpz((1 << 100) >> b)
        assert mpz(1 << 100) >> b == mpz((1 << 100) >> b)

    @pytest.mark.parametrize('b', [0, 2, sys.maxsize, MAX_UI])
    def test_rshifts(self, b):
        assert b << mpz(1) == mpz(b << 1)
        assert b >> mpz(1) == mpz(b >> 1)

    @pytest.mark.parametrize('b', [-1, MAX_UI + 1])
    def test_shifts_invalid_shift(self, b):
        with pytest.raises(OverflowError):
            mpz(1) << b
        with pytest.raises(OverflowError):
            mpz(1) >> b

    @pytest.mark.parametrize('type_', [int, long, mpz])
    def test_shifts_valid_type(self, type_):
        assert mpz(1) << type_(1) == mpz(2)
        assert mpz(4) >> type_(1) == mpz(2)

    @pytest.mark.parametrize('type_', [float, str])
    def test_shifts_invalid_type(self, type_):
        with pytest.raises(TypeError):
            mpz(1) << type_(1)
        with pytest.raises(TypeError):
            mpz(1) >> type_(1)

    @pytest.mark.parametrize('type_', [float, str])
    def test_rshifts_invalid_type(self, type_):
        with pytest.raises(TypeError):
            type_(1) << mpz(1)
        with pytest.raises(TypeError):
            type_(1) >> mpz(1)

    def test_str(self):
        n = mpz('123456789abcdef0', 16)
        assert str(n) == '1311768467463790320'
        assert repr(n) == 'mpz(1311768467463790320)'
        assert hex(n) == '0x123456789abcdef0'
        if PY3:
            assert oct(n) == '0o110642547423257157360'
        else:
            assert oct(n) == '0110642547423257157360'
        n = -mpz('123456789abcdef0', 16)
        assert str(n) == '-1311768467463790320'
        assert repr(n) == 'mpz(-1311768467463790320)'
        assert hex(n) == '-0x123456789abcdef0'
        if PY3:
            assert oct(n) == '-0o110642547423257157360'
        else:
            assert oct(n) == '-0110642547423257157360'

    def test_conversions_int(self):
        for n in self.numbers:
            for type_ in [int, long]:
                n1 = type_(n)
                mpz_n = type_(mpz(n))
                assert type(n1) == type(mpz_n)
                assert n1 == mpz_n

    def test_conversion_float(self):
        for n in self.numbers:
            n1 = float(n)
            mpz_n = float(mpz(n))
            assert type(n1) == type(mpz_n)
            assert abs(n1 - mpz_n) <= abs(n1 * sys.float_info.epsilon)

    def test_conversion_complex(self):
        for n in self.numbers:
            n1 = complex(n)
            mpz_n = complex(mpz(n))
            assert type(n1) == type(mpz_n)
            assert abs(n1.real - mpz_n.real) <= abs(n1.real * sys.float_info.epsilon) and n1.imag == mpz_n.imag

    @pytest.mark.parametrize('n', numbers)
    def test_unary_methods(self, n):
        assert mpz(-n) == -mpz(n)
        assert mpz(+n) == +mpz(n)
        assert mpz(abs(n)) == abs(mpz(n))
        assert mpz(~n) == ~mpz(n)

    @pytest.mark.parametrize('n', numbers)
    def test_bit_ops(self, n):
        assert mpz(n) & mpz(n + 1) == mpz(n & (n + 1))
        assert mpz(n) & (n + 1) == mpz(n & (n + 1))
        assert mpz(n) | mpz(n + 1) == mpz(n | (n + 1))
        assert mpz(n) | (n + 1) == mpz(n | (n + 1))
        assert mpz(n) ^ mpz(n + 1) == mpz(n ^ (n + 1))
        assert mpz(n) ^ (n + 1) == mpz(n ^ (n + 1))

    @pytest.mark.parametrize('n', numbers)
    def test_bit_rops(self, n):
        assert n & mpz(n + 1) == mpz(n & (n + 1))
        assert n | mpz(n + 1) == mpz(n | (n + 1))
        assert n ^ mpz(n + 1) == mpz(n ^ (n + 1))

    def test_index(self):
        l = range(5)
        assert l[mpz(2)] == l[2]
        assert l[mpz(-1)] == l[-1]
        with pytest.raises(IndexError):
            l[mpz(10)]

    def test_nonzero(self):
        assert mpz(23)
        assert not mpz(0)
        assert mpz(-1)

    @pytest.mark.parametrize('b', [-1, 0, 1, 1024, MAX_UI + 1])
    def test_pow_no_mod(self, b):
        if b < 0:
            for exp in [mpz(b), b]:
                with pytest.raises(ValueError) as exc:
                    mpz(2) ** exp
                assert exc.value.args == ('mpz.pow with negative exponent',)
        elif b > MAX_UI:
            for exp in [mpz(b), b]:
                with pytest.raises(ValueError) as exc:
                    mpz(2) ** exp
                assert exc.value.args == ('mpz.pow with outragous exponent',)
        else:
            res = mpz(2 ** b)
            assert mpz(2) ** mpz(b) == res
            assert mpz(2) ** b == res

    @pytest.mark.parametrize('b', [-1, 0, 1, 1024, MAX_UI + 1])
    def test_pow_with_mod(self, b):
        if b < 0:
            for exp in [mpz(b), b]:
                for mod in [mpz(7), 7]:
                    with pytest.raises(ValueError) as exc:
                        pow(mpz(2), exp, mod)
                    assert exc.value.args == ('mpz.pow with negative exponent',)
        else:
            res = mpz(pow(2, b, 7))
            assert pow(mpz(2), mpz(b), mpz(7)) == res
            assert pow(mpz(2), b, mpz(7)) == res
            assert pow(mpz(2), mpz(b), 7) == res
            assert pow(mpz(2), b, 7) == res

    @pytest.mark.parametrize('b', numbers)
    def test_rpow(self, b):
        assert b ** mpz(3) == mpz(b ** 3)

    def test_rpow_invalid(self):
        with pytest.raises(ValueError) as exc:
            1 ** mpz(-1)
        assert exc.value.args == ('mpz.pow with negative exponent',)
        with pytest.raises(ValueError) as exc:
            1 ** mpz(MAX_UI + 1)
        assert exc.value.args == ('mpz.pow with outragous exponent',)

    def test_pow_invalid(self):
        with pytest.raises(TypeError):
            mpz(2) ** 2.0
        with pytest.raises(TypeError):
            2.0 ** mpz(2)
        with pytest.raises(TypeError):
            pow(mpz(2), 2, 2.0)

    def test_mpz_mul_pypy_jit_bug(self):
        # XXX causes core dump on pypy with jit enabled
        x = mpz(1)
        for i in range(10000):    # This bug occurs randomly, so repeat
            assert x * x == x

    @pytest.mark.parametrize('n', invalids)
    def test_invalid_op(self, n):
        with pytest.raises(TypeError):
            mpz(1) - n
        with pytest.raises(TypeError):
            mpz(1) + n
        with pytest.raises(TypeError):
            mpz(1) // n
        with pytest.raises(TypeError):
            mpz(1) / n
        with pytest.raises(TypeError):
            mpz(1) % n
        with pytest.raises(TypeError):
            divmod(mpz(1), n)

    @pytest.mark.parametrize('n', invalids)
    def test_invalid_rop(self, n):
        with pytest.raises(TypeError):
            n - mpz(1)
        with pytest.raises(TypeError):
            n + mpz(1)
        with pytest.raises(TypeError):
            n // mpz(1)
        with pytest.raises(TypeError):
            n / mpz(1)
        with pytest.raises(TypeError):
            n % mpz(1)
        with pytest.raises(TypeError):
            divmod(n, mpz(1))


class TestCmp(object):
    def test_cmp_int(self):
        assert mpz(1) < 2
        assert mpz(1) <= 2
        assert mpz(2) > 1
        assert mpz(2) >= 1
        assert mpz(2) == 2
        assert mpz(1) != 2

        assert mpz(sys.maxsize - 1) < sys.maxsize
        assert mpz(sys.maxsize + 1) > sys.maxsize
        assert mpz(sys.maxsize) == sys.maxsize

        assert mpz(2*sys.maxsize - 1) < 2*sys.maxsize
        assert mpz(2*sys.maxsize + 1) > 2*sys.maxsize
        assert mpz(2*sys.maxsize) == 2*sys.maxsize

        assert mpz(4*sys.maxsize - 1) < 4*sys.maxsize
        assert mpz(4*sys.maxsize + 1) > 4*sys.maxsize
        assert mpz(4*sys.maxsize) == 4*sys.maxsize

    def test_cmp_float(self):
        assert mpz(1) > 0.5
        assert mpz(1) < 1.5
        assert mpz(1) == 1.0

    def test_cmp_mpz(self):
        assert mpz(2) > mpz(1)
        assert mpz(1) < mpz(2)
        assert mpz(2) == mpz(2)

    @pytest.mark.xfail("sys.version.startswith('2')", reason="python2 comparison")
    @pytest.mark.parametrize('n', invalids)
    def test_invalid_cmp(self, n):
        with pytest.raises(TypeError):
            mpz(1) > n
        with pytest.raises(TypeError):
            mpz(1) < n
        with pytest.raises(TypeError):
            mpz(1) >= n
        with pytest.raises(TypeError):
            mpz(1) <= n

    @pytest.mark.xfail(reason='cpython __hash__ implementation bug (feature)')
    def test_hash_neg1(self):
        assert hash(mpz(-1)) == -1

    def test_hash(self):
        assert hash(mpz(1)) == 1
        assert hash(mpz(-2)) == -2
        assert hash(mpz(sys.maxsize)) == sys.maxsize
        assert hash(mpz(sys.maxsize+1)) == -sys.maxsize - 1
