import random
import math

"""
Various behaviors to be passed as callbacks to DummyClient objects. These all 
take the visible state as a dictionary and return a list of expressed belief 
states.

In the future, they will also return a list of influencers to unfollow, but I
will implement this functionality later.

State dictionaries contain the following data:
error: Dummy agents should ignore this
int followers: the number of followers the agent has
int outDegree: the number of influencers the agent has
[(str, str)] issues: the issues in the simulation. Each string of an issue
    represents a stance. Agents should not worry about the lettering on issues;
    rather, they should treat issues as choices between -1 and 1.
[{str: str, [int], int}] messages: a list of messages sent to the agent by
    influencers. Each message contains a 'User' key, mapping to the name (str)
    of the influencer; a 'Latest Post' key, mapping to a list of integer belief 
    state expressions; and a 'Followers' key, mapping to the in-degree (int) 
    of the message author.
int step: the current step of the simulation
int readyCount: the number of agents who have signalled readiness to the server.
int size: the number of agents in the simulation.

Note that I am strongly considering replacing readyCount and size with a single
value representing the percentage of people who are ready. This would prevent
agents and humans participants from knowing the true size of a simulation.
"""


def random_behavior(state: dict, memory: dict) -> list:
    """Randomly select belief states regardless of state."""
    return [random.choice([-1, 1] for _ in state["issues"])]


def zero_intelligence(state: dict, memory: dict) -> list:
    """
    Choose the most popular belief states seen. Weight by the degree of the 
    influencer.
    """

    expression = [0 for _ in state["issues"]]
    for message in state["messages"]:
        for i, message_val in enumerate(message["Latest Post"]):
            expression[i] += message_val * message["Followers"]
    return [math.copysign(1, v) for v in expression]


def zero_intelligence_unweighted(state: dict, memory: dict) -> list:
    """
    This is exactly the same as zero_intelligence, except it does not weight
    messages by the in-degree of their authors.
    """

    expression = [0 for _ in state["issues"]]
    for message in state["messages"]:
        for i, message_val in enumerate(message["Latest Post"]):
            expression[i] += message_val
    return [math.copysign(1, v) for v in expression]