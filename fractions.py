import dataclasses
import itertools
import math
import random
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class Fraction:
    numerator: int
    denominator: int

    expected_format = '{numerador} / {denominador}'

    @property
    def value(self) -> float:
        return self.numerator / self.denominator

    def format_lines(self, add_plus: bool = False) -> List[str]:
        padding = 4
        numbers = [str(abs(n)) for n in [self.numerator, self.denominator]]
        width = max(len(num) for num in numbers) + padding
        sign = '  -  ' if self.value < 0 else '  +  ' if add_plus else ''
        l1, l3 = [" " * len(sign) + center_format_str(num, width) for num in numbers]
        l2 = sign + '_' * width
        lines = [l1, l2, l3]
        return lines

    @classmethod
    def parse(cls, raw_str: str) -> "Fraction":
        num, den = [int(x.strip()) for x in raw_str.strip().split('/', 2)]
        return cls(num, den)


@dataclass
class MixedFraction(Fraction):
    expected_format = '[-]{entero} {numerador}/{denominador}'

    def format_lines(self, add_plus: bool = False) -> List[str]:
        numerator, denominator = abs(self.numerator), abs(self.denominator)
        integer = numerator // denominator
        numerator = numerator % denominator

        sign = ' - ' if self.value < 0 else ' + ' if add_plus else ''
        l1 = sign
        if integer > 0:
            l1 += f"{integer} "
        if numerator > 0:
            l1 += f"{numerator}/{denominator}"
        lines = [l1]
        return lines

    @classmethod
    def parse(cls, raw_str: str) -> "MixedFraction":
        raw_str = raw_str.strip()
        try:
            whole = int(raw_str)
            return cls(whole, 1)
        except ValueError:
            pass
        try:
            frac = Fraction.parse(raw_str)
            return cls(frac.numerator, frac.denominator)
        except ValueError:
            pass
        raw_int, raw_frac = raw_str.split(' ', 1)
        integer = int(raw_int)
        sign = -1 if integer < 0 else 1
        frac = Fraction.parse(raw_frac)
        return cls(integer * frac.denominator + sign * frac.numerator, frac.denominator)


@dataclass
class Challenge:
    term1: Fraction
    term2: Fraction

    def format_lines(self):
        f1, f2 = self.term1, self.term2
        left = f1.format_lines()
        right = f2.format_lines(add_plus=True)
        return [x + y for x, y in zip(left, right)]

    def __str__(self):
        return "\n".join(self.format_lines())

    @property
    def value(self) -> float:
        return self.term1.value + self.term2.value


@dataclass
class Solution:
    challenge: Challenge

    def normalize(self) -> "Challenge":
        """Returns a simpler equivalent challenge with common denominator"""
        f1, f2 = self.challenge.term1, self.challenge.term2
        den = lcm(f1.denominator, f2.denominator)
        num1 = int(f1.numerator * den / f1.denominator)
        num2 = int(f2.numerator * den / f2.denominator)
        return Challenge(
            dataclasses.replace(self.challenge.term1, numerator=num1, denominator=den),
            dataclasses.replace(self.challenge.term2, numerator=num2, denominator=den),
        )

    def explain(self) -> Tuple[Challenge, Fraction, Fraction]:
        fraction_cls = self.challenge.term1.__class__
        sol = self.normalize()
        f1, f2 = sol.term1, sol.term2
        assert f1.denominator == f2.denominator
        den = f1.denominator
        num = f1.numerator + f2.numerator
        raw_fraction = fraction_cls(num, den)
        gcd = math.gcd(num, den)
        num /= gcd
        den /= gcd
        return sol, raw_fraction, fraction_cls(int(num), int(den))

    def answer(self) -> Fraction:
        return self.explain()[-1]

    def format_lines(self):
        chain = [x.format_lines() for x in self.explain()]
        equals = "  =  "
        padding = " " * len(equals)
        lines = len(chain[0])
        eq_block = [padding] * ((lines - 1) // 2) + [equals] + [padding] * (lines // 2)
        line_blocks = [self.challenge.format_lines()] + [x for pair in
                                                         itertools.zip_longest([], chain, fillvalue=eq_block) for x in
                                                         pair]
        return ["".join(x) for x in zip(*line_blocks)]

    def __str__(self):
        return "\n".join(self.format_lines())


def lcm(a: int, b: int) -> int:
    return abs(a * b) // math.gcd(a, b)


@dataclass
class FractionsChallenger:
    level: int
    fraction_class = Fraction

    @property
    def max_value(self) -> int:
        return 10 * self.level if self.level > 0 else 1

    def rand_numerator(self) -> int:
        return random.randint(-self.max_value, self.max_value)

    def rand_denominator(self) -> int:
        return random.randint(1, self.max_value)

    def rand_fraction(self) -> Fraction:
        return self.fraction_class(self.rand_numerator(), self.rand_denominator())

    def challenge(self) -> Challenge:
        return Challenge(self.rand_fraction(), self.rand_fraction())


@dataclass
class MixedChallenger(FractionsChallenger):
    fraction_class = MixedFraction


def center_format_str(word: str, width: int) -> str:
    pad = (width - len(word))
    rpad = int(pad / 2)
    lpad = pad - rpad
    return " " * lpad + word + " " * rpad
