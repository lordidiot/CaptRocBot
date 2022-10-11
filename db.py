from datetime import datetime, timedelta
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
    times: Iterable[datetime], floor: int, tele: str, chat_id: int
):
    conn = create_connection()
    cur = conn.cursor()

    # Check for duplicate bookings
    sql = """
        SELECT TIME
        FROM LoungeBookings
        WHERE TIME = ? AND
              FLOOR = ?
    """
    for time in times:
        cur.execute(sql, (time, floor))
        rows = cur.fetchall()
        if rows:
            return False

    # Insert new bookings if okay
    sql = """
        INSERT INTO LoungeBookings(TIME, FLOOR, TELE, CHAT_ID)
        VALUES(?, ?, ?, ?)
    """
    for time in times:
        cur.execute(sql, (time, floor, tele, chat_id))

    close_connection(conn)
    return True


def get_bookings_in_day(date: datetime, floor: int) -> List[str]:
    """Return list of iso format times with booking within the day specified by date"""
    conn = create_connection()
    cur = conn.cursor()
    sql = """
        SELECT TIME
        FROM LoungeBookings
        WHERE TIME >= ? AND
              TIME < ? AND
              FLOOR = ?
    """

    cur.execute(sql, (date, date+timedelta(days=1), floor))
    rows = cur.fetchall()

    close_connection(conn)
    return [row[0] for row in rows]

def get_bookings_in_week(date: datetime, tele: str) -> List[Tuple[str, int, str]]:
    conn = create_connection()
    cur = conn.cursor()
    if tele:
        sql = """
            SELECT TIME, FLOOR, TELE
            FROM LoungeBookings
            WHERE TIME >= ? AND
                  TIME < ? AND
                  TELE = ? ORDER BY
                  FLOOR ASC, TIME DESC
        """
        cur.execute(sql, (date, date+timedelta(days=7), tele))
        rows = cur.fetchall()
    else:
        sql = """
            SELECT TIME, FLOOR, TELE
            FROM LoungeBookings
            WHERE TIME >= ? AND
                TIME < ?
                ORDER BY
                FLOOR ASC, TIME DESC
        """
        cur.execute(sql, (date, date+timedelta(days=7)))
        rows = cur.fetchall()


    close_connection(conn)
    return rows

def del_booking(time: datetime, floor: int, tele: str) -> None:
    conn = create_connection()
    cur = conn.cursor()
    sql = """
        DELETE FROM LoungeBookings
        WHERE TIME = ? AND
              FLOOR = ? AND
              TELE = ?
    """

    cur.execute(sql, (time, floor, tele))
    close_connection(conn)