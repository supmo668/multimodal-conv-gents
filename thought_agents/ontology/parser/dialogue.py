from typing import List, Dict
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser

from thought_agents.ontology.config.dialogue import Person, name_field

class Dialogue(BaseModel):
    speaker: str = name_field
    dialogue: str = Field(
        ..., description="your dialogue to the current conversation")
    inner_thought: str = Field(
        ..., description="your inner thought up to the current conversation")

class DialogueParticipants(BaseModel):
    hosts: List[Person] = Field(
        ..., description="host of the podcast")
    guests: List[Person] = Field(
        ..., description="list of guests of the podcast")
    
class Podcast(BaseModel):
    title: str = Field(..., description="Title of the podcast")
    abstract: str = Field(..., description="Abstract of the podcast")
    participants: DialogueParticipants = Field(
        ..., description="Participants of the podcast")
    dialogues: List[Dialogue] = Field(
        ..., description="Script of dialogues that took palce in the podcast")
    
podcast_parser = PydanticOutputParser(pydantic_object=Podcast)
dialogue_parser = PydanticOutputParser(pydantic_object=Dialogue)