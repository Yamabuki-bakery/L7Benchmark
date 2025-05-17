from dataclasses import dataclass
from typing import Optional, Callable, Any
from collections import OrderedDict
from enum import Enum
from header_parse import parse_header
from typing import Optional
from collections import OrderedDict

class HttpMethod(Enum):
    GET = 'GET'
    POST = 'POST'
    PUT = 'PUT'
    DELETE = 'DELETE'
    HEAD = 'HEAD'
    OPTIONS = 'OPTIONS'
    # PATCH = 'PATCH'

    def __str__(self):
        return self.value


@dataclass
class Args():
    url: str
    connection: int
    ip: Optional[str]
    time: int
    shared_session: bool
    body: bool
    header: list[str]
    profile: str
    debug: bool
    method: HttpMethod = HttpMethod.GET

type UrlGetter = Callable[..., str]

type ClientSessionOptions = dict[str, Any]


@dataclass
class RequestInfo:
    method: HttpMethod
    url: str
    hostname: str
    headers: OrderedDict[str, str]
    body: Optional[Any] = None

# @dataclass
# class WorkerContext:
#     worker_id: int
#     last_url: Optional[str]
#     last_status_code: Optional[int]


class BaseProfile:
    """所有 Profile 必須繼承的基類"""
    def __init__(self, args: Args, first_url: str, hostname: str):
        """
        args: 從命令行解析的參數字典
        first_url: 第一個請求的 URL，一般由命令行參數提供，並完成 IP 解析後的結果
        hostname: SNI 的主機名，也應該被用在 Host header 裡面
        """
        self.args: Args = args
        self.first_url: str = first_url
        self.hostname: str = hostname
        self.custom_headers: OrderedDict[str, str] = parse_header(args.header)
            
        # ⚠️ 這個應該總是注入到 headers 的最前面
        self.custom_headers["host"] = hostname
        self.custom_headers.move_to_end("host", last=False)

    
    def generate_request(self, 
          worker_id: int,
          last_url: Optional[str],
          last_status_code: Optional[int],        
        ) -> RequestInfo:
        """
        必須返回包含請求參數的 object，格式：
        RequestInfo(
            method='GET',
            url='http://example.com',
            headers={},
            body=None
        )
        """
        raise NotImplementedError