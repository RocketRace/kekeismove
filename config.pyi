from typing import TYPE_CHECKING, Sequence

if TYPE_CHECKING:
    from bot import EmojiConfig

token: str
cogs: Sequence[str]
prefix: str
emoji: EmojiConfig
