import numpy as np
import networkx as nx


class Network:
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
        self.rng = rng

        for i in self.nodes:
            for j in self.nodes:
                self.relation_graph[i][j]["r"] = default_edge

        self.default_edge = default_edge
        self.boosted_edge = boosted_edge
        self.suppressed_edge = suppressed_edge


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
        return nx.ego_graph(self.follow_graph, node, radius)


    def get_global_page_rank(self) -> dict:
        return nx.pagerank(self.relation_graph)

    
    def get_local_page_rank(self, center_node: int, radius: int):
        return nx.pagerank(self.ego_graph(center_node, radius))


    def get_graph_state(self) -> nx.DiGraph:
        return self.relation_graph.copy()