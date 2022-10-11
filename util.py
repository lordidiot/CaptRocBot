from collections import defaultdict
import pytz
from typing import Dict, Iterable, List, Optional, Tuple
from datetime import datetime, timedelta, timezone

from db import del_booking, get_bookings_in_day, get_bookings_in_week, insert_booking

tz = pytz.timezone('Etc/GMT-8')

def today() -> datetime:
    time = now()
    return datetime(time.year, time.month, time.day, tzinfo=tz)

def now() -> datetime:
    return datetime.now(tz)

def to_utc(date: datetime) -> datetime:
    return date.astimezone(timezone.utc)

def to_tz(date: datetime) -> datetime:
    return date.astimezone(tz)

def to_iso(date: datetime) -> str:
    return date.isoformat()

def from_iso(date: datetime) -> str:
    return datetime.fromisoformat(date)

def next_week() -> List[datetime]:
    """Returns days in next two weeks"""
    return [today()+timedelta(days=i) for i in range(7)]

def weekday(x: datetime) -> str:
    return [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun"
    ][x.weekday()]

def get_available_timings(date: datetime, floor: int) -> List[datetime]:
    """Returns timezone corrected available timings within day"""
    date = date.replace(hour=0, minute=0, second=0, microsecond=0)
    hours = set([
        date.replace(hour=i, minute=0, second=0, microsecond=0)
        for i in range(24)
    ])

    # to_utc before going to db, to_tz coming back from db
    bookings = get_bookings_in_day(to_utc(date), floor)
    bookings = set([to_tz(from_iso(i)) for i in bookings])

    avail = sorted(hours.difference(bookings))

    return avail

def make_booking(times: Iterable[datetime], floor: int, tele: str, chat_id: int) -> bool:
    # to_utc before going to db
    dates = [to_utc(time) for time in times]
    return insert_booking(dates, floor, tele, chat_id)

def get_bookings(tele: str="") -> Dict[Tuple[int, int], List[Tuple[datetime, int, str]]]:
    date = to_utc(now()) 
    bookings = get_bookings_in_week(date, tele)
    l = defaultdict(list)
    for booking in bookings:
        time, floor, username = booking
        time = to_tz(from_iso(time))
        l[(time.day, time.month)].append((time, floor, username))
    return l

def time_to_range(time: datetime, hours: int) -> str:
    return f"{time.hour*100:04d}-{(time.hour+hours)*100:04d}"

def delete_booking(time: datetime, floor: int, tele: str) -> None:
    del_booking(to_utc(time), floor, tele)
