import os

def __set_env(env_name: str):
    env_value = os.getenv(env_name)
    if env_value is None:
        print("Please set " + env_name + " as an environment variable")
        exit(1)
    return env_value

SHOPIFY_API_KEY = __set_env("SHOPIFY_API_KEY")
SHOPIFY_API_SECRET = __set_env("SHOPIFY_API_SECRET")

DB_NAME = __set_env("DB_NAME")
DB_USER = __set_env("DB_USER")
DB_PASSWORD = __set_env("DB_PASSWORD")
DB_HOST = __set_env("DB_HOST")
DB_PORT = __set_env("DB_PORT")

ES_HOST = __set_env("ES_HOST")
ES_PORT = __set_env("ES_PORT")
ES_API_KEY = __set_env("ES_API_KEY")
