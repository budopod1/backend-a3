import sqlite3
import time
import pickle
from math import floor, log


INTERVAL = 60
assert INTERVAL > 1


def load():
    conn = sqlite3.connect("saves.db")
    with conn:
        blobs = conn.execute(
            "SELECT save FROM saves ORDER BY created DESC LIMIT 1"
        ).fetchall()
        if len(blobs) == 0:
            return None
        (blob,), = blobs
    conn.close()
    return pickle.loads(blob)


def setup():
    conn = sqlite3.connect("saves.db")
    with conn:
        exec_file(conn, "setup.sql")
    conn.close()


def exec_file(conn, path):
    with open(path) as file:
        conn.executescript(file.read())


def save(conn, state):
    conn.execute(
        "INSERT INTO saves (created, save) VALUES (?, ?)",
        (int(time.time()), pickle.dumps(state))
    )


def remove_extra(conn):
    with conn:
        saves = conn.execute("SELECT created FROM saves ORDER BY created ASC")
    bins = {}
    for created, in saves:
        num = floor(log((time.time() - created) / INTERVAL, 2))
        if num not in bins:
            bins[num] = created
    print(f"Saving game... ({len(bins) + 1} saves)")
    with conn:
        vals = ", ".join([str(val) for val in bins.values()])
        conn.execute(f"DELETE FROM saves WHERE created NOT IN ({vals})")


def repeat_save(state):
    try:
        while True:
            time.sleep(INTERVAL)
            conn = sqlite3.connect("saves.db")
            remove_extra(conn)
            with conn:
                save(conn, state)
            conn.close()
    finally:
        # Should be a seperate way to use a context manager to do this
        conn.close()
    