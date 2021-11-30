from math import exp
import requests
import time
import random
import json
from threading import Thread


class DummyClient:
    def __init__(self, url, key: str):
        self.url = url
        self.key = key

    
    def run(self):
        state = self.get("/state")
        expressed_state = [random.choice([-1, 1]) for _ in state["issues"]]
        self.post("/send-message", {"message": expressed_state})


    def get(self, req_url: str) -> dict:
        return json.loads(requests.get(self.url + req_url + "/" + self.key).text)

    
    def post(self, req_url: str, data: dict):
        requests.post(self.url + req_url + "/" + self.key, data={"data": json.dumps(data)})


if __name__ == "__main__":
    server_url = "http://localhost:5000"#input("Server URL: ")
    num_clients = 24#int(input("Number of Clients: "))
    random_seed = 42#int(input("Seed: "))

    random.seed(random_seed)

    threads = []

    for _ in range(num_clients):
        client = DummyClient(
                server_url,
                json.loads(requests.get(server_url + "/new-apikey").text)["apiKey"]
            )
        thread = Thread(target=lambda: client.run())
        thread.daemon = True
        thread.start()

        threads.append(thread)

    print("Press CTRL+C to stop")
    dead = 0
    while True:
        time.sleep(1.0)