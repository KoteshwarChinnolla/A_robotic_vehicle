import matplotlib.pyplot as plt
import numpy as np
import heapq
import serial
import time
from PIL import Image
class shortest_path:
    def a_star_search(self,maze, start, end):
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        neighbors = [(0, 1), (1, 0), (0, -1), (-1, 0) ,(1,-1),(-1,1),(1,1),(-1,-1)]
        directions = ["left", "down", "right", "up","right-down","left-up","left-down","right-up"]
        close_set = set()
        came_from = {}
        gscore = {start: 0}
        fscore = {start: heuristic(start, end)}
        oheap = []

        heapq.heappush(oheap, (fscore[start], start))

        while oheap:
            current = heapq.heappop(oheap)[1]

            if current == end:
                data = []
                dir_data = []
                while current in came_from:
                    direction, prev = came_from[current]
                    data.append(current)
                    dir_data.append(direction)
                    current = prev
                data.append(start)
                dir_data.append(None)  # No direction for the start
                return data[::-1], dir_data[::-1]  # Return reversed path and directions

            close_set.add(current)
            for idx, (i, j) in enumerate(neighbors):
                neighbor = current[0] + i, current[1] + j
                tentative_g_score = gscore[current] + 1

                if 0 <= neighbor[0] < maze.shape[0]:
                    if 0 <= neighbor[1] < maze.shape[1]:
                        if maze[neighbor[0]][neighbor[1]] == 0:
                            continue
                    else:
                        # neighbor is out of bounds
                        continue
                else:
                    # neighbor is out of bounds
                    continue

                if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, 0):
                    continue

                if tentative_g_score < gscore.get(neighbor, 0) or neighbor not in [i[1] for i in oheap]:
                    came_from[neighbor] = (directions[idx], current)
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + heuristic(neighbor, end)
                    heapq.heappush(oheap, (fscore[neighbor], neighbor))

        return False