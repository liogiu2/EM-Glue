from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI()

class Item(BaseModel):
    pddl: str

@app.get("/")
def index():
    return {"message": "Hello"}

@app.get("/changed_relation")
def get_res(item: Item):
    return item.pddl
