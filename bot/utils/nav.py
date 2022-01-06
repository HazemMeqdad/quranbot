from __future__ import annotations
from typing import Any
import hikari
from lightbulb.utils import pag
from typing import Optional

class EmbedPaginator(pag.EmbedPaginator):
    def __init__(self, *, max_lines: Optional[int] = None, max_chars: int = 2048, prefix: str = "", suffix: str = "", line_separator: str = "\n") -> None:
        super().__init__(
            max_lines=max_lines,
            max_chars=max_chars,
            prefix=prefix,
            suffix=suffix,
            line_separator=line_separator,
            page_factory=lambda i, s: hikari.Embed(description=s).set_footer(text=f"Page {i}"),
        )
    
