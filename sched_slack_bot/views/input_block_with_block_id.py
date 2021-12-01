from typing import Union, Optional, Any

from slack_sdk.models.blocks import InputBlock, PlainTextObject, InputInteractiveElement


class InputBlockWithBlockId(InputBlock):
    block_id: str

    def __init__(self, *, label: Union[str, dict[str, Any], PlainTextObject],
                 element: Union[str, dict[str, Any], InputInteractiveElement],
                 block_id: str, hint: Optional[Union[str, dict[str, Any], PlainTextObject]] = None,
                 dispatch_action: Optional[bool] = None, optional: Optional[bool] = None, **others: dict[str, Any]):
        super().__init__(label=label, element=element, block_id=block_id, hint=hint, dispatch_action=dispatch_action,
                         optional=optional, **others)
