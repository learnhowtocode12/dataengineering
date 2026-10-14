"""
Graph - a set of vertices connected by edges, stored as an adjacency list.
Demonstrates BFS, DFS, and Dijkstra's shortest path on a weighted graph.
"""

import heapq
from collections import deque


class Graph:
    def __init__(self, directed=False):
        self._adjacency = {}
        self.directed = directed

    def add_edge(self, u, v, weight=1):
        self._adjacency.setdefault(u, []).append((v, weight))
        if not self.directed:
            self._adjacency.setdefault(v, []).append((u, weight))
        else:
            self._adjacency.setdefault(v, [])

    def bfs(self, start):
        visited = {start}
        order = []
        queue = deque([start])
        while queue:
            node = queue.popleft()
            order.append(node)
            for neighbor, _ in self._adjacency.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return order

    def dfs(self, start):
        visited = set()
        order = []

        def _dfs(node):
            visited.add(node)
            order.append(node)
            for neighbor, _ in self._adjacency.get(node, []):
                if neighbor not in visited:
                    _dfs(neighbor)

        _dfs(start)
        return order

    def dijkstra(self, start):
        """Shortest distance from start to every reachable vertex."""
        distances = {start: 0}
        visited = set()
        min_heap = [(0, start)]

        while min_heap:
            dist, node = heapq.heappop(min_heap)
            if node in visited:
                continue
            visited.add(node)
            for neighbor, weight in self._adjacency.get(node, []):
                new_dist = dist + weight
                if new_dist < distances.get(neighbor, float("inf")):
                    distances[neighbor] = new_dist
                    heapq.heappush(min_heap, (new_dist, neighbor))

        return distances


def main():
    graph = Graph()
    for u, v, w in [(1, 2, 4), (1, 3, 1), (2, 4, 1), (3, 4, 5), (4, 5, 3)]:
        graph.add_edge(u, v, w)

    print("BFS from 1:", graph.bfs(1))
    print("DFS from 1:", graph.dfs(1))
    print("Dijkstra shortest distances from 1:", graph.dijkstra(1))


if __name__ == "__main__":
    main()
