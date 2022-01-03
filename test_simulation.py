import numpy as np
import networkx as nx

from simulation import Simulation


default_parameters = {
    "seed": 1,
    "size": 0,
    "length": 5,
    "issues": 4,
    "v0": 1,
    "alpha": 2
}


def test(test_name):
    def decorator(test):
        def inner():
            status = "PASSED"
            try:
                test()
            except Exception as e:
                print(e)
                status = "FAILED"
            print(f"{test_name} test {status}")
        return inner
    return decorator


@test("Edge creation")
def test_edge_creation():
    sim = Simulation(default_parameters)
    sim.clear_graph()
    sim.create_agents(2)
    sim.create_edge(0, 1) # a influences b
    a, b = sim.agents_by_id # nodes 0 and 1
    
    assert sim.get_followers_of(a) == [b]


@test("Message send")
def test_message_send():
    sim = Simulation(default_parameters)
    sim.clear_graph()
    sim.create_agents(3)
    sim.create_edge(0, 2) # a influences c
    sim.create_edge(1, 0) # b influences a
    sim.create_edge(2, 1) # c influences b
    a, b, c = sim.agents_by_id # nodes 0, 1, and 2

    a_express = [-1, 1, -1, 1]
    b_express = [1, -1, 1, -1]
    c_express = [-1, -1, 1, 1]

    a.express_belief_state(a_express)
    b.express_belief_state(b_express)
    c.express_belief_state(c_express)
    sim.sync_belief_states()
    sim.send_all_messages()

    a_feed = list(a.feed[0].message)
    b_feed = list(b.feed[0].message)
    c_feed = list(c.feed[0].message)

    assert a_feed == b_express, f"{a_feed} should equal {b_express}"
    assert b_feed == c_express, f"{b_feed} should equal {c_express}"
    assert c_feed == a_express, f"{c_feed} should equal {a_express}"



if __name__ == "__main__":
    test_edge_creation()
    test_message_send()