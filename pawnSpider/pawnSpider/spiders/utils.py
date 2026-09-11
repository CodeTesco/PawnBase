import re
from datetime import datetime

def clean_tc(raw_string):
    if not raw_string:
        return None, 0

    text = raw_string.lower()
    plus_match = re.search(r"(\d+)[^\d+]*\+[^\d+]*(\d+)", text)
    if plus_match:
        return int(plus_match.group(1)), int(plus_match.group(2))

    hm_match = re.search(r'(\d+)\s*h(?:ours?)?[^\d]*(\d+)?\s*m?', text)
    if hm_match:
        hours = int(hm_match.group(1))
        minutes = int(hm_match.group(2)) if hm_match.group(2) else 0
        return hours*60 + minutes, 0

    min_match = re.search(r"(\d+)", text)
    if min_match:
        return int(min_match.group(1)), 0

    return None, 0

def clean_date(raw_string):
    if not raw_string:
        return None

    value = raw_string.strip().split(" to ", 1)[0].strip()
    for pattern, date_format in (
        (r"\d{4}/\d{2}/\d{2}", "%Y/%m/%d"),
        (r"\d{2}\.\d{2}\.\d{4}", "%d.%m.%Y"),
    ):
        match = re.search(pattern, value)
        if match:
            return datetime.strptime(match.group(), date_format).date()

    return None