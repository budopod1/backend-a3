import sqlite3
import time
import pickle


INTERVAL = 60


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


def repeat_save(state):
    try:
        conn = sqlite3.connect("saves.db")
        while True:
            print("Saving game...")
            time.sleep(INTERVAL)
            with conn:
                save(conn, state)
            with conn:
                exec_file(conn, "removal.sql")
    finally:
        # Should be a seperate way to use a context manager to do this
        conn.close()
    