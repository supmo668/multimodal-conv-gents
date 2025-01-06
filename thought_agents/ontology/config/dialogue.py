from hydra.core.config_store import ConfigStore
from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict

from pydantic import BaseModel, Field
from thought_agents.ontology.chats.client import AutogenLLMConfig

name_field = Field(..., description="name of the person")

class Person(BaseModel):
    name: str = name_field
    sex: Optional[str] = Field(None, description="sex of the person")
    description: str = Field(..., description="A description of the person if known, otherwise just a generic character.")

class PodcastCharacters(BaseModel):
    hosts: List[Person] = Field(..., description="host of the podcast")
    guests: List[Person] = Field(..., description="list of guests of the podcast")

    @property
    def guest_names(self) -> List[str]:
        return [guest.name for guest in self.guests]
    @property
    def host_names(self) -> List[str]:
        return [host.name for host in self.hosts]
    @property
    def n_characters(self) -> int:
        return len(self.hosts) + len(self.guests)

class PodcastConfig(BaseModel):
    topic: str = Field(default="Natural Conversation", description="topic of the podcast")
    n_rounds: int = Field(default=5, description="number of talking rounds in the podcast")
    length: int = Field(default=10, description="length of the podcast in minutes")
    character_cfg: PodcastCharacters = None
    

class ConversationConfig(BaseModel):
    llm_config: AutogenLLMConfig
    podcast_config: PodcastConfig
    system_prompts: Dict[str, Dict | str]
    
# Register the configuration with ConfigStore
# cs = ConfigStore.instance()
# cs.store(name="podcast_base", node=PodcastConfig)

