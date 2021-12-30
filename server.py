import random
import time
import json
from datetime import datetime

from simulation import Simulation


class Server:
    """
    A class to provide access to prior completed simulations, to set up new
    simulations, and to query the active simulation.
    """
    
    def __init__(self):
        self.admin_key = "abcdef" # will be changed in deployed version
        self.completed_simulations = []

        self.api_key_generator = self.get_new_api_key_generator()
        self.active_simulation: Simulation = None
        self.agents_by_key = {}

    
    def get_new_api_key_generator(self, length=6):
        used = set()
        while True:
            key = ""
            for i in range(length):
                key += chr(random.randint(65, 90))

            if not (key in used) and key != self.admin_key:
                used.add(key)
                yield key

    
    def end_simulation(self) -> None:
        self.completed_simulations.append(
            (str(datetime.now()), self.active_simulation)
        )
        self.active_simulation = None
        self.api_key_generator = self.get_new_api_key_generator()
        self.agents_by_key = {}

    
    def get_client_api_key(self) -> str:
        for key, agent in self.agents_by_key.items():
            if agent.awaiting_client:
                agent.awaiting_client = False
                return key
    
    
    def get_state(self, key) -> str:
        agent = self.agents_by_key.get(key)
        if agent != None:
            agent.last_client_connection = time.time()
            return json.dumps({
                "error": None,
                "followers": self.active_simulation.get_in_degree(agent),
                "outDegree": self.active_simulation.get_out_degree(agent),
                "issues": self.active_simulation.issues,
                "messages": agent.get_feed(),
                "step": self.active_simulation.step,
                "readyCount": self.active_simulation.get_ready_agent_count(),
                "size": self.active_simulation.size
            })
        else:
            return json.dumps({"error": "keyNotFound"})

    
    def send_message(self, key, message) -> str:
        agent = self.agents_by_key.get(key)
        if agent != None and message != None:
            agent.express_belief_state(message)
        return json.dumps({"error": None})


    def unfollow_influencer(self, key, influencer_id) -> str:
        agent = self.agents_by_key.get(key)
        if agent != None and influencer_id != None:
            agent.unfollow_influencer(influencer_id)
        return json.dumps({"error": None})


    def get_admin_view(self) -> str:
        return json.dumps({
            "params": self.active_simulation.params,
            "step": self.active_simulation.step,
            "ready": self.active_simulation.get_ready_agent_count(),
            "apiKey": [(key, not agent.awaiting_client) for key, agent in self.agents_by_key.items()]
        })
