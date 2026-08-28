"""Fetch and normalize the externally managed training timetable."""

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


WEEKDAYS = {
    1: "Ponedeljek",
    2: "Torek",
    3: "Sreda",
    4: "Četrtek",
    5: "Petek",
}


class TimetableUnavailable(Exception):
    """Raised when the timetable API cannot provide usable data."""


def fetch_timetable(url, timeout):
    """Return the API timetable plus a reserved Friday entry."""
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "PKSK/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response:  # noqa: S310 - configured HTTPS endpoint
            payload = json.load(response)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
        raise TimetableUnavailable from error

    if not isinstance(payload, dict) or not isinstance(payload.get("urnik"), list):
        raise TimetableUnavailable

    days_by_number = {}
    for day in payload["urnik"]:
        if not isinstance(day, dict):
            continue
        day_number = day.get("dan")
        if day_number not in WEEKDAYS:
            continue

        terms = []
        for term in day.get("termini", []):
            if not isinstance(term, dict):
                continue
            group = term.get("skupina")
            starts_at = term.get("od")
            ends_at = term.get("do")
            instructors = term.get("vaditelji", [])
            if not all(isinstance(value, str) and value for value in (group, starts_at, ends_at)):
                continue
            if not isinstance(instructors, list) or not all(isinstance(name, str) for name in instructors):
                instructors = []
            terms.append(
                {
                    "skupina": group,
                    "od": starts_at,
                    "do": ends_at,
                    "vaditelji": instructors,
                }
            )

        days_by_number[day_number] = {
            "dan": day_number,
            "dan_naziv": day.get("dan_naziv") or WEEKDAYS[day_number],
            "termini": sorted(terms, key=lambda term: (term["od"], term["do"], term["skupina"])),
        }

    return [
        {
            **days_by_number.get(day_number, {"dan": day_number, "dan_naziv": day_name, "termini": []}),
            "is_pending": day_number == 5 and day_number not in days_by_number,
        }
        for day_number, day_name in WEEKDAYS.items()
    ]
