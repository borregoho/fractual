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

    def explain(self) -> Tuple[Challenge, Fraction]:
        sol = self.normalize()
        f1, f2 = sol.term1, sol.term2
        assert f1.denominator == f2.denominator
        den = f1.denominator
        num = f1.numerator + f2.numerator
        gcd = math.gcd(num, den)
        num /= gcd
        den /= gcd
        return sol, Fraction(int(num), int(den))

    def format_lines(self):
        sol, res = self.explain()
        equals = "  =  "
        padding = " " * len(equals)
        return ["".join(x) for x in zip(sol.format_lines(), [padding, equals, padding], res.format_lines())]

    def __str__(self):
        return "\n".join(self.format_lines())


@dataclass
class Challenger:
    level: int

    @property
    def max_value(self) -> int:
        return 10 * self.level

    def rand_numerator(self) -> int:
        return 1
        return random.randint(-self.max_value, self.max_value)

    def rand_denominator(self) -> int:
        return 1
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
    level: int = 1


@dataclass
class Repl:
    args: MainEntryPointArgs
    points: int = 0
    presented_challenges: int = 0
    successful_challenges: int = 0

    def __post_init__(self):
        self.challenger = Challenger(level=self.args.level)

    def present_challenge(self) -> int:
        """
        Presents challenge
        :return: Accumulated points: positive on success, 0 on failure
        """
        challenge = self.challenger.challenge()
        print()
        cprint(f"Nivel: {self.challenger.level} | Puntuación: {self.points}", 'blue')
        print()
        print("Calcula:\n")
        print(challenge)
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
                break
            # error
            cprint("¡Respuesta incorrecta!", 'white', 'on_red')
            attempts -= 1
        else:
            print("Intentos agotados. Solución:")
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
