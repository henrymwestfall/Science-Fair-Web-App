import requests
import time
import random
import json
from threading import Thread

import behaviors


class DummyClient:
    def __init__(self, url: str, key: str, behavior, wait_range=range(0)):
        """
        A dummy client to act as a human in simulations. This class manages
        interactions with the server and accepts a callback to define behavior
        in reaction to state.

        url: the root domain of the server
        key: the API key to use when interacting with the server
        behavior: a callback that defines behavior. This should accept state as
            a dictionary and should return a list of expressed belief states.
            In the future, this should also return a list of influencers to
            unfollow, but this is not yet implemented on any behaviors.
        wait_range: the maximum and minimum amounts of time the agent waits 
            between choosing its response and POSTing it. In all-dummy 
            simulations, this should be 0, hence the default value.
        """

        self.url = url
        self.key = key
        self.behavior = behavior
        self.wait_range = wait_range
        self.memory = {}

    
    def run(self):
        while True:
            state = self.get("/state")
            expressed_state = self.behavior(state, self.memory)
            # time.sleep(random.randint(self.wait_range.start, self.wait_range.stop))
            time.sleep(0.5)
            self.post("/send-actions", {
                "message": expressed_state, "follows": []
            })


    def get(self, req_url: str) -> dict:
        return json.loads(requests.get(self.url + req_url + "/" + self.key).text)

    
    def post(self, req_url: str, data: dict):
        requests.post(self.url + req_url + "/" + self.key, data={"data": json.dumps(data)})


if __name__ == "__main__":
    server_url = input("Server URL: ")
    num_clients = int(input("Number of Clients: "))
    random_seed = int(input("Seed: "))

    random.seed(random_seed)

    threads = []

    for _ in range(num_clients):
        client = DummyClient(
                server_url,
                json.loads(requests.get(server_url + "/new-apikey").text)["apiKey"],
                behaviors.zero_intelligence,
            )
        thread = Thread(target=lambda: client.run())
        thread.daemon = True
        thread.start()

        threads.append(thread)

    print("Press CTRL+C to stop")
    dead = 0
    while True:
        time.sleep(1.0)