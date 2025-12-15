import inspect
# TODO: probably just drop this file
class NoModuleSelectedError(Exception):
    def __init__(self):
        caller = inspect.stack()[1].function
        super().__init__(f"Operation '{caller}()': no module selected")