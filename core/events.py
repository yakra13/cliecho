class ControlEvent:
    pass

class InputClosed(ControlEvent):
    """stdin closed (Ctrl+D / Ctrl+Z)"""

class UserInterrupt(ControlEvent):
    """Ctrl+C"""

class ShutdownRequested(ControlEvent):
    """Explicit quit command"""

class RestartRequested(ControlEvent):
    """User wants to restart CLI"""

class FatalError(ControlEvent):
    def __init__(self, exc: Exception):
        self.exc = exc
