import time

import numpy as np

from message import Message


class Agent:
    def __init__(self, sim, node_id: int, name: str):
        self.parent_sim = sim
        self.node_id = node_id
        self.name = name

        self.score = 0
        self.approval = 1

        self.expressed_belief_state = np.array([])
        self.next_expressed_belief_state = np.array([])
        self.feed = []

        self.influencers = []
        self.influencers_to_unfollow = []

        self.partisan_affiliation = None

        self.last_client_connection = 0

    
    @property
    def awaiting_client(self):
        return time.time() - self.last_client_connection >= 5


    def get_feed(self) -> list:
        return [m.toDict() for m in self.feed]

    
    def receive_message(self, message: Message) -> None:
        self.feed.append(message)


    def add_influencer(self, influencer) -> None:
        if not influencer in self.influencers:
            self.influencers.append(influencer)


    def unfollow_influencer(self, influencer: int) -> None:
        self.influencers_to_unfollow.append(influencer)


    def express_belief_state(self, belief_state: list) -> None:
        self.next_expressed_belief_state = np.array(belief_state)
        self.parent_sim.handle_agent_belief_expression(self)


    def sync_belief_state(self) -> None:
        self.expressed_belief_state = self.next_expressed_belief_state
        self.next_expressed_belief_state = np.zeros(self.next_expressed_belief_state.shape)