from pydantic import BaseModel, Field
from typing import Optional

class AgentBase(BaseModel):
    """Base model for agent data."""
    first_name: str = Field(..., description="First name of the agent")
    last_name: str = Field(..., description="Last name of the agent")
    phone_number: str = Field(..., description="Agent's phone number")
    rank: int = Field(..., description="Rank of the agent")

class AgentCreate(AgentBase):
    """Model for creating a new agent."""
    id: int = Field(..., description="Numeric unique ID for the agent")

class AgentUpdate(AgentBase):
    """Model for updating an existing agent."""
    first_name: Optional[str] = Field(None, description="Agent's first name")
    last_name: Optional[str] = Field(None, description="Agent's last name")
    phone_number: Optional[str] = Field(None, description="Agent's phone number")
    rank: Optional[str] = Field(None, description="Agent's rank")

class AgentOut(AgentBase):
    """Model for outputting agent data."""
    id: int = Field(..., description="Numeric unique ID for the agent")





