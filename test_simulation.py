import numpy as np
import networkx as nx

from simulation import Simulation
from agent import Agent


default_parameters = {
    "seed": 1,
    "size": 0,
    "length": 5,
    "issues": 4,
    "v0": 1,
    "alpha": 2
}

tests = {}


def test(test_name):
    """Return a decorator for test functions."""
    def decorator(test):
        """Decorate a test function to handle and display passage/failure."""
        def inner():
            status = "PASSED"
            try:
                test()
            except AssertionError as e:
                print(e)
                status = "FAILED"
            print(f"{test_name} test {status}")

        # add the test to the dictionary of tests for later use
        tests[test_name] = inner
        return inner

    return decorator


@test("Edge creation")
def test_edge_creation():
    sim = Simulation(default_parameters)
    sim.clear_graph()
    a, b = sim.create_agents(2)
    sim.create_edge(0, 1) # a influences b
    
    assert sim.get_followers_of(a) == [b]


@test("Message send")
def test_message_send():
    # set up the simulation to test on
    sim = Simulation(default_parameters)
    sim.clear_graph()
    a, b, c = sim.create_agents(3)
    sim.create_edge(0, 2) # a influences c
    sim.create_edge(1, 0) # b influences a
    sim.create_edge(2, 1) # c influences b

    # express belief states, synchronize, and send messages
    a_express = [-1, 1, -1, 1]
    b_express = [1, -1, 1, -1]
    c_express = [-1, -1, 1, 1]
    a.express_belief_state(a_express)
    b.express_belief_state(b_express)
    c.express_belief_state(c_express)
    sim.sync_belief_states()
    sim.send_all_messages()

    # assert feed contents equal influencer expressions
    a_feed = list(a.feed[0].message)
    b_feed = list(b.feed[0].message)
    c_feed = list(c.feed[0].message)

    assert a_feed == b_express, f"{a_feed} should equal {b_express}"
    assert b_feed == c_express, f"{b_feed} should equal {c_express}"
    assert c_feed == a_express, f"{c_feed} should equal {a_express}"


@test("Ideology summary")
def test_ideological_summary():
    sim = Simulation(default_parameters)
    sim.clear_graph()
    a = sim.create_agent()
    beliefs = (
        [1, 1, -1, 1],
        [1, -1, -1, 1],
        [1, -1, -1, -1],
        [1, -1, -1, 1]
    )
    # create a belief state history based on these beliefs
    for b in beliefs:
        a.express_belief_state(b)
        a.sync_belief_state()

    # test with multiple discount values. Expected results are hand calculated.
    # the following tuples are formatted as (discount, expected) where expected
    # is a list, not an array; thus it should be cast to an array later.
    test_cases = (
        (0.5, (0, 1.875, 1.75, 0.125, 1.875, 0, 0.5, 1.375)),
        (0.9, (0, 3.439, 2.71, 0.729, 3.439, 0, 0.9, 2.539)),
        (1.0, (0, 4, 3, 1, 4, 0, 1, 3)), # weight all equally
        (0.0, (0, 1, 1, 0, 1, 0, 0, 1)) # only weight immediate past
    )

    for discount, expected in test_cases:
        # TODO: change test cases to match normalized expectation
        actual = a.get_ideological_summary(discount, False)
        # assert, allowing for slight error in float operations
        assert abs((actual - expected).sum()) < 0.01


@test("Rewiring")
def test_rewiring():
    sim = Simulation(default_parameters)
    sim.clear_graph()
    a, b, c = sim.create_agents(3)
    sim.create_edge(0, 1)
    sim.create_edge(1, 2)
    sim.create_edge(2, 0)


if __name__ == "__main__":
    for test_fnc in tests.values():
        test_fnc()