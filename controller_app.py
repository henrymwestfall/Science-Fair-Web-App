# run this on my computer

import time
import requests

from src.simulation import *
from src.server import *

server = Server()
print(f"Admin key: {server.admin_key}")



get_requests = {}

def route(name: str, method: str):
    def decorator(fnc):
        if method == "GET":
            get_requests[name] = fnc
        return fnc
    return decorator


