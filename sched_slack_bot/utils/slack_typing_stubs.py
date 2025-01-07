from typing import TypedDict, Dict, List


class SlackBodyUser(TypedDict, total=False):
    id: str
    username: str
    name: str
    team_id: str


class SlackInputBlockState(TypedDict, total=False):
    selected_conversation: str
    selected_date: str
    selected_option: Dict[str, str]
    selected_users: List[str]
    type: str


class SlackState(TypedDict, total=False):
    values: Dict[str, Dict[str, SlackInputBlockState]]


class SlackView(TypedDict, total=False):
    state: SlackState
    id: str
    external_id: str


class SlackAction(TypedDict, total=False):
    action_id: str
    block_id: str


class SlackBody(TypedDict, total=False):
    trigger_id: str
    user: SlackBodyUser
    view: SlackView
    actions: List[SlackAction]


class SlackEvent(TypedDict, total=False):
    user: str
