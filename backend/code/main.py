# main.py
from database import logger, init_db
# import database
from routes import users, tokens, permissions, cellars, bottles, admin  # import routers
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

print("Start")
logger.info("##### Start #####")

app = FastAPI(
    title="Wine Cellar Management API",
    description="API pour gérer utilisateurs, permissions, caves à vin et bouteilles.",
    version="1.0.0",
)

init_db()

# CORS (dev-friendly)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restreindre en prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(tokens.router)
app.include_router(users.router)
app.include_router(permissions.router)
app.include_router(cellars.router)
app.include_router(bottles.router)
app.include_router(admin.router)




@app.on_event("startup")
def on_startup():
    # Create tables if not exist
    init_db()
    # pass


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=True)
