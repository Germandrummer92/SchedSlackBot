from typing import TypedDict


class SlackEvent(TypedDict, total=False):
    user: str
