"""Small creator scheduling helper. Public function names are stable."""
from datetime import datetime


def parse_time(value):
    return datetime.fromisoformat(value).replace(tzinfo=None)


def conflicts(events):
    ordered = sorted(events, key=lambda row: row['start'])
    pairs = []
    for left, right in zip(ordered, ordered[1:]):
        if parse_time(left['end']) >= parse_time(right['start']):
            pairs.append([left['id'], right['id']])
    return pairs


def total_minutes(events):
    return sum((parse_time(e['end']) - parse_time(e['start'])).seconds // 60 for e in events)
