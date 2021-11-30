import json
import re


def fetch_user_id(text: str, username: str) -> int:
    matched = re.search(
        '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
    ).group()
    return json.loads(matched).get('id')
