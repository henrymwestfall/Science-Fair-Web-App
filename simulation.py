import time
import math
from threading import Thread

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from agent import *
from message import Message


class Simulation:
    def __init__(self, params):
        self.params = params
        if self.params["seed"] == None:
            self.rng = np.random.default_rng()
        else:
            self.rng = np.random.default_rng(self.params["seed"])

        self.agents_by_id = []
        self.size = self.params["size"]
        self.graph: nx.DiGraph = nx.fast_gnp_random_graph(self.size, 5.0 / self.size, directed=True)
        self.graphs = [self.graph.copy()]

        fake_names = self.fake_name_generator()
        for node in self.graph.nodes:
            agent = Agent(self, node, next(fake_names))
            agent.approval = self.params["v0"]
            self.agents_by_id.append(agent)

        # step specific counters
        self.idle_agents = set()

        self.length = self.params["length"]
        self.step = 0
        self.min_step_time = 10 # seconds

        # randomly generate issues as pairs of letters
        self.num_issues = min(self.params["issues"], 13)
        self.issues = []

        # capital letters, excluding vowels
        alphabet = [chr(v) for v in range(65, 91) \
            if not chr(v) in ("A", "E", "I", "O", "U", "Y")]
        issue_choices = self.rng.choice(alphabet, size=self.num_issues * 2, replace=False)
        issue = ["blank", "blank"]
        for stance in issue_choices:
            if issue[0] == "blank":
                issue[0] = stance
            elif issue[1] == "blank":
                issue[1] = stance
                self.issues.append(tuple(issue))
                issue = ["blank", "blank"]


    def start(self) -> None:
        thread = Thread(target=lambda: self.run())
        thread.daemon = True
        thread.start()


    def run(self) -> None:
        print("Starting simulation")
        for i in range(self.length):
            self.step = i
            self.process_step()
            self.graphs.append(self.graph.copy())

    
    def process_step(self) -> None:
        if self.step != 0:
            print("Updating approvals...")
            if self.step != 1: # expressed belief states don't exist yet
                self.update_approvals()
            print("Syncing belief states...")
            for agent in self.agents_by_id:
                agent.sync_belief_state()
            print("Sending messages...")
            self.send_all_messages()

            self.idle_agents.clear()
        
        # wait for agents to express belief states
        print("Waiting for clients...")
        start = time.time()
        while len(self.idle_agents) < self.size or time.time() - start < self.min_step_time:
            time.sleep(0.1)

        # rewire connections
        print("Rewiring connections...")
        for agent in self.agents_by_id:
            self.rewire(agent)


    def update_approvals(self) -> None:
        for agent in self.agents_by_id:
            followers = self.get_followers_of(agent)
            for f in followers:
                agent.approval += (f.next_expressed_belief_state == \
                    agent.expressed_belief_state).sum()


    def rewire(self, agent: Agent) -> None:
        # determine which agents can be selected as influencers and their weights
        ego_graph = nx.generators.ego.ego_graph(self.graph, agent.node_id, radius=2)
        choice_weights = {}
        possibities = []
        for node in ego_graph:
            possible_influencer = self.get_agent(node)
            if not (possible_influencer is agent or possible_influencer in agent.influencers):
                possibities.append(possible_influencer)
                a = agent.expressed_belief_state
                b = possible_influencer.expressed_belief_state
                cos_theta = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
                choice_weights[possible_influencer] = cos_theta \
                    * math.log(possible_influencer.approval, self.params["alpha"])

        # unfollow as many as possible
        n = len(possibities)
        rewire_count = len(agent.influencers_to_unfollow)
        for i in range(min(rewire_count, n)):
            self.sever_edge(agent.node_id, agent.influencers_to_unfollow[i])
        agent.influencers_to_unfollow.clear()

        # select new influeners
        for _ in range(rewire_count):
            ps = [choice_weights[possibility] / n for possibility in possibities]
            selection = self.rng.choice(possibities, ps)
            possibities.remove(selection)
            n -= 1

            self.create_edge(agent.node_id, selection.node_id)
            

    def send_all_messages(self) -> None:
        for agent in self.agents_by_id:
            for follower in self.get_followers_of(agent):
                follower.receive_message(Message(
                    agent, 
                    np.array(agent.expressed_belief_state),
                    self.get_in_degree(agent)
                    )
                )

    
    def is_idle(self, agent: Agent) -> bool:
        return agent in self.idle_agents

    
    def handle_agent_belief_expression(self, agent: Agent) -> None:
        self.idle_agents.add(agent)


    def alert_message_sent(self, agent_id):
        self.idle_agents.add(agent_id)


    def get_agent(self, agent_id: int) -> Agent:
        return self.agents_by_id[agent_id]


    def get_all_agents(self) -> list:
        return self.agents_by_id


    def get_agents_by_type(self, agent_type: int) -> list:
        return [a for a in self.agents_by_id if a.agent_type == agent_type]


    def get_followers_of(self, agent: Agent) -> list:
        return [self.get_agent(node) \
            for node in self.graph.successors(agent.node_id)]


    def get_in_degree(self, agent: Agent) -> int:
        return self.graph.in_degree(agent.node_id)

    
    def get_out_degree(self, agent: Agent) -> int:
        return self.graph.out_degree(agent.node_id)

    
    def create_edge(self, node_a: int, node_b: int) -> None:
        self.get_agent(node_a).add_influencer(self.get_agent(node_b))
        if not self.graph.has_edge(node_a, node_b):
            self.graph.add_adge(node_a, node_b)


    def sever_edge(self, node_a: int, node_b: int) -> None:
        if self.graph.has_edge(node_a, node_b):
            self.get_agent(node_a).influencers.remove(self.get_agent(node_b))
            self.graph.remove_edge(node_a, node_b)


    def fake_name_generator(self):
        possible_first_names = []
        possible_surnames = []

        with open("names/firstnames.txt") as f:
            possible_first_names = f.readlines()

        with open("names/surnames.txt") as f:
            possible_surnames = f.readlines()
        
        used_surnames = set()

        while True:
            surname = self.rng.choice(possible_surnames)
            initial = chr(self.rng.integers(65, 90, endpoint=True))

            if not surname in used_surnames:
                used_surnames.add(surname)
                yield initial + " " + surname


    def plot_graph(self):
        plt.figure(figsize=(7, 7))

        max_degree = 0
        for node in self.graph.nodes:
            max_degree = max(self.graph.in_degree(node), max_degree)
        
        colors = []
        for node in self.graph.nodes:
            a = min(1.0, self.graph.in_degree(node) / max_degree + 0.2)
            colors.append((0.53, 0.81, 0.92, a))

        nx.draw_networkx(self.graph, pos=nx.spring_layout(self.graph), node_color=colors)
        plt.show()