from copy import deepcopy
import random
import networkx as nx
import numpy as np


class Network:
    RANDOM = 0
    SMALL_WORLD = 1

    def __init__(self, 
                 size: int, 
                 default_edge: float, 
                 boosted_edge: float, 
                 suppressed_edge: float,
                 rng):

        self.size = size
        self.nodes = range(size)
        self.relation_graph = nx.DiGraph()
        self.follow_graph = nx.DiGraph()
        self.last_message_graph = nx.DiGraph()
        self.rng = rng

        self.relation_graph.add_nodes_from(self.nodes)
        self.follow_graph.add_nodes_from(self.nodes)

        for i in self.nodes:
            for j in self.nodes:
                self.relation_graph.add_edge(i, j, r=default_edge)

        self.default_edge = default_edge
        self.boosted_edge = boosted_edge
        self.suppressed_edge = suppressed_edge

    
    @staticmethod
    def to_array(network: 'Network') -> 'list[list[int]]':
        array = [[1 for _ in range(network.size)] for _ in range(network.size)]
        
        for i in network.nodes:
            for j in network.nodes:
                if i == j:
                    continue
                array[i][j] = network.relation_graph[i][j]["r"]

        return array


    def reset_last_message_graph(self):
        self.last_message_graph = nx.DiGraph()


    def suppress_edge(self, from_node: int, to_node: int) -> None:
        self.relation_graph[from_node][to_node]["r"] = self.suppressed_edge
        if self.follow_graph.has_edge(from_node, to_node):
            self.follow_graph.remove_edge(from_node, to_node)

    
    def boost_edge(self, from_node: int, to_node: int) -> None:
        self.relation_graph[from_node][to_node]["r"] = self.boosted_edge
        if not self.follow_graph.has_edge(from_node, to_node):
            self.follow_graph.add_edge(from_node, to_node)


    def get_relation(self, from_node: int, to_node: int) -> float:
        return self.relation_graph[from_node][to_node]["r"]


    def get_followers_of(self, node: int) -> list:
        return list(self.follow_graph.predecessors(node))


    def get_in_degree(self, node: int) -> int:
        return len(self.get_followers_of(node))


    def ego_graph(self, node: int, radius: int):
        return nx.ego_graph(self.relation_graph, node, radius)


    def get_global_page_rank(self) -> dict:
        return nx.pagerank(self.relation_graph, weight="r")

    
    def get_local_page_rank(self, center_node: int, radius: int):
        personalization = {n: 0 for n in self.relation_graph.nodes}
        personalization[center_node] = 1
        return nx.pagerank(self.relation_graph, alpha=0.7, personalization=personalization)


    def get_graph_state(self) -> nx.DiGraph:
        return Network.to_array(self)

    
    def generate_small_world(self, k: int, p: float, seed: int) -> None:
        """
        Generate a small world graph. Since edges are probabilistic, this
        means boosting edges at initialization.
        """
        
        # generate base, bidirectional graph
        self.follow_graph = nx.watts_strogatz_graph(
            self.size, k, p, seed
        ).to_directed()

        # update edge data in relationship graph
        for u in self.follow_graph.nodes:
            for v in self.follow_graph[u]:
                self.boost_edge(u, v)


    def generate_random_world(self, k: int, seed: int) -> None:
        rng = np.random.default_rng(seed=seed)

        for u in self.nodes:
            possibilities = list(self.nodes)
            possibilities.remove(u)
            v = rng.choice(possibilities, replace=False)
            self.boost_edge(u, v)


    def copy(self) -> 'Network':
        return deepcopy(self)