"""
main chat workflows
"""
import autogen, hydra
from omegaconf import DictConfig, OmegaConf

from thought_agents.dialogue.transition import get_state_transition
from thought_agents.dialogue.agents import agent_registry
from thought_agents.dialogue.initiator import initiation_registry

from omegaconf import OmegaConf
from beartype import beartype

from thought_agents.ontology.config.dialogue import ConversationConfig, PodcastConfig # PodcastCharacters, AutogenLLMConfig, 
# from agents.ontology.chats.client import AutogenLLMConfig

@beartype
def create_podcast_group(cfg: ConversationConfig):
    initializer = autogen.UserProxyAgent(
        name="init", 
        code_execution_config=False,
    )
    # create research_agents: research_coder, executor, informer
    research_agents = agent_registry.get_class("dialogue.research")(
        cfg.llm_config, cfg.system_prompts)
    podcast_host, podcast_guests = agent_registry.get_class("podcast.characters")(cfg)
    script_parser = agent_registry.get_class("podcast.parser")(
        cfg.llm_config, cfg.system_prompts)
    # create podcast agents:  podcast_host, podcast_guests
    all_agents = [initializer] + research_agents + podcast_host + podcast_guests + script_parser
    expected_podcast_length= cfg.podcast_config.n_rounds + len(all_agents) - cfg.podcast_config.character_cfg.n_characters
    print(f"Expected podcast length: {expected_podcast_length}")
    groupchat = autogen.GroupChat(
        agents=all_agents,
        messages=[],
        max_round=expected_podcast_length,
        speaker_selection_method=get_state_transition(
            cfg.podcast_config, 
            transition="podcast.default", 
            MAX_ROUND=expected_podcast_length
        ),
    )
    return initializer, autogen.GroupChatManager(
        groupchat=groupchat, 
        llm_config=cfg.llm_config.model_dump()
    )

@beartype
def create_assessment_group(cfg: ConversationConfig, assessment_type: str = "epu.character_assessment"):
    initializer = autogen.UserProxyAgent(
        name="init", 
        code_execution_config=False,
    )
    # create research_agents: research_coder, executor, informer
    research_agents = agent_registry.get_class("dialogue.research")(
        cfg.llm_config, cfg.system_prompts)
    character_assessment_parser = agent_registry.get_class(assessment_type)(
        cfg.llm_config, cfg.system_prompts)
    all_agents = [initializer] + character_assessment_parser
    # create podcast agents:  podcast_host, podcast_guests
    groupchat = autogen.GroupChat(
        agents=all_agents, 
        max_round=len(all_agents),
        messages=[],
        speaker_selection_method=get_state_transition(
            cfg.podcast_config, 
            transition="epu.character_assessment", 
        ),
    )
    return initializer, autogen.GroupChatManager(
        groupchat=groupchat, 
        llm_config=cfg.llm_config.model_dump()
    )
    

@hydra.main(version_base=None, config_path="../../conf/dialogue", config_name="default")
def main(cfg: DictConfig) -> None:
    # Convert the OmegaConf config to the Pydantic model
    config_dict = OmegaConf.to_container(cfg, resolve=True)
    main_cfg: ConversationConfig = ConversationConfig(**config_dict)
    
    # prompts = OmegaConf.to_container(cfg.system_prompts)
    initializer, manager = create_podcast_group(main_cfg)
    # parsers
    chat_result = initiation_registry.get_class("podcast")(
        initializer, manager, 
        main_cfg.podcast_config, main_cfg.system_prompts
    )
    return chat_result.chat_history

if __name__ == "__main__":
    main()
