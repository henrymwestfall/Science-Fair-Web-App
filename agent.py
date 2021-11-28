import numpy as np

class Agent:
    def __init__(self, sim, node_id: int):
        self.parent_sim = sim
        self.node_id = node_id

        self.score = 0
        self.approval = 1

        self.expressed_belief_state = []
        self.next_expressed_belief_state = []
        self.feed = []

        self.influencers = []
        self.influencers_to_unfollow = []

        self.partisan_affiliation = None

        self.awaiting_client = True

    
    def get_feed(self):
        return self.feed

    
    def receive_message(self, message: np.ndarray) -> None:
        self.feed.append(list(message))


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
        self.next_expressed_belief_state.clear()