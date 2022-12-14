import itertools
import math
import random
import sys
from dataclasses import dataclass
from typing import List, Tuple

from argparse_dataclass import ArgumentParser
from colorama import init
from pyfiglet import figlet_format
from termcolor import cprint

init(strip=not sys.stdout.isatty())  # strip colors if stdout is redirected


def center_format_str(word: str, width: int) -> str:
    pad = (width - len(word))
    rpad = int(pad / 2)
    lpad = pad - rpad
    return " " * lpad + word + " " * rpad


@dataclass
class Fraction:
    numerator: int
    denominator: int

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


def lcm(a: int, b: int) -> int:
    return abs(a * b) // math.gcd(a, b)


@dataclass
class Solution:
    challenge: Challenge

    def normalize(self) -> "Challenge":
        """Returns a simpler equivalent challenge with common denominator"""
        f1, f2 = self.challenge.term1, self.challenge.term2
        den = lcm(f1.denominator, f2.denominator)
        num1 = int(f1.numerator * den / f1.denominator)
        num2 = int(f2.numerator * den / f2.denominator)
        return Challenge(Fraction(num1, den), Fraction(num2, den))

    def explain(self) -> Tuple[Challenge, Fraction, Fraction]:
        sol = self.normalize()
        f1, f2 = sol.term1, sol.term2
        assert f1.denominator == f2.denominator
        den = f1.denominator
        num = f1.numerator + f2.numerator
        raw_fraction = Fraction(num, den)
        gcd = math.gcd(num, den)
        num /= gcd
        den /= gcd
        return sol, raw_fraction, Fraction(int(num), int(den))

    def answer(self) -> Fraction:
        return self.explain()[-1]

    def format_lines(self):
        chain = [x.format_lines() for x in self.explain()]
        equals = "  =  "
        padding = " " * len(equals)
        eq_block = [padding, equals, padding]
        line_blocks = [self.challenge.format_lines()] + [x for pair in itertools.zip_longest([], chain,fillvalue=eq_block) for x in
                                                         pair]
        return ["".join(x) for x in zip(*line_blocks)]

    def __str__(self):
        return "\n".join(self.format_lines())


@dataclass
class Challenger:
    level: int

    @property
    def max_value(self) -> int:
        return 10 * self.level if self.level > 0 else 1

    def rand_numerator(self) -> int:
        return random.randint(-self.max_value, self.max_value)

    def rand_denominator(self) -> int:
        return random.randint(1, self.max_value)

    def rand_fraction(self) -> Fraction:
        return Fraction(self.rand_numerator(), self.rand_denominator())

    def challenge(self) -> Challenge:
        return Challenge(self.rand_fraction(), self.rand_fraction())


@dataclass
class MainEntryPointArgs:
    """
    This is a simple fraction addition game
    """
    level: int = 2


@dataclass
class Repl:
    args: MainEntryPointArgs
    points: int = 0
    presented_challenges: int = 0
    successful_challenges: int = 0

    def __post_init__(self):
        self.challenger = Challenger(level=self.args.level)

    @property
    def success_rate(self):
        return self.successful_challenges / self.presented_challenges if self.presented_challenges > 0 else math.nan

    def present_challenge(self) -> int:
        """
        Presents challenge
        :return: Accumulated points: positive on success, 0 on failure
        """
        print()
        cprint("-" * 60, 'magenta')
        cprint(
            f"  Nivel: {self.challenger.level} | "
            f"Puntuaci??n: {self.points} | "
            f"Efectividad: {self.success_rate * 100.0:0.0f}%",
            'magenta')
        cprint("-" * 60, 'magenta')
        input("Presiona ENTER para continuar...")
        challenge = self.challenger.challenge()
        print()
        print("Calcula:\n")
        print()
        print(challenge)
        print()
        attempts = 3
        sol = Solution(challenge)
        while attempts:
            if attempts < 3:
                print(f"Te quedan {attempts}/3 intentos")
            while True:
                try:
                    answer_raw = input("Tu respuesta [{numerador} / {denominador}]:")
                    num, den = [int(x.strip()) for x in answer_raw.strip().split('/', 2)]
                    answer = Fraction(num, den)
                    break
                except ValueError as exc:
                    print(str(exc))
                    print("Error: Formato de respuesta incorrecto. Formato esperado: {numerador} / {denominador}")

            if abs(answer.value - challenge.value) < 1e-4:
                # success
                if sol.answer() == answer:
                    cprint("??EMPINGATION!", 'grey', 'on_green')
                    break
                else:
                    cprint("Respuesta correcta pero podr??a simplificarse", 'grey', 'on_yellow')
            else:
                # error
                cprint("??Respuesta incorrecta!", 'white', 'on_red')
                attempts -= 1
        else:
            print("Intentos agotados. Soluci??n:")
            print()
            print(sol)
        return [0, 1, 5, 10][attempts]

    def run(self):
        while True:
            points = self.present_challenge()
            self.presented_challenges += 1
            self.points += points
            if points > 0:
                self.successful_challenges += 1


if __name__ == '__main__':
    ap = ArgumentParser(MainEntryPointArgs)
    args = ap.parse_args()
    cprint(figlet_format('Fractual!', font='starwars', width=120), 'grey', 'on_magenta', attrs=['bold'])
    Repl(args).run()
