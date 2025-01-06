
from autogen import config_list_from_json


llm_config = {
    "config_list": config_list_from_json(
        "OAI_CONFIG_LIST", filter_dict={'model': ['gemini-1.5-pro']}
    )
}