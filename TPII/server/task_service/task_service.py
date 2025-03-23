from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TaskRequest(BaseModel):
    task_name: str
    task_params: dict

@app.get("/")
def health_check():
    return {"status": "ready"}

@app.post("/executeTask")
def execute_task(task: TaskRequest):
    result = { "task": task.task_name, "params": task.task_params, "status": "Completado" }
    return result
