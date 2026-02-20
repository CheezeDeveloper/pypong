from .ball import Ball
from .paddle import Paddle
from .court import Court
from .cpu import CPU
from .game import Game


def demo():
    """Run a quick demo game."""
    game = Game()
    game.add(Paddle("left"), Paddle("right"), Ball(), Court())
    game.set_win_score(5)
    game.run()
