import queue

import shopify
import elasticsearch

from ..env import ES_HOST, ES_PORT, ES_API_KEY
from .document_creator import create_product_document

def __setup_elasticsearch():
    address = f"http://{ES_HOST}:{ES_PORT}"
    return elasticsearch.Elasticsearch(address, api_key=ES_API_KEY)

def __index_product(es_client: elasticsearch.Elasticsearch,
                    index: str, product: shopify.Product):
    product_id = product.attributes["id"]
    product_document = create_product_document(product)
    
    es_client.index(
        index=index,
        id=product_id,
        document=product_document)
    pass

def __process_idexing(es_client: elasticsearch.Elasticsearch,
                      access_token: str, shop_name: str):
    print("Indexer - Activating shopify session with token...")
    session = shopify.Session(shop_name, "2023-10", access_token)

    shopify.ShopifyResource.activate_session(session)
    print("Indexer - Session activated !")
    
    products = shopify.Product._find_every()
    try:
        es_client.indices.create(index=shop_name)
        print(f"Indexer - Created index {shop_name} in Elastic !")
        for product in products:
            __index_product(es_client, shop_name, product)
    except Exception as exception:
        print(f"An error occurred while indexing {shop_name}:")
        print(exception)

    shopify.ShopifyResource.clear_session()


def index_shop(process_queue: queue.Queue):
    es_client = __setup_elasticsearch()
    print("Indexer - Initialized ES client")

    while True:
        (access_token, shop_name) = process_queue.get(block=True)
        print("Indexer - Get access_token and shop_name !")

        __process_idexing(es_client, access_token, shop_name)

        process_queue.task_done()
