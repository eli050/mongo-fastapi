from typing import List, Optional, Any
from collections.abc import Mapping
from pymongo import MongoClient, ASCENDING, ReturnDocument
from pymongo.collection import Collection
from pymongo.errors import PyMongoError, DuplicateKeyError

from models import AgentCreate, AgentUpdate, AgentOut


class DALException(Exception):
    """Custom exception for Data Access Layer errors."""
    pass


class AgentsDAL:
    """Data Access Layer for managing agents in MongoDB."""
    def __init__(self, client: MongoClient, db_name: str, collection_name: str = "agents") -> None:
        try:
            self.client = client
            self.db = client[db_name]
            self.collection: Collection = self.db[collection_name]
            self.collection.create_index([("id", ASCENDING)], name="uniq_agent_id", unique=True)
        except PyMongoError as e:
            raise DALException(f"Failed to initialize AgentsDAL: {e}") from e

    @staticmethod
    def _to_agent_out(doc: Mapping[str, Any]) -> AgentOut:
        """Convert a MongoDB document to an AgentOut model."""
        return AgentOut(
            id=int(doc["id"]),
            first_name=doc["first_name"],
            last_name=doc["last_name"],
            phone_number=doc["phone_number"],
            rank=int(doc["rank"]),
        )

    def create_agent(self, payload: AgentCreate) -> AgentOut:
        """Create a new agent in the database."""
        try:
            doc = payload.model_dump()
            self.collection.insert_one(doc)
            return self._to_agent_out(doc)
        except DuplicateKeyError as e:
            raise DALException(f"Agent with id {payload.id} already exists.") from e
        except PyMongoError as e:
            raise DALException(f"Failed to create agent: {e}") from e

    def get_agent(self, agent_id: int) -> Optional[AgentOut]:
        """Fetch an agent by ID from the database."""
        try:
            doc = self.collection.find_one({"id": agent_id})
            return self._to_agent_out(doc) if doc else None
        except PyMongoError as e:
            raise DALException(f"Failed to fetch agent {agent_id}: {e}") from e

    def list_agents(self) -> List[AgentOut]:
        """List all agents in the database."""
        try:
            return [self._to_agent_out(doc) for doc in self.collection.find({}).sort("id", ASCENDING)]
        except PyMongoError as e:
            raise DALException(f"Failed to list agents: {e}") from e

    def update_agent(self, agent_id: int, changes: AgentUpdate) -> Optional[AgentOut]:
        """Update an existing agent's details."""
        try:
            update_doc = {k: v for k, v in changes.model_dump(exclude_unset=True).items()}
            result = self.collection.find_one_and_update(
                {"id": agent_id}, {"$set": update_doc}, return_document=ReturnDocument.AFTER
            )
            return self._to_agent_out(result) if result else None
        except PyMongoError as e:
            raise DALException(f"Failed to update agent {agent_id}: {e}") from e

    def delete_agent(self, agent_id: int) -> bool:
        """Delete an agent by ID from the database."""
        try:
            res = self.collection.delete_one({"id": agent_id})
            return res.deleted_count == 1
        except PyMongoError as e:
            raise DALException(f"Failed to delete agent {agent_id}: {e}") from e

    def health_check(self) -> bool:
        """Perform a health check on the database connection."""
        try:
            self.client.admin.command("ping")
            return True
        except PyMongoError as e:
            raise DALException(f"Health check failed: {e}") from e
