import sqlite3
from typing import Iterable, List, Tuple

DB_FILE = "data.db"


def create_connection():
    conn = sqlite3.connect(DB_FILE)
    return conn


def close_connection(conn):
    conn.commit()
    conn.close()


def insert_booking(
    year: int, month: int, day: int, hours: Iterable[int], floor: int, tele: str, chat_id: int
):
    conn = create_connection()
    cur = conn.cursor()

    # Check for duplicate bookings
    sql = """
        SELECT YEAR, MONTH, DAY, HOUR
        FROM LoungeBookings
        WHERE YEAR = ? AND
              MONTH = ? AND
              DAY = ? AND
              HOUR = ? AND
              FLOOR = ?
    """
    for hour in hours:
        cur.execute(sql, (year, month, day, hour, floor))
        rows = cur.fetchall()
        if rows:
            return False

    # Insert new bookings if okay
    sql = """
        INSERT INTO LoungeBookings(YEAR, MONTH, DAY, HOUR, FLOOR, TELE, CHAT_ID)
        VALUES(?, ?, ?, ?, ?, ?, ?)
    """
    for hour in hours:
        cur.execute(sql, (year, month, day, hour, floor, tele, chat_id))

    close_connection(conn)
    return True


def get_bookings_in_day(year: int, month: int, day: int, floor: int):
    conn = create_connection()
    cur = conn.cursor()
    sql = """
        SELECT HOUR
        FROM LoungeBookings
        WHERE YEAR = ? AND
              MONTH = ? AND
              DAY = ? AND
              FLOOR = ?
    """

    cur.execute(sql, (year, month, day, floor))
    rows = cur.fetchall()

    close_connection(conn)
    return [row[0] for row in rows]