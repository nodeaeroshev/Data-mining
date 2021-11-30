import re


def fetch_csrf_token(text: str) -> str:
    """Get csrf-token for auth"""
    matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
    return matched.split(':').pop().replace(r'"', '')
