import aiohttp
from typing import Any
from mytypes import ClientSessionOptions


client_session_options: ClientSessionOptions = {
    # 'connector': aiohttp.TCPConnector(ssl=False),
    'timeout': aiohttp.ClientTimeout(total=45),
    'auto_decompress': False,
}
tcp_connector_options: dict[str, Any]  = {
    'ssl': False,
    'ttl_dns_cache': 120,
}