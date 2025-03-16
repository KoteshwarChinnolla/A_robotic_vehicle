import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
from plot_img import maze_repo
from image_toMatrix import get_maze
from images_select import Select


s=Select()
path=s.display()
maze_fun = get_maze()
maze=maze_fun.maze(path[0])
maze_repo.plot_maze(maze_repo,maze=maze,FILE_NAME=path[1])