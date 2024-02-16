import shopify
import threading
import queue

from .env import SHOPIFY_API_KEY, SHOPIFY_API_SECRET
from .listener import fill_process_queue
from .indexer import index_shop

def main():
    shopify.Session.setup(api_key=SHOPIFY_API_KEY, secret=SHOPIFY_API_SECRET)
    shared_queue: queue.Queue = queue.Queue()
    
    listener_thread = threading.Thread(target=fill_process_queue, args=(shared_queue,))
    indexer_thread = threading.Thread(target=index_shop, args=(shared_queue,))

    listener_thread.start()
    indexer_thread.start()

    listener_thread.join()
    shared_queue.join()
    indexer_thread.join()

if __name__ == "__main__":
    main()
