import inspect
# TODO: probably just drop this file
class NoModuleError(Exception):
    def __init__(self):
        caller = inspect.stack()[1].function
        super().__init__(f"Operation '{caller}()': no module selected")

class GuardrailError(Exception):
    def __init__(self, value: str, reason: str):
        self.value: str = value
        self.reason: str = reason
        super().__init__(f"Invalid guard rail value:'{value}': {reason}")