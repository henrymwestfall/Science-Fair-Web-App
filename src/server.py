import random
import string
import time
import json
from datetime import datetime
from smtplib import SMTP, SMTPAuthenticationError

from src.email_api import send_result, send_plaintext_email
from src.simulation import Simulation


class Server:
    """
    A class to provide access to prior completed simulations, to set up new
    simulations, and to query the active simulation.
    """
    
    def __init__(self):
        self.completed_simulations = []

        self.admin_key = "" # will be changed in deployed version
        self.sender_pass = ""
        self.api_key_generator = self.get_new_api_key_generator()
        self.admin_key = next(self.api_key_generator)
        self.active_simulation: Simulation = None
        self.agents_by_key = {}

        self.simulation_parameter_queue = []

        with open("parameters.json", "r") as f:
            self.default_parameters = json.load(f)


    def prompt_login(self) -> None:
        with open("password.txt") as f:
            self.sender_pass = f.read()

        valid = False
        while not valid:
            for _ in range(10):
                session = SMTP('smtp.gmail.com', 587)
                session.starttls()
                try:
                    session.login("henrywestfall.sciencefair@gmail.com", self.sender_pass)
                    valid = True
                    break
                except SMTPAuthenticationError:
                    print("Invalid password. Please try again.")
            else:
                print("You have reached the maximum number of login attempts. Try again after 10 minutes")
                time.sleep(600)

        send_plaintext_email(
            "henrymwestfall@gmail.com", 
            self.sender_pass, 
            "Admin Access Code",
            f"Admin Key: {self.admin_key}\nSetup: \
            http://localhost:5000/simulation-setup/{self.admin_key} \
            or https://science-fair-web-app.herokuapp.com/simulation-setup/{self.admin_key}"
        )

    
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

        with open("latest_results.json", "w") as f:
            json.dump(self.active_simulation.get_as_dict(), f)

        send_result(
            "henrymwestfall@gmail.com", 
            self.sender_pass, 
            "latest_results.json", 
            self.active_simulation.name + ".json"
        )

        self.api_key_generator = self.get_new_api_key_generator()
        self.agents_by_key = {}

        self.active_simulation = None

        # if there are queued parameters, begin simulations with them
        if len(self.simulation_parameter_queue) > 0:
            self.start_simulation(self.simulation_parameter_queue.pop(0))


    def set_simulation_pause(self, paused: bool) -> None:
        self.active_simulation.paused = paused

    
    def get_client_api_key(self) -> str:
        """
        Get an unused api key for a client agent.
        """

        for key, agent in self.agents_by_key.items():
            if agent.awaiting_client:
                agent.last_client_connection = time.time()
                return key
    
    
    def get_state(self, key) -> dict:
        """
        Get the state as seen by a given client.
        """

        agent = self.agents_by_key.get(key)
        if agent != None:
            agent.last_client_connection = time.time()
            return {
                "error": None,
                "likes": agent.approval,
                "likeChange": agent.approval_change,
                "outDegree": self.active_simulation.feed_size,
                "issues": self.active_simulation.issues,
                "messages": agent.get_feed(),
                "step": self.active_simulation.step,
                "readyCount": self.active_simulation.get_ready_agent_count(),
                "stepEndTime": self.active_simulation.step_end_time,
                "size": self.active_simulation.size
            }
        else:
            return {"error": "keyNotFound"}


    def receive_client_input(self, key, message, follows) -> dict:
        """
        Receive input from a client. This input should contain a message to
        send and a list of influencers to unfollow. The influencers should
        be identified by their names. (or IDs? TODO: figure this out)
        """
        self.send_message(key, message)
        self.update_relationships(key, follows)
        return {"error": None}

    
    def send_message(self, key, message):
        agent = self.agents_by_key.get(key)
        if agent != None and message != None:
            agent.express_belief_state(message)


    def unfollow_influencers(self, key, influencer_names=[]):
        agent = self.agents_by_key.get(key)
        if agent != None:
            for name in influencer_names:
                in_id = self.active_simulation.agents_by_name[name].node_id
                self.active_simulation.network.suppress_edge(agent.node_id, in_id)

    
    def follow_influencers(self, key, influencer_names=[]):
        agent = self.agents_by_key.get(key)
        if agent != None:
            for name in influencer_names:
                in_id = self.active_simulation.agents_by_name[name].node_id
                self.active_simulation.network.boost_edge(agent.node_id, in_id)


    def update_relationships(self, key: str, new_relationships: 'list[int]') -> None:
        agent = self.agents_by_key.get(key)
        if agent != None:
            self.active_simulation.update_relationships(agent, new_relationships)


    def get_simulation_state(self) -> dict:
        if self.active_simulation != None:
            agent_data = [
                [key] + self.active_simulation.get_agent_data_for_admin(agent) \
                for key, agent in self.agents_by_key.items()
            ]

            return {
                "params": self.active_simulation.params,
                "step": self.active_simulation.step,
                "paused": self.active_simulation.paused,
                "ready": self.active_simulation.get_ready_agent_count(),
                "agentData": agent_data,
                "stepEndTime": self.active_simulation.step_end_time,
                "error": None
            }
        else:
            return {"error": "No active simulation"}

    
    def get_all_data(self, end_current=False) -> list:
        if end_current:
            self.end_simulation()
        return [
            (timestamp, sim.get_as_dict()) 
            for timestamp, sim in self.completed_simulations
        ]