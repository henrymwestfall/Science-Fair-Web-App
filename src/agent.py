import time

import numpy as np

from src.message import Message


class Agent:
    def __init__(self, sim, node_id: int, name: str):
        self.parent_sim = sim
        self.node_id = node_id
        self.name = name

        self.prior_approvals = []
        self.approval = 0
        self.approval_change = 0

        # list of belief state expressions by step
        self.prior_belief_states = []
        self.prior_feeds = []

        self.expressed_belief_state = np.array([])
        self.next_expressed_belief_state = np.array([])
        self.feed = []

        self.prior_message: Message = None
        self.message: Message = None

        self.see_more = set()
        self.see_less = set()

        self.last_client_connection = 0
        self.last_client_ready_post = 0

    
    @property
    def awaiting_client(self):
        """Return whether this agent is waiting for a client connection. An 
        agent is considered waiting when it has not received any requests from
        a client for more then 2 seconds.
        """
        return time.time() - self.last_client_connection >= 2


    @property
    def ready(self):
        """Return whether this agent is flagged as ready. If the client has
        sent a POST request to mark the agent as ready within the last 2
        seconds, the agent is ready.
        """
        return time.time() - self.last_client_ready_post <= 2


    def get_feed(self) -> list:
        """Return the message feed as a JSON-friendly list."""
        return [m.to_dict() for m in self.feed]

    
    def clear_feed(self) -> None:
        self.prior_feeds.append(self.feed)
        self.feed = []

    
    def receive_message(self, message: Message) -> None:
        """Receive a message to the feed."""
        message.viewers.append(self)
        self.feed.append(message)


    def get_message(self) -> Message:
        if self.message is None:
            self.message = Message(self, np.array(self.expressed_belief_state))
        return self.message


    def clear_message(self) -> None:
        self.prior_message = self.message
        self.message = None


    def boost_influencer(self, influencer) -> None:
        """Follow an agent."""
        self.see_more.add(influencer)


    def suppress_influencer(self, influencer) -> None:
        """Unfollow an influencer based on the index of the influencer in this
        agent's list of influencers (Agent.influencers)"""
        self.see_less.add(influencer)


    def express_belief_state(self, belief_state: list) -> None:
        """Updaye the next expressed belief state based on a given list. 
        Expressed belief states are numpy arrays. This method also tells 
        the agent that there is a connected client at the time it's called.
        """
        self.next_expressed_belief_state = np.array(belief_state)
        self.last_client_ready_post = time.time()


    def sync_belief_state(self) -> None:
        """Update the actual expressed belief state. Expressed belief state
        and next expressed belief state are kept separate so that all agents
        in a simulation may be updated in parallel."""
        self.expressed_belief_state = self.next_expressed_belief_state
        self.next_expressed_belief_state = np.zeros(self.next_expressed_belief_state.shape)
        self.prior_belief_states.append(self.expressed_belief_state)

    
    def clear_influencer_change_lists(self) -> None:
        self.see_less.clear()
        self.see_more.clear()


    def get_ideological_summary(self, 
                                history_discount: float, 
                                normalize=True) -> np.ndarray:
        """
        Get a vector with a bit for each expression for each issue assume only
        2 ways to express a belief, or nonexpression. Lower discount values
        weight the immediate future more.

        TODO: rename 'history_discount'
        """
        state = np.ndarray(self.parent_sim.num_issues * 2)
        for step, expression in enumerate(reversed(self.prior_belief_states)):
            w = history_discount ** step
            for i, opinion in enumerate(expression):
                # add w to the correct bit based on opinion
                if opinion == -1:
                    state[i * 2] += w
                else:
                    state[i * 2 + 1] += w
        
        norm = np.linalg.norm(state)
        if norm == 0 or not normalize:
            return state
        else:
            return state / norm