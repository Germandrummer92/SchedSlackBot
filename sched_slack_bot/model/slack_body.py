from typing import TypedDict, Dict


class SlackBodyUser(TypedDict, total=False):
    id: str
    username: str
    name: str
    team_id: str


class SlackInputBlockState(TypedDict, total=False):
    type: str


class SlackState(TypedDict, total=False):
    values: Dict[str, Dict[str, SlackInputBlockState]]


class SlackView(TypedDict, total=False):
    state: SlackState
    id: str


class SlackBody(TypedDict, total=False):
    trigger_id: str
    user: SlackBodyUser
    view: SlackView
