class Court:
    """The playing field with borders and optional net."""

    def __init__(self, width=60, height=22, border_h="═", border_v="║",
                 corner_tl="╔", corner_tr="╗", corner_bl="╚", corner_br="╝",
                 net_char="│", net_enabled=True):
        self.width = width
        self.height = height
        self.border_h = border_h
        self.border_v = border_v
        self.corner_tl = corner_tl
        self.corner_tr = corner_tr
        self.corner_bl = corner_bl
        self.corner_br = corner_br
        self.net_char = net_char
        self.net_enabled = net_enabled

    def top_border(self):
        """Return top border string."""
        return self.corner_tl + self.border_h * self.width + self.corner_tr

    def bottom_border(self):
        """Return bottom border string."""
        return self.corner_bl + self.border_h * self.width + self.corner_br

    def row_start(self):
        """Return left border character."""
        return self.border_v

    def row_end(self):
        """Return right border character."""
        return self.border_v

    def get_net_char(self, y):
        """Return net character for given row, or space if no net."""
        if not self.net_enabled:
            return " "
        if y % 2 == 0:
            return self.net_char
        return " "

    def net_x(self):
        """Return x position of net."""
        return self.width // 2
