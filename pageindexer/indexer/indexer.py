import queue

import shopify
import elasticsearch
from sentence_transformers import SentenceTransformer

from ..env import ES_HOST, ES_PORT, ES_API_KEY
from .document_creator import create_product_document


def __setup_elasticsearch():
    """
    Setup the Elasticsearch client with the environment variables.
    @return: Elasticsearch client
    """
    address = f"http://{ES_HOST}:{ES_PORT}"
    return elasticsearch.Elasticsearch(address, api_key=ES_API_KEY)


def __index_product(
    es_client: elasticsearch.Elasticsearch,
    model: SentenceTransformer,
    index: str,
    product: shopify.Product,
):
    """
    Index a product in the Elasticsearch index.
    @param es_client: Elasticsearch client
    @param model: SentenceTransformer model to encode the product title and description
    @param index: Name of the Elasticsearch Index
    @param product: Shopify product object
    """
    product_id = product.attributes["id"]
    product_document = create_product_document(model, product)

    es_client.index(index=index, id=product_id, document=product_document)
    pass


def __process_indexing(
    es_client: elasticsearch.Elasticsearch,
    model: SentenceTransformer,
    access_token: str,
    shop_name: str,
):
    """
    Process the indexing of a Shopify store.
    @param es_client: Elasticsearch client
    @param model: SentenceTransformer model to encode the product title and description
    @param access_token: Shopify access token
    @param shop_name: Shopify shop name
    """
    print("Indexer - Activating shopify session with token...")
    session = shopify.Session(shop_name, "2025-01", access_token)

    shopify.ShopifyResource.activate_session(session)
    print("Indexer - Session activated !")

    products = shopify.Product._find_every()
    try:
        es_index = {
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "description": {"type": "text"},
                    "vendor": {"type": "keyword"},
                    "image_link": {"type": "text"},
                    "options": {"type": "keyword"},
                    "vector": {
                        "type": "dense_vector",
                        "dims": 768,
                        "index": True,
                        "similarity": "cosine",
                    },
                }
            }
        }
        es_client.indices.create(index=shop_name, body=es_index)
        print(f"Indexer - Created index {shop_name} in Elastic !")
        for product in products:
            __index_product(es_client, model, shop_name, product)
    except Exception as exception:
        print(f"An error occurred while indexing {shop_name}:")
        print(exception)

    shopify.ShopifyResource.clear_session()


def index_shop(process_queue: queue.Queue):
    """
    Index the products of a Shopify store.
    @param process_queue: Queue containing the access token and shop Name
    """
    es_client: elasticsearch.Elasticsearch = __setup_elasticsearch()
    model: SentenceTransformer = SentenceTransformer("quora-distilbert-multilingual")
    print("Indexer - Initialized ES client")

    while True:
        (access_token, shop_name) = process_queue.get(block=True)
        print("Indexer - Get access_token and shop_name !")

        __process_indexing(es_client, model, access_token, shop_name)

        process_queue.task_done()
