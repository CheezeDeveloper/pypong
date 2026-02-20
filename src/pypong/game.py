import sys
import os
import time

from .ball import Ball
from .paddle import Paddle
from .court import Court
from .cpu import CPU
from .collision import CollisionHandler
from .input import InputHandler


class Game:
    """Main game engine. Add paddles, ball, court and run."""

    def __init__(self, title="PyPong"):
        self.title = title
        self.paddles = []
        self.ball = None
        self.court = None
        self.cpus = []
        self.collision = CollisionHandler()
        self.input_handler = None

        # Scores
        self.scores = {}
        self.win_score = 7

        # State
        self.running = True
        self.paused = False
        self.game_over = False
        self.winner = None

        # Timing
        self.tick_rate = 0.045
        self.countdown = 0
        self.countdown_timer = 0.0

        # Sound
        self.sound_enabled = True

        # Callbacks
        self.on_hit = None
        self.on_score = None
        self.on_wall_bounce = None
        self.on_game_over = None

    def add(self, *objects):
        """Add game objects (Paddles, Ball, Court, CPU)."""
        for obj in objects:
            if isinstance(obj, CPU):
                self.paddles.append(obj)
                self.cpus.append(obj)
                self.scores[obj.side] = 0
            elif isinstance(obj, Paddle):
                self.paddles.append(obj)
                self.scores[obj.side] = 0
            elif isinstance(obj, Ball):
                self.ball = obj
            elif isinstance(obj, Court):
                self.court = obj
        return self

    def set_win_score(self, score):
        """Set points needed to win."""
        self.win_score = score
        return self

    def set_tick_rate(self, rate):
        """Set game tick rate (seconds per frame)."""
        self.tick_rate = rate
        return self

    def set_sound(self, enabled):
        """Enable or disable terminal beep sound."""
        self.sound_enabled = enabled
        return self

    def _beep(self):
        """Terminal bell sound."""
        if self.sound_enabled:
            sys.stdout.write('\a')
            sys.stdout.flush()

    def _setup(self):
        """Initialize all game objects."""
        if self.court is None:
            self.court = Court()
        if self.ball is None:
            self.ball = Ball()

        w = self.court.width
        h = self.court.height

        self.ball.setup(w, h)
        self.collision.set_bounds(h)

        for paddle in self.paddles:
            paddle.setup(w, h)

        self.input_handler = InputHandler()
        self.countdown = 3
        self.countdown_timer = time.time()

        # Hide cursor
        sys.stdout.write('\033[?25l')
        sys.stdout.flush()

    def _restart(self):
        """Restart the game."""
        for side in self.scores:
            self.scores[side] = 0
        for paddle in self.paddles:
            paddle.reset()
        self.ball.reset()
        self.game_over = False
        self.winner = None
        self.paused = False
        self.countdown = 3
        self.countdown_timer = time.time()

    def _handle_input(self, keys):
        """Process input for all paddles and game controls."""
        for key in keys:
            if key == 'q':
                self.running = False
            elif key == 'p' and not self.game_over:
                self.paused = not self.paused
            elif key == 'r':
                self._restart()

        if not self.paused and not self.game_over:
            for paddle in self.paddles:
                paddle.handle_input(keys)

    def _update(self):
        """Update game state."""
        if self.paused or self.game_over:
            return

        # Countdown
        if self.countdown > 0:
            if time.time() - self.countdown_timer >= 1.0:
                self.countdown -= 1
                self.countdown_timer = time.time()
            return

        # Update ball
        positions = self.ball.update(self.tick_rate)

        for _ in positions:
            # Wall bounces
            if self.collision.bounce_walls(self.ball):
                self._beep()
                if self.on_wall_bounce:
                    self.on_wall_bounce(self.ball)

            # Paddle collisions
            for paddle in self.paddles:
                result = self.collision.check_paddle(self.ball, paddle)

                if result == True:
                    paddle.register_hit()
                    # Reset other paddles combo
                    for other in self.paddles:
                        if other is not paddle:
                            other.reset_combo()
                    self._beep()
                    if self.on_hit:
                        self.on_hit(paddle, self.ball)

                elif result == "scored":
                    # Other side scored
                    scoring_side = "right" if paddle.side == "left" else "left"
                    self.scores[scoring_side] = self.scores.get(scoring_side, 0) + 1
                    self._beep()

                    if self.on_score:
                        self.on_score(scoring_side, self.scores)

                    # Check win
                    if self.scores[scoring_side] >= self.win_score:
                        self.game_over = True
                        self.winner = scoring_side
                        if self.on_game_over:
                            self.on_game_over(self.winner, self.scores)
                    else:
                        direction = 1 if scoring_side == "left" else -1
                        self.ball.reset(direction)
                        self.countdown = 3
                        self.countdown_timer = time.time()
                    return

        # Update CPUs
        for cpu in self.cpus:
            cpu.update(self.ball)

    def _build_frame(self):
        """Render the game as a string."""
        lines = []
        w = self.court.width
        h = self.court.height

        # Score header
        left_name = "P1"
        right_name = "P2"
        for paddle in self.paddles:
            if isinstance(paddle, CPU):
                if paddle.side == "left":
                    left_name = "CPU"
                else:
                    right_name = "CPU"

        left_score = self.scores.get("left", 0)
        right_score = self.scores.get("right", 0)
        header = f"  {left_name} [{left_score}]"
        header2 = f"[{right_score}] {right_name}"
        gap = w + 2 - len(header) - len(header2)
        lines.append(header + " " * max(gap, 1) + header2)

        # Spacer
        lines.append("")

        # Top border
        lines.append(self.court.top_border())

        # Ball position
        bx, by = self.ball.get_display_pos()
        show_ball = not self.ball.frozen or int(time.time() * 4) % 2 == 0

        # Trail positions
        trail_map = {}
        if self.ball.trail_enabled and not self.ball.frozen:
            for tx, ty, tc in self.ball.get_trail_positions():
                trail_map[(tx, ty)] = tc

        # Paddle cells
        paddle_map = {}
        for paddle in self.paddles:
            for px, py, pc in paddle.get_cells():
                paddle_map[(px, py)] = pc

        # Net x
        net_x = self.court.net_x()

        # Draw field
        for y in range(h):
            row = [self.court.row_start()]
            for x in range(w):
                drawn = False

                # Ball
                if not drawn and x == bx and y == by and show_ball:
                    row.append(self.ball.char)
                    drawn = True

                # Trail
                if not drawn and (x, y) in trail_map:
                    row.append(trail_map[(x, y)])
                    drawn = True

                # Paddles
                if not drawn and (x, y) in paddle_map:
                    row.append(paddle_map[(x, y)])
                    drawn = True

                # Net
                if not drawn and x == net_x:
                    row.append(self.court.get_net_char(y))
                    drawn = True

                if not drawn:
                    row.append(" ")

            row.append(self.court.row_end())
            lines.append("".join(row))

        # Bottom border
        lines.append(self.court.bottom_border())

        # Controls
        control_parts = []
        for paddle in self.paddles:
            if not isinstance(paddle, CPU) and paddle.up_key and paddle.down_key:
                name = "P1" if paddle.side == "left" else "P2"
                control_parts.append(f"{paddle.up_key.upper()}/{paddle.down_key.upper()}:{name}")
        control_parts.extend(["P:Pause", "Q:Quit", "R:Restart"])
        lines.append("  " + "  ".join(control_parts))

        # Status
        if self.countdown > 0:
            lines.append(f"\n          >>> Get ready... {self.countdown} <<<")
        elif self.paused:
            lines.append(f"\n          >>> PAUSED - Press P to resume <<<")
        elif self.game_over:
            winner_name = left_name if self.winner == "left" else right_name
            lines.append(f"\n          >>> {winner_name} WINS! R:Restart Q:Quit <<<")
        else:
            lines.append("")

        # Padding
        for _ in range(3):
            lines.append(" " * (w + 2))

        return "\n".join(lines)

    def run(self):
        """Start the game loop."""
        try:
            self._setup()
            os.system('cls' if os.name == 'nt' else 'clear')

            while self.running:
                start = time.time()

                keys = self.input_handler.read_keys()
                self._handle_input(keys)
                self._update()

                frame = self._build_frame()
                sys.stdout.write('\033[H')
                sys.stdout.write(frame)
                sys.stdout.flush()

                elapsed = time.time() - start
                sleep = self.tick_rate - elapsed
                if sleep > 0:
                    time.sleep(sleep)

        except KeyboardInterrupt:
            pass
        finally:
            self.input_handler.cleanup()
            sys.stdout.write('\033[?25h')
            sys.stdout.flush()
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"\n  Thanks for playing {self.title}! 🏓\n")
