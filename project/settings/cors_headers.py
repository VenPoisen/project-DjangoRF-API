from utils.environment import get_env_variable, parse_comma_sep_str_to_list
from .environment import env

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")
