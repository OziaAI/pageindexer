import queue

import shopify
import elasticsearch

from ..env import ES_HOST, ES_PORT, ES_API_KEY
from .document_creator import create_product_document

def __setup_elasticsearch():
    address = f"http://${ES_HOST}:${ES_PORT}"
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

def _process_idexing(es_client, access_token, shop_name):
    session = shopify.Session(shop_name, "2023-10", access_token)

    shopify.ShopifyResource.activate_session(session)
    
    products = shopify.Product._find_every()
    try:
        es_client.indices.create(index=shop_name)
        for product in products:
            __index_product(es_client, shop_name, product)
    except Exception as exception:
        print(f"An error occurred while indexing ${shop_name}:")
        print(exception)

    shopify.ShopifyResource.clear_session()


def index_shop(queue: queue.Queue):
    es_client = __setup_elasticsearch()

    while True:
        (access_token, shop_name) = queue.get(block=True)

        _process_idexing(es_client, access_token, shop_name)

        queue.task_done()
