from .environment import env

CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS")
