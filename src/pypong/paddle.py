class Paddle:
    """A player-controlled paddle."""

    def __init__(self, side="left", height=5, speed=2,
                 up_key=None, down_key=None, char="█", end_char=None):
        self.side = side
        self.height = height
        self.speed = speed
        self.char = char
        self.end_char = end_char or ("▐" if side == "left" else "▌")
        self.y = 0.0
        self.x = 0

        # Keys
        if up_key and down_key:
            self.up_key = up_key
            self.down_key = down_key
        elif side == "left":
            self.up_key = 'w'
            self.down_key = 's'
        else:
            self.up_key = 'i'
            self.down_key = 'k'

        self.court_width = 0
        self.court_height = 0

        # Stats
        self.hits = 0
        self.combo = 0

    def setup(self, court_width, court_height):
        """Initialize paddle for given court size."""
        self.court_width = court_width
        self.court_height = court_height
        if self.side == "left":
            self.x = 1
        else:
            self.x = court_width - 2
        self.y = float(court_height // 2 - self.height // 2)

    def reset(self):
        """Reset paddle to center."""
        self.y = float(self.court_height // 2 - self.height // 2)
        self.combo = 0

    def handle_input(self, keys):
        """Move paddle based on key presses."""
        for key in keys:
            if key == self.up_key:
                self.y = max(0, self.y - self.speed)
            elif key == self.down_key:
                self.y = min(self.court_height - self.height, self.y + self.speed)

    def register_hit(self):
        """Called when this paddle hits the ball."""
        self.hits += 1
        self.combo += 1

    def reset_combo(self):
        """Reset combo counter."""
        self.combo = 0

    def get_cells(self):
        """Get list of (x, y, char) for rendering."""
        cells = []
        top = int(self.y)
        for y in range(top, top + self.height):
            if y == top or y == top + self.height - 1:
                cells.append((self.x, y, self.end_char))
            else:
                cells.append((self.x, y, self.char))
        return cells
