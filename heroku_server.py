import time

class HerokuServer:
    """
    A class with the same methods as src.server.Server that stores calls rather
    than executes them.
    """

    def __init__(self):
        self.recent_method_calls = {}

    
    def call(self, method: str, params: dict):
        self.recent_method_calls[time.time()] = method, params


    def get_recent_calls(self) -> dict:
        temp = self.recent_method_calls
        self.recent_method_calls = {}
        return temp
