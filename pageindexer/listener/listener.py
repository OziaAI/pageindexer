import select
import psycopg2
import psycopg2.extensions
import queue

from ..env import DB_NAME, DB_PASSWORD, DB_USER, DB_HOST, DB_PORT

def __get_cursor():

    db = psycopg2.connect(host=DB_HOST, database=DB_NAME,
                          user=DB_USER, password=DB_PASSWORD,
                          port=DB_PORT)
    db.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

    return (db,db.cursor())

def __get_token_and_shop(cursor, notification):
    print("Got Notification:", notification.pid, notification.channel,
          notification.payload)

    # According to the architecture, the database send the id of the
    # new access as payload of the notification
    # We can just grab the row with the correspondant id and have
    # the access token along with the shop linked to

    access_id = notification.payload

    query = "SELECT shop_name, access_token FROM shopify_access WHERE id = %s";

    cursor.execute(query, (access_id,))

    rows = cursor.fetchall()

    print(rows)
    shop_name, access_token = rows[0]

    return access_token, shop_name

def fill_queue_on_notify(queue: queue.Queue):

    (db,cursor) = __get_cursor()
    # https://stackoverflow.com/a/44199319
    # According to this post, we need to quote the channel name
    cursor.execute("LISTEN \"access_update\";")

    print("Listening for any notification on `access_update`")

    while True:
        if select.select([db],[],[],5) == ([],[],[]):
            # https://www.psycopg.org/docs/advanced.html#asynchronous-notifications
            # This technique checks, using kernel awakening strategy, 
            # when some data is ready to be read
            print("Timeout")
        else:
            db.poll()
            while db.notifies:
                notification = db.notifies.pop(0)
                item = __get_token_and_shop(cursor, notification)
                queue.put(item)



