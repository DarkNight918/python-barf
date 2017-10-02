# Copyright (c) 2013, Felipe Andres Manzano
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     * Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice,this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the copyright holder nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED CVC, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.


class Symbol(object):

    def __init__(self, value, *children):
        assert type(value) in [int, long, str, bool]
        assert all([isinstance(x, Symbol) for x in children])

        if len(children) > 0:
            self._value = '(' + str(value) + ' ' + ' '.join(map(str, children)) + ')'
        else:
            self._value = str(value)

    def __getstate__(self):
        state = {
            'value': self.value
        }

        return state

    def __setstate__(self, state):
        self._value = state['value']

    @property
    def value(self):
        return self._value

    def __str__(self):
        return str(self._value)


class BitVec(Symbol):
    """A symbolic bit vector"""

    def __init__(self, size, value, *children):
        super(BitVec, self).__init__(value, *children)

        self.size = size

    def __getstate__(self):
        state = super(BitVec, self).__getstate__()
        state['size'] = self.size

        return state

    def __setstate__(self, state):
        super(BitVec, self).__setstate__(state)

        self.size = state['size']

    @property
    def declaration(self):
        return '(declare-fun %s () (_ BitVec %d))' % (self.value, self.size)

    # Arithmetic operators
    def __add__(self, other):
        return BitVec(self.size, 'bvadd', self, cast_to_bitvec(other, self.size))

    def __sub__(self, other):
        return BitVec(self.size, 'bvsub', self, cast_to_bitvec(other, self.size))

    def __mul__(self, other):
        return BitVec(self.size, 'bvmul', self, cast_to_bitvec(other, self.size))

    def __div__(self, other):
        return BitVec(self.size, 'bvsdiv', self, cast_to_bitvec(other, self.size))

    def __truediv__(self, other):
        return BitVec(self.size, 'bvsdiv', self, cast_to_bitvec(other, self.size))

    def __mod__(self, other):
        return BitVec(self.size, 'bvsmod', self, cast_to_bitvec(other, self.size))

    # Bitwise operators
    def __and__(self, other):
        return BitVec(self.size, 'bvand', self, cast_to_bitvec(other, self.size))

    def __xor__(self, other):
        return BitVec(self.size, 'bvxor', self, cast_to_bitvec(other, self.size))

    def __or__(self, other):
        return BitVec(self.size, 'bvor', self, cast_to_bitvec(other, self.size))

    def __lshift__(self, other):
        return BitVec(self.size, 'bvshl', self, cast_to_bitvec(other, self.size))

    def __rshift__(self, other):
        return BitVec(self.size, 'bvlshr', self, cast_to_bitvec(other, self.size))

    def __invert__(self):
        return BitVec(self.size, 'bvnot', self)

    # Reverse arithmetic operators
    def __radd__(self, other):
        return BitVec(self.size, 'bvadd', cast_to_bitvec(other, self.size), self)

    def __rsub__(self, other):
        return BitVec(self.size, 'bvsub', cast_to_bitvec(other, self.size), self)

    def __rmul__(self, other):
        return BitVec(self.size, 'bvmul', self, cast_to_bitvec(other, self.size))

    def __rdiv__(self, other):
        return BitVec(self.size, 'bvsdiv', cast_to_bitvec(other, self.size), self)

    def __rtruediv__(self, other):
        return BitVec(self.size, 'bvsdiv', cast_to_bitvec(other, self.size), self)

    def __rmod__(self, other):
        return BitVec(self.size, 'bvmod', cast_to_bitvec(other, self.size), self)

    # Reverse bitwise operators
    def __rand__(self, other):
        return BitVec(self.size, 'bvand', self, cast_to_bitvec(other, self.size))

    def __rxor__(self, other):
        return BitVec(self.size, 'bvxor', self, cast_to_bitvec(other, self.size))

    def __ror__(self, other):
        return BitVec(self.size, 'bvor', self, cast_to_bitvec(other, self.size))

    def __rlshift__(self, other):
        return BitVec(self.size, 'bvshl', cast_to_bitvec(other, self.size), self)

    def __rrshift__(self, other):
        return BitVec(self.size, 'bvlshr', cast_to_bitvec(other, self.size), self)

    # Comparison operators (signed)
    def __lt__(self, other):
        return Bool('bvslt', self, cast_to_bitvec(other, self.size))

    def __le__(self, other):
        return Bool('bvsle', self, cast_to_bitvec(other, self.size))

    def __eq__(self, other):
        return Bool('=', self, cast_to_bitvec(other, self.size))

    def __ne__(self, other):
        return Bool('not', self == other)

    def __gt__(self, other):
        return Bool('bvsgt', self, cast_to_bitvec(other, self.size))

    def __ge__(self, other):
        return Bool('bvsge', self, cast_to_bitvec(other, self.size))

    def __neg__(self):
        return BitVec(self.size, 'bvneg', self)

    # Comparison operators (unsigned)
    def ult(self, other):
        return Bool('bvult', self, cast_to_bitvec(other, self.size))

    def ule(self, other):
        return Bool('bvule', self, cast_to_bitvec(other, self.size))

    def ugt(self, other):
        return Bool('bvugt', self, cast_to_bitvec(other, self.size))

    def uge(self, other):
        return Bool('bvuge', self, cast_to_bitvec(other, self.size))

    # Arithmetic operators (unsigned)
    def udiv(self, other):
        return BitVec(self.size, 'bvudiv', self, cast_to_bitvec(other, self.size))

    def urem(self, other):
        return BitVec(self.size, 'bvurem', self, cast_to_bitvec(other, self.size))

    # Reverse arithmetic operators (unsigned)
    def rudiv(self, other):
        return BitVec(self.size, 'bvudiv', cast_to_bitvec(other, self.size), self)

    def rurem(self, other):
        return BitVec(self.size, 'bvurem', cast_to_bitvec(other, self.size), self)

    # TODO __mod__ and smod use the same smtlib operator, which one is the correct one?
    def smod(self, other):
        return BitVec(self.size, 'bvsmod', cast_to_bitvec(other, self.size), self)


class Bool(Symbol):
    """A symbolic bool"""

    def __init__(self, value, *children):
        super(Bool, self).__init__(value, *children)

    @property
    def declaration(self):
        return '(declare-fun %s () Bool)' % self.value

    # Comparison operators
    def __eq__(self, other):
        return Bool('=', self, cast_to_bool(other))

    def __ne__(self, other):
        return Bool('not', self == other)

    # Logical operators
    def __and__(self, other):
        return Bool('and', self, cast_to_bool(other))

    def __or__(self, other):
        return Bool('or', self, cast_to_bool(other))

    def __xor__(self, other):
        return Bool('xor', self, cast_to_bool(other))

    def __invert__(self):
        return Bool('not', self)

    # Reverse logical operators
    def __rand__(self, other):
        return Bool('and', self, cast_to_bool(other))

    def __ror__(self, other):
        return Bool('or', self, cast_to_bool(other))

    def __rxor__(self, other):
        return Bool('xor', self, cast_to_bool(other))


def cast_to_bool(value):
    if type(value) in (int, long, bool):
        value = Bool(str(bool(value)).lower())

    assert type(value) == Bool

    return value


def cast_to_bitvec(value, size):
    if type(value) in (int, long):
        value = cast_int(value, size)
    elif type(value) is str:
        assert len(value) == 1

        value = cast_char(value, size)
    elif type(value) is BitVec:
        assert value.size == size
    else:
        raise Exception("Invalid value type.")

    assert type(value) == BitVec

    return value


def cast_int(value, size):
    if size == 1:
        return BitVec(size, '#' + bin(value & 1)[1:])
    else:
        return BitVec(size, '#x%0*x' % (size / 4, truncate_int(value, size)))


def cast_char(value, size):
    return cast_int(ord(value), size)


def truncate_int(value, size):
    return value & ((1 << size) - 1)
