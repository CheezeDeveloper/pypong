class CollisionHandler:
    """Handles all ball collision detection and response."""

    def __init__(self, court_top=1.0, court_bottom=None, min_dy=0.3, max_dy=0.9):
        self.court_top = court_top
        self.court_bottom = court_bottom
        self.min_dy = min_dy
        self.max_dy = max_dy

    def set_bounds(self, height):
        """Set court boundaries based on court height."""
        self.court_bottom = float(height - 2)

    def bounce_walls(self, ball):
        """Handle ball bouncing off top and bottom walls. Returns True if bounced."""
        bounced = False
        bounce_count = 0

        while (ball.y < self.court_top or ball.y > self.court_bottom) and bounce_count < 10:
            bounce_count += 1
            bounced = True
            if ball.y < self.court_top:
                ball.y = 2 * self.court_top - ball.y
                ball.dy = abs(ball.dy)
                if abs(ball.dy) < self.min_dy:
                    ball.dy = self.min_dy
            if ball.y > self.court_bottom:
                ball.y = 2 * self.court_bottom - ball.y
                ball.dy = -abs(ball.dy)
                if abs(ball.dy) < self.min_dy:
                    ball.dy = -self.min_dy

        # Hard clamp safety
        if ball.y <= self.court_top:
            ball.y = self.court_top + 0.5
            ball.dy = abs(ball.dy)
            if abs(ball.dy) < self.min_dy:
                ball.dy = self.min_dy
        if ball.y >= self.court_bottom:
            ball.y = self.court_bottom - 0.5
            ball.dy = -abs(ball.dy)
            if abs(ball.dy) < self.min_dy:
                ball.dy = -self.min_dy

        return bounced

    def check_paddle(self, ball, paddle):
        """Check if ball hits a paddle. Returns True if hit."""
        by = int(round(ball.y))
        by = max(1, by)
        paddle_top = int(paddle.y)
        paddle_bottom = paddle_top + paddle.height

        if paddle.side == "left":
            if ball.x <= paddle.x + 1 and ball.dx < 0:
                if paddle_top <= by < paddle_bottom:
                    ball.x = float(paddle.x + 2)
                    ball.dx = abs(ball.dx)
                    self._apply_spin(ball, paddle)
                    return True
                elif ball.x < 0:
                    return "scored"

        elif paddle.side == "right":
            if ball.x >= paddle.x - 1 and ball.dx > 0:
                if paddle_top <= by < paddle_bottom:
                    ball.x = float(paddle.x - 2)
                    ball.dx = -abs(ball.dx)
                    self._apply_spin(ball, paddle)
                    return True
                elif ball.x >= paddle.court_width:
                    return "scored"

        return False

    def _apply_spin(self, ball, paddle):
        """Apply spin to ball based on where it hits the paddle."""
        by = int(round(ball.y))
        center = paddle.y + paddle.height / 2.0
        offset = (by - center) / (paddle.height / 2.0)
        ball.dy = offset * 1.0

        if abs(ball.dy) < self.min_dy:
            ball.dy = self.min_dy if ball.dy >= 0 else -self.min_dy
        if ball.dy > self.max_dy:
            ball.dy = self.max_dy
        elif ball.dy < -self.max_dy:
            ball.dy = -self.max_dy

        ball.speed = min(ball.speed + ball.speed_increment, ball.max_speed)
