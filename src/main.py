from .db import models, database
from fastapi import FastAPI
import sys

sys.path.append("..")


app = FastAPI(title="Store API")


# Server startup event
@app.on_event("startup")
def startup_event():
    models.Base.metadata.create_all(bind=database.engine)


@app.get("/")
def read_root():
    return {"Hello": "World"}
