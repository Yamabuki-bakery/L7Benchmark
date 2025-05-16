from dataclasses import dataclass
from typing import Optional, Callable, Any

@dataclass
class Args():
    url: str
    connection: int
    ip: str | None
    time: int
    shared_session: bool
    body: bool = False

type UrlGetter = Callable[..., str]

type ClientSessionOptions = dict[str, Any]