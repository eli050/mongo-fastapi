import os
from typing import List
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from contextlib import asynccontextmanager

from dal import AgentsDAL, DALException
from models import AgentCreate, AgentUpdate, AgentOut

# Load environment variables for MongoDB connection
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_HOST = os.getenv("MONGO_HOST", "mongo-app")
MONGO_DB = os.getenv("MONGO_INITDB_DATABASE", os.getenv("MONGO_DB", "mydb"))
MONGO_USER = os.getenv("MONGO_USERNAME")
MONGO_PASS = os.getenv("MONGO_PASSWORD")

if MONGO_USER and MONGO_PASS:
    URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource={MONGO_DB}"
else:
    URI = f"mongodb://{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"

agents_dal: AgentsDAL | None = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler to initialize and clean up the DAL."""
    global agents_dal
    client = MongoClient(URI)
    try:
        agents_dal = AgentsDAL(client=client, db_name=MONGO_DB)
        yield
    finally:
        client.close()

app = FastAPI(title="Agents API", version="1.0.0", lifespan=lifespan)

@app.get("/healthz")
def healthz() -> dict:
    """Health check endpoint to verify the service is running."""
    try:
        assert agents_dal is not None
        ok = agents_dal.health_check()
        return {"status": "ok" if ok else "error"}
    except (AssertionError, DALException) as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents", response_model=AgentOut, status_code=201)
def create_agent(agent: AgentCreate) -> AgentOut:
    """Create a new agent in the database."""
    try:
        assert agents_dal is not None
        return agents_dal.create_agent(agent)
    except (AssertionError, DALException) as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/agents", response_model=List[AgentOut])
def list_agents() -> List[AgentOut]:
    """List all agents in the database."""
    try:
        assert agents_dal is not None
        return agents_dal.list_agents()
    except (AssertionError, DALException) as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/{agent_id}", response_model=AgentOut)
def get_agent(agent_id: int) -> AgentOut:
    """Fetch an agent by ID from the database."""
    try:
        assert agents_dal is not None
        agent = agents_dal.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        return agent
    except HTTPException:
        raise
    except (AssertionError, DALException) as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/agents/{agent_id}", response_model=AgentOut)
def update_agent(agent_id: int, changes: AgentUpdate) -> AgentOut:
    """Update an existing agent in the database."""
    try:
        assert agents_dal is not None
        updated = agents_dal.update_agent(agent_id, changes)
        if not updated:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        return updated
    except HTTPException:
        raise
    except (AssertionError, DALException) as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/agents/{agent_id}", status_code=204)
def delete_agent(agent_id: int) -> None:
    """Delete an agent by ID from the database."""
    try:
        assert agents_dal is not None
        deleted = agents_dal.delete_agent(agent_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
        return None
    except HTTPException:
        raise
    except (AssertionError, DALException) as e:
        raise HTTPException(status_code=500, detail=str(e))
