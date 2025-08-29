from datetime import datetime
from dataclasses import dataclass


@dataclass
class Date:
    day: int
    suffix: str
    month: str
    year: str


def ordinal(day: int):
    if day == 0:
        return ''

    if 10 <= day % 100 <= 20:
        return 'th'
    else:
        return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')


def try_get_date(date: str) -> Date:
    for fmt in ('%B %Y', '%Y-%m-%d', '%d %B %Y'):
        try:
            dt = datetime.strptime(date, fmt)

            if fmt == '%B %Y':
                day = 0
            else:
                day = dt.day

            suffix = ordinal(day)
            month = dt.strftime("%B")
            year = str(dt.year)

            return Date(day, suffix, month, year)
        except ValueError:
            continue
    else:
        raise ValueError(f"Unknown date format: {date}")


def get_formatted_date(date: str) -> Date:
    return try_get_date(date)
