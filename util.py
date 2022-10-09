import pytz
from typing import Iterable, List, Tuple
from datetime import datetime, timedelta

from db import get_bookings_in_day, insert_booking

tz = pytz.timezone('Asia/Singapore')

def today() -> datetime:
    time = now()
    return datetime(time.year, time.month, time.day, tzinfo=tz)

def now() -> datetime:
    return datetime.now(tz)

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

def get_available_timings(date: Tuple[int, int], floor: int) -> List[str]:
    date = datetime(now().year, date[1], date[0], tzinfo=tz)
    bookings = get_bookings_in_day(date.year, date.month, date.day, floor)
    avail = sorted(set(range(24)).difference(bookings))
    return [f"{x*100:04d}-{(x+1)*100:04d}" for x in avail]

def make_booking(date: Tuple[int, int], floor: int, times: Iterable[str], tele: str, chat_id: int) -> bool:
    date = datetime(now().year, date[1], date[0], tzinfo=tz)
    hours = [int(i.split('-')[0])//100 for i in times]
    return insert_booking(date.year, date.month, date.day, hours, floor, tele, chat_id)