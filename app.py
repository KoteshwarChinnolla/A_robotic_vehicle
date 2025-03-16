from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import uvicorn
import numpy as np
from PIL import Image
# from plot_img import maze_repo
from image_toMatrix import get_maze
# from images_select import Select
from astar import shortest_path
from fastapi.encoders import jsonable_encoder
import json
from agent.robot_voice import build_graph
graph=build_graph()

sp=shortest_path()
maze_fun = get_maze()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with specific allowed origins in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods, including OPTIONS
    allow_headers=["*"],  # Allow all headers
)


class image_link(BaseModel):
    image_link: str

class a_star(BaseModel):
    maze: list
    start: dict
    end: dict

class end(BaseModel):
    end: str

class text(BaseModel):
    text: str
    name: str
    id: str = "1oivb3jnjn5nhjp98jnfg90n"

class status_on(BaseModel):
    thread_id: str = "1oivb3jnjn5nhjp98jnfg90n"
    name: str

class qn_user(BaseModel):
    text: str
    user_response: str
    name: str
    id: str = "1oivb3jnjn5nhjp98jnfg90n"

class an_user(BaseModel):
    text: str
    user_response: str
    name: str
    id: str = "1oivb3jnjn5nhjp98jnfg90n"

@app.get("/")
async def read_root(request: Request):
    return {"message": "you are on the right track"}


@app.post("/plot_maze")
async def plot_maze(image_data: image_link):
    # print(image_data)
    maze = maze_fun.maze(image_data.image_link)
    # print(maze)
    if isinstance(maze, np.ndarray):
        maze = maze.tolist()  # Convert NumPy array to a list
    return {"maze": maze}

@app.post("/a_star_algo")
async def a_star_algo(a_star: a_star):
    print("+"*50)
    maze = np.array(a_star.maze) #a_star.maze
    start1 = (int(a_star.start["x"]),int(a_star.start["y"]))
    end1 = (int(a_star.end["x"]), int(a_star.end["y"]))
    print(f'start is {start1}')
    print(f'end is {end1}')
    print("+"*50)
    path, directions = sp.a_star_search(maze, start1, end1)
    return {"path": path, "directions": directions}


@app.post("/chatInput")
async def chatInput(test:text):
    response=graph.response(test.text,test.name,test.id,"starting")
    return {"response": response}

@app.post("/status_on")
async def status_on(status_on:status_on):
    response=graph.status_on(status_on.thread_id)
    return {"response": response}

@app.post("/question_for_user")
async def question_for_user(text:qn_user):
    response=graph.middle_response(text.text,"",text.name,text.id,type_="mid")
    return {"response": response}

@app.post("/user_response")
async def user_response(text:an_user):
    response=graph.middle_response(text.text,text.user_response,text.name,text.id,type_="mid")
    return {"response": response}


@app.post("/saveLastPath")
async def save_last_path(end: end):
    print("+" * 50)
    with open("lastpossition.json", "r+") as file:
        data = json.load(file)
        data["lastPosition"] = end.end
        data["current location"] = end.end
        print(data)
        file.seek(0)
        file.truncate()
        json.dump(data, file, indent=4)
    return {"message": "Last path saved"}
    # except Exception as e:
    #     print(f"Error saving last path: {e}")
    #     return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)