import sys
import os

WINDOWS = os.name == 'nt'

if WINDOWS:
    import msvcrt
else:
    import tty
    import termios
    import select


class InputHandler:
    """Cross-platform non-blocking keyboard input."""

    def __init__(self):
        self._original_settings = None
        if not WINDOWS:
            self._original_settings = termios.tcgetattr(sys.stdin)
            tty.setcbreak(sys.stdin.fileno())

    def get_key(self):
        """Read a single key without blocking. Returns None if no key pressed."""
        if WINDOWS:
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                if ch in (b'\x00', b'\xe0'):
                    msvcrt.getch()
                    return None
                try:
                    return ch.decode('utf-8').lower()
                except:
                    return None
            return None
        else:
            if select.select([sys.stdin], [], [], 0)[0]:
                ch = sys.stdin.read(1)
                return ch.lower()
            return None

    def read_keys(self, max_keys=15):
        """Read all available keys. Returns list of key characters."""
        keys = []
        for _ in range(max_keys):
            key = self.get_key()
            if key is None:
                break
            keys.append(key)
        return keys

    def cleanup(self):
        """Restore terminal to original state."""
        if not WINDOWS and self._original_settings:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._original_settings)
