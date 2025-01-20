# pageindexer
This project is used to index and retrieve information in our ElastichSearch stack.

## Environment variable that needs to be set
- DB\_NAME (no default): The name of the database to connect to.
- DB\_USER (no default): The user to connect to the database with.
- DB\_PASSWORD (no default): The password to connect to the database with.
- DB\_HOST (no default): The host of the database.
- DB\_PORT (no default): The port of the database.
- ES\_HOST (no default): The host of the ElasticSearch instance.
- ES\_PORT (no default): The port of the ElasticSearch instance.
- ES\_API\_KEY (no default): The API key to connect to the ElasticSearch
  instance with.
- SHOPIFY\_API\_KEY (no default): The API key to connect to the Shopify API
  with.
- SHOPIFY\_API\_SECRET (no default): The API secret to connect to the Shopify
  API with.

## How to run ?

### In development mode

#### For Foundxtion and nixOS users

In a terminal, do the following commands:
```zsh
cd tools/;
nix-shell --run zsh;
cd ..;
poetry install;
# export all environment variables...
poetry run python3 -m pageindexer.main;
```

### In production mode
You can use the available docker-compose file to run the server in production mode.
