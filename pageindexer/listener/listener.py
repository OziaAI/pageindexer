import select
import psycopg2
import psycopg2.extensions
import queue

from ..env import DB_NAME, DB_PASSWORD, DB_USER, DB_HOST, DB_PORT


def __get_cursor():
    """
    Get a connection and a cursor to the database
    @return: a tuple with the connection and the cursor
    """

    db = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD, port=DB_PORT
    )
    db.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    return (db, db.cursor())


def __get_token_and_shop(cursor, notification):
    """
    Get the token and the shop name from the database
    @param cursor: the cursor to the database
    @param notification: the notification object
    @return: a tuple with the token, the shop name and the access id
    """
    print(
        "Listener - Got Notification:",
        notification.pid,
        notification.channel,
        notification.payload,
    )

    # According to the architecture, the database send the id of the
    # new access as payload of the notification
    # We can just grab the row with the correspondant id and have
    # the access token along with the shop linked to

    access_id = notification.payload

    query = "SELECT shop_name, access_token FROM shopify_access WHERE id = %s"

    cursor.execute(query, (access_id,))

    rows = cursor.fetchall()

    print(rows)
    shop_name, access_token = rows[0]

    return access_token, shop_name, access_id


def __mark_item(cursor, access_id):
    query = "UPDATE shopify_access SET product_loaded = TRUE WHERE id = %s"

    cursor.execute(query, (access_id,))


def __fill_queue_on_notify(queue: queue.Queue, db, cursor):

    # https://stackoverflow.com/a/44199319
    # According to this post, we need to quote the channel name
    cursor.execute('LISTEN "access_update";')

    print("Listener - Listening for any notification on `access_update`")

    while True:
        if select.select([db], [], [], 5) == ([], [], []):
            # https://www.psycopg.org/docs/advanced.html#asynchronous-notifications
            # This technique checks, using kernel awakening strategy,
            # when some data is ready to be read
            pass
        else:
            db.poll()
            while db.notifies:
                notification = db.notifies.pop(0)
                access_token, shop_name, access_id = __get_token_and_shop(
                    cursor, notification
                )
                queue.put((access_token, shop_name))
                __mark_item(cursor, access_id)


def __fill_queue_of_unprocessed(queue: queue.Queue, db, cursor):
    """
    Fill the queue with the shop name and the access token
    of the shops that have not been processed yet
    @param queue: the queue to Fill
    @param db: the database connection
    @param cursor: the cursor to the database
    """

    query = "SELECT shop_name, access_token, id FROM shopify_access WHERE product_loaded = False"

    cursor.execute(query)

    rows = cursor.fetchall()
    for row in rows:
        shop_name, access_token, access_id = row
        queue.put((access_token, shop_name))
        __mark_item(cursor, access_id)


def fill_process_queue(queue: queue.Queue):
    """
    Fill the queue with the shop name and the access token.
    @param queue: the queue to fill
    """
    (db, cursor) = __get_cursor()

    __fill_queue_of_unprocessed(queue, db, cursor)
    __fill_queue_on_notify(queue, db, cursor)
