from os import read
from random import choice
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
        self.agents_by_name = {}
        self.size = self.params["size"]
        self.graph: nx.DiGraph = nx.scale_free_graph(self.size)
        self.graphs = [self.graph.copy()]

        self.fake_names = self.fake_name_generator()
        for node in self.graph.nodes:
            agent = Agent(self, node, next(self.fake_names))
            agent.approval = self.params["v0"]
            self.agents_by_id.append(agent)
            self.agents_by_name[agent.name] = agent

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
        """Start a new thread with the simulation running."""
        thread = Thread(target=lambda: self.run())
        thread.daemon = True
        thread.start()


    def run(self) -> None:
        """Run the simulation for a number of steps based on the length 
        attribute."""
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
            self.sync_belief_states()

            print("Clearing feeds...")
            self.clear_feeds()

            print("Sending messages...")
            self.send_all_messages()

            print("Rewiring connections...")
            for agent in self.agents_by_id:
                self.rewire(agent)

        
        # wait for agents to express belief states
        print("Waiting for clients...")
        start = time.time()
        while self.get_ready_agent_count() < self.size or time.time() - start < self.min_step_time:
            time.sleep(0.1)


    def sync_belief_states(self) -> None:
        for agent in self.agents_by_id:
            agent.sync_belief_state()


    def clear_feeds(self) -> None:
        for agent in self.agents_by_id:
            agent.feed.clear()


    def get_ready_agent_count(self) -> int:
        """Get the number of agents who are ready."""
        ready_count = 0
        for agent in self.agents_by_id:
            if agent.ready:
                ready_count += 1
        return ready_count


    def update_approvals(self) -> None:
        """Update the approvals of each agent.
        
        Approval increases by one each time a follower expresses the same
        belief as an influencer's prior belief state expression.
        """
        for agent in self.agents_by_id:
            followers = self.get_followers_of(agent)
            for f in followers:
                agent.approval += (f.next_expressed_belief_state == \
                    agent.expressed_belief_state).sum()


    def rewire(self, agent: Agent) -> None:
        """Update agent-agent connections stochastically based on similarity 
        and approval.
        
        Agents may only connect to agents who are within an ego graph with 
        radius 2. Given an agent i, each potential influencer j is assigned
        a weight equal to the product of the sum of percent similarity over
        (I) a given depth between the i and j's previously expressed belief 
        states and (II) the accumulated approval of the influencer j.
        """

    def get_new_influencer_possibilities_and_weights(self, agent: Agent) -> tuple:
        # determine which agents can be selected as influencers and their weights
        ego_graph = nx.generators.ego.ego_graph(self.graph, agent.node_id, radius=2)
        choice_weights = {}
        possibilities = []
        for node in ego_graph:
            possible_influencer = self.get_agent(node)
            if not (possible_influencer is agent or possible_influencer in agent.influencers):
                possibilities.append(possible_influencer)
                similarity = self.agent_ideology_similarity(agent, possible_influencer)
                choice_weights[possible_influencer] =  similarity * possible_influencer.approval

        return possibilities, choice_weights

    
    def unfollow_for_agent(self, agent: Agent, n: int):
        # unfollow as many as possible
        rewire_count = len(agent.influencers_to_unfollow)
        for i in range(min(rewire_count, n)):
            self.sever_edge(
                agent.node_id,
                self.agents_by_name[agent.influencers_to_unfollow[i]].node_id
            )
        agent.influencers_to_unfollow.clear()


    def select_new_influencers(self, agent: Agent, rewire_count: int, choice_weights: dict, possibilities: list, n: int):
        # select new influeners
        for _ in range(rewire_count):
            ps = [choice_weights[possibility] / n for possibility in possibilities]
            selection = self.rng.choice(possibilities, ps)
            possibilities.remove(selection)
            n -= 1

            self.create_edge(agent.node_id, selection.node_id)


    @staticmethod
    def agent_ideological_similarity_hamming(agent_a: Agent,
                                    agent_b: Agent,
                                    depth: int = 3,
                                    discount: float = 0.75) -> float:
        """
        Calculate ideological similarity using Hamming Distance.
        TODO: determine if this method is still useful, potentially remove
        """
        applied_depth = min((depth, len(agent_a.prior_belief_states)))
        similarity = 0
        for i in range(-1, -(applied_depth + 1), -1):
            a = agent_a.prior_belief_states[i]
            b = agent_b.prior_belief_states[i]
            similarity += ((a == b).sum() / a.size) * discount ** (abs(i) - 1)
        return similarity

    
    @staticmethod
    def agent_ideology_similarity(agent_a: Agent,
                                    agent_b: Agent,
                                    discount: float = 0.5) -> float:
        """
        Get the cosine similarity between the ideological summaries of two
        agents. These ideologies are normalized, so the cosine equals their
        dot product.
        """
        return np.dot(
            agent_a.get_ideological_summary(discount), 
            agent_b.get_ideological_summary(discount)
        )


    def send_all_messages(self) -> None:
        """Send expressed belief states from all influencers to their 
        followers."""
        for agent in self.agents_by_id:
            for follower in self.get_followers_of(agent):
                follower.receive_message(Message(
                    agent, 
                    np.array(agent.expressed_belief_state),
                    self.get_in_degree(agent)
                    )
                )


    def get_agent(self, agent_id: int) -> Agent:
        """Return the agent with a given id"""
        return self.agents_by_id[agent_id]


    def get_all_agents(self) -> list:
        """Return a list of all Agents in the simulation"""
        return self.agents_by_id


    def get_agents_by_type(self, agent_type: int) -> list:
        """Return all agents of a given type.
        
        TODO: check for uses and potentially remove this method and agent 
        typing"""
        return [a for a in self.agents_by_id if a.agent_type == agent_type]


    def get_followers_of(self, agent: Agent) -> list:
        """Return a list of followers for a given agent."""
        return [self.get_agent(node) \
            for node in self.graph.successors(agent.node_id)]


    def get_in_degree(self, agent: Agent) -> int:
        """Get the in degree of a given agent."""
        return self.graph.in_degree(agent.node_id)

    
    def get_out_degree(self, agent: Agent) -> int:
        """Get the out degree of a given agent."""
        return self.graph.out_degree(agent.node_id)


    def clear_graph(self) -> None:
        self.graph = nx.DiGraph()
        self.agents_by_id.clear()

    
    def create_agent(self) -> Agent:
        agent = Agent(self, len(self.agents_by_id), next(self.fake_names))
        self.agents_by_id.append(agent)
        self.graph.add_node(agent.node_id)
        return agent


    def create_agents(self, count: int) -> list:
        return [self.create_agent() for _ in range(count)]

    
    def create_edge(self, node_a: int, node_b: int) -> None:
        """
        Create an edge between nodes a and b where a influences b.
        
        node_a: the integer id of the influencer node.
        node_b: the integer id of the follower node.
        """
        self.get_agent(node_a).add_influencer(self.get_agent(node_b))
        if not self.graph.has_edge(node_a, node_b):
            self.graph.add_edge(node_a, node_b)


    def sever_edge(self, node_a: int, node_b: int) -> None:
        """
        Remove an edge between nodes a and b where a influences b.
        
        node_a: the integer id of the influencer node.
        node_b: the integer id of the follower node.
        """
        if self.graph.has_edge(node_a, node_b):
            self.get_agent(node_a).influencers.remove(self.get_agent(node_b))
            self.graph.remove_edge(node_a, node_b)


    def fake_name_generator(self):
        """Generate fake names without repetition based on the source surnames."""
        possible_surnames = []

        with open("names/surnames.txt") as f:
            possible_surnames = f.readlines()
        
        used_surnames = set()

        while True:
            surname = self.rng.choice(possible_surnames)
            initial = chr(self.rng.integers(65, 90, endpoint=True))

            if not surname in used_surnames:
                used_surnames.add(surname)
                yield initial + ". " + surname


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