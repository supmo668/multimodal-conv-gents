"""
Workflows that initiates chats with agents.
"""
from typing import List, Tuple, Dict, AnyStr
from thought_agents.utils.logger import logger
from beartype import beartype
from omegaconf import DictConfig

import autogen

from thought_agents.utils.registry import initiation_registry

from thought_agents.ontology.config.dialogue import PodcastConfig, PodcastCharacters

@initiation_registry.register(name="podcast")
def create_podcast(
  initializer: autogen.AssistantAgent, 
  manager: autogen.GroupChatManager,
  podcast_cfg: PodcastConfig,
  system_prompts: str
  
  ) -> List[AnyStr]:
  expected_podcast_length = podcast_cfg.length + len(manager.groupchat.agents) - podcast_cfg.character_cfg.n_characters
  logger.info(f"Expected podcast length: {expected_podcast_length}")
  print(f"Expected podcast length: {expected_podcast_length}")
  return initializer.initiate_chat(
    manager, 
    message=system_prompts['podcast']["initiation"].format(
      characters=",".join(podcast_cfg.character_cfg.guest_names),
      topic=podcast_cfg.topic,
      # length of the actual podcast = settings rounds + no. of research rounds
      # no. of research rounds = len(all agents) - no. of characters
      length = expected_podcast_length
      )
  )
  
@initiation_registry.register(name="epu-assessment")
def create_assessment(
  initializer: autogen.AssistantAgent, 
  manager: autogen.GroupChatManager,
  podcast_cfg: PodcastConfig,
  system_prompts: str,
  **kwargs
  ) -> List[AnyStr]:
  """
  parameters:
    kwargs: 
      conversation: copy of convesration
  """
  return initializer.initiate_chat(
    manager, 
    message=system_prompts['epu']["initiation"].format(
      characters=",".join(
        podcast_cfg.character_cfg.guest_names),
      conversation = kwargs['conversation']
      )
  )