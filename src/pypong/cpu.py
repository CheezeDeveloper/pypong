import random


class CPU(Paddle):
    """AI-controlled paddle."""

    # Import here to avoid circular imports at module level
    def __init__(self, side="right", height=5, difficulty="medium",
                 char="█", end_char=None):
        # Import Paddle at runtime
        from .paddle import Paddle as _Paddle

        # Initialize parent
        if end_char is None:
            end_char = "▐" if side == "left" else "▌"

        self.side = side
        self.height = height
        self.speed = 2
        self.char = char
        self.end_char = end_char
        self.y = 0.0
        self.x = 0
        self.up_key = None
        self.down_key = None
        self.court_width = 0
        self.court_height = 0
        self.hits = 0
        self.combo = 0

        # CPU specific
        self.difficulty = difficulty
        self._reaction_timer = 0
        self._configs = {
            "easy": {"react_every": 6, "wobble": 4.0, "chase_always": False, "speed": 1},
            "medium": {"react_every": 3, "wobble": 1.5, "chase_always": False, "speed": 2},
            "hard": {"react_every": 1, "wobble": 0.0, "chase_always": True, "speed": 2},
        }

    def setup(self, court_width, court_height):
        """Initialize CPU paddle."""
        self.court_width = court_width
        self.court_height = court_height
        if self.side == "left":
            self.x = 1
        else:
            self.x = court_width - 2
        self.y = float(court_height // 2 - self.height // 2)

    def handle_input(self, keys):
        """CPU ignores keyboard input."""
        pass

    def update(self, ball):
        """AI decision making."""
        self._reaction_timer += 1

        config = self._configs.get(self.difficulty, self._configs["medium"])

        if self._reaction_timer % config["react_every"] != 0:
            return

        target_y = ball.y
        paddle_center = self.y + self.height / 2.0

        # Add wobble for imprecision
        target_y += random.uniform(-config["wobble"], config["wobble"])

        # Only chase if ball coming toward us (or always on hard)
        should_chase = config["chase_always"]
        if self.side == "right" and ball.dx > 0:
            should_chase = True
        elif self.side == "left" and ball.dx < 0:
            should_chase = True

        if should_chase:
            diff = target_y - paddle_center
            if abs(diff) > 1:
                if diff > 0:
                    self.y = min(self.court_height - self.height, self.y + config["speed"])
                else:
                    self.y = max(0, self.y - config["speed"])
