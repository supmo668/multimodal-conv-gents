import autogen

config_list = autogen.config_list_from_json(
    "OAI_CONFIG_LIST",
    filter_dict={
        # "model": ["gpt-4", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"],
        "model": ["gemini-1.5-pro"],
    },
)

llm_config = {
    "cache_seed": 42,  # change the cache_seed for different trials
    "temperature": 0,
    "config_list": config_list,
    "timeout": 120,
}

llm_config_stream = {"stream": True, **llm_config}