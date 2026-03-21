# main.py
from fastapi import FastAPI
from routes import google
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import logging

print("Start")
logging.info("##### Start #####")

app = FastAPI(
    title="Wine Cellar Management API",
    description="API pour gérer utilisateurs, permissions, caves à vin et bouteilles.",
    version="1.0.0",
)

# init_db()

# CORS (dev-friendly)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restreindre en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(google.router)





# @app.on_event("startup")
# def on_startup():
#     # Create tables if not exist
#     # init_db()
#     pass


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
