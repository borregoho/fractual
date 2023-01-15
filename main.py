import math
import sys
from dataclasses import dataclass, field
from enum import Enum, auto

from argparse_dataclass import ArgumentParser
from colorama import init
from pyfiglet import figlet_format
from termcolor import cprint

from fractions import Fraction, Solution, FractionsChallenger, MixedChallenger

init(strip=not sys.stdout.isatty())  # strip colors if stdout is redirected


class Topic(Enum):
    fractions = auto()
    mixed = auto()


@dataclass
class MainEntryPointArgs:
    """
    This is a simple fraction addition game
    """
    mode: str = field(metadata={'choices': [x.name for x in Topic]}, default=Topic.mixed.name)
    level: int = 1


@dataclass
class Repl:
    args: MainEntryPointArgs
    points: int = 0
    presented_challenges: int = 0
    successful_challenges: int = 0

    def __post_init__(self):
        # dispatch based on mode
        mode = Topic[self.args.mode]
        challenger = {Topic.mixed: MixedChallenger, Topic.fractions: FractionsChallenger}[mode]
        self.challenger = challenger(level=self.args.level)

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
            f"Puntuación: {self.points} | "
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
        fraction_class = self.challenger.fraction_class
        while attempts:
            if attempts < 3:
                print(f"Te quedan {attempts}/3 intentos")
            while True:
                try:
                    answer_raw = input(f"Tu respuesta [{fraction_class.expected_format}]:")
                    answer = fraction_class.parse(answer_raw)
                    break
                except ValueError as exc:
                    print(str(exc))
                    print(f"Error: Formato de respuesta incorrecto. Formato esperado: {fraction_class.expected_format}")

            if abs(answer.value - challenge.value) < 1e-4:
                # success
                if sol.answer() == answer:
                    cprint("¡EMPINGATION!", 'grey', 'on_green')
                    break
                else:
                    cprint("Respuesta correcta pero podría simplificarse", 'grey', 'on_yellow')
            else:
                # error
                cprint("¡Respuesta incorrecta!", 'white', 'on_red')
                attempts -= 1
        else:
            print("Intentos agotados. Solución:")
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
