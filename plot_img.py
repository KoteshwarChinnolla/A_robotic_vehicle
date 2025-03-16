from astar import shortest_path
import json
import numpy as np
import matplotlib.pyplot as plt
from arduino_send import send_arduino

send_arduino=send_arduino()
FILE_PATH = "lastpossition.json"
sp=shortest_path()
class maze_repo:
    def plot_maze(self,maze,FILE_NAME):

        fig, ax = plt.subplots(figsize=(10, 10))
        colored_maze = np.zeros((maze.shape[0], maze.shape[1], 3))
        # Set walls to black
        colored_maze[maze == 0] = [0, 0, 0]
        # Set passages to white
        colored_maze[maze == 1] = [1, 1, 1]
        
        ax.imshow(colored_maze)
        ax.set_xticks([]), ax.set_yticks([])

        green_cells = []
        directions_1 = []
        cid = [None]  # List to hold connection id

        with open(FILE_PATH, "r") as file:
            data=json.load(file)

        lastele=data[FILE_NAME].split(" ")
        colored_maze[int(lastele[1]), int(lastele[0])] = [1, 0, 0]
        green_cells.append((int(lastele[1]), int(lastele[0])))
        ax.imshow(colored_maze)
        plt.draw()
        
        def on_click(event):
            if event.inaxes and event.button == 1:  # Check for left mouse button
                x, y = int(event.xdata + 0.5), int(event.ydata + 0.5)  # Round to nearest integer
                if maze[y, x] == 1:  # Only allow clicking on passages
                    colored_maze[y, x] = [1, 0, 0]  # Set cell to green
                    green_cells.append((y, x))
                    ax.imshow(colored_maze)
                    plt.draw()
                    print(green_cells)
                    if len(green_cells) > 1:
                        # Find shortest path between last two green cells
                        path, directions = sp.a_star_search(maze, green_cells[-2], green_cells[-1])
                        directions_1.append(directions)
                        directions.append("left")
                        path.append((path[-1][0], path[-1][1]+1))
                        print("Path:", path)
                        print("Directions:", directions)

                        with open(FILE_PATH, "w") as file:
                            data[FILE_NAME]=str(path[-1][1])+" "+str(path[-1][0])
                            json.dump(data, file)
                        
                        cus_array=send_arduino.angles_to_send(data=directions[1:])
                        for i in range(len(path) - 1):
                            y1, x1 = path[i]
                            y2, x2 = path[i + 1]
                            # ax.plot([x1, x2], [y1, y2], color='blue', linewidth=8)
                            ax.annotate("", xy=(x2, y2), xytext=(x1, y1),arrowprops=dict(arrowstyle="fancy", color='blue', linewidth=1))
                            plt.pause(0.0005)  # Allow GUI to update
                            plt.draw()
                            
                            sent = send_arduino.decode(cus_array[i])
                            # sendtoarduino(cus_array[i])
                            # time.sleep(0.1)  # Delay for visualization
                        send_arduino.sendtoarduino('s')
                        print('stop')
                        
        cid[0] = fig.canvas.mpl_connect('button_press_event', on_click)
        plt.show()
        return directions_1