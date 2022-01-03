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

        self.simulation_parameter_queue = []

        with open("parameters.json", "r") as f:
            self.default_parameters = json.load(f)

    
    def get_new_api_key_generator(self, length=6):
        used = set()
        while True:
            key = ""
            for i in range(length):
                key += chr(random.randint(65, 90))

            if not (key in used) and key != self.admin_key:
                used.add(key)
                yield key


    def start_simulation(self, params: dict) -> None:
        """
        Start a simulation with the passed parameters. Simulations do not
        execute simultaneously, so this adds the request to a queue if there
        is already an active simulation.
        """

        print(params)

        if params == None:
            params = self.default_parameters.copy()

        if self.active_simulation != None:
            self.simulation_parameter_queue.append(params)
        else:
            self.active_simulation = Simulation(params)
            for agent in self.active_simulation.agents_by_id:
                self.agents_by_key[next(self.api_key_generator)] = agent
            self.active_simulation.start()

    
    def end_simulation(self) -> None:
        """
        End the active simulation and log it as completed. Then, start the next
        simulation based on queued parameters.
        """

        self.completed_simulations.append(
            (str(datetime.now()), self.active_simulation)
        )
        self.api_key_generator = self.get_new_api_key_generator()
        self.agents_by_key = {}

        self.active_simulation = None

        # if there are queued parameters, begin simulations with them
        if len(self.simulation_parameter_queue) > 0:
            self.start_simulation(self.simulation_parameter_queue.pop(0))

    
    def get_client_api_key(self) -> str:
        """
        Get an unused api key for a client agent.
        """

        for key, agent in self.agents_by_key.items():
            if agent.awaiting_client:
                agent.last_client_connection = time.time()
                return key
    
    
    def get_state(self, key) -> str:
        """
        Get the state as seen by a given client.
        """

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


    def get_simulation_state(self) -> str:
        if self.active_simulation != None:
            return json.dumps({
                "params": self.active_simulation.params,
                "step": self.active_simulation.step,
                "ready": self.active_simulation.get_ready_agent_count(),
                "apiKeys": [(key, not agent.awaiting_client) for key, agent in self.agents_by_key.items()]
            })
        else:
            return json.dumps({"error": "No active simulation"})