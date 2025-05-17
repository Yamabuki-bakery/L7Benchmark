import asyncio
import aiohttp
from typing import Optional
from mytypes import Args, UrlGetter, ClientSessionOptions, BaseProfile, RequestInfo
import logging
from stats import Stats
from config import client_session_options, tcp_connector_options


# SNI hostname feature is tested by Wireshark
async def worker(
    session: Optional[aiohttp.ClientSession],
    profile: BaseProfile,
    semaphore: asyncio.Semaphore,
    stats: Stats,
    args: Args,
    worker_id: int,
) -> None:
    own_session: aiohttp.ClientSession = session or aiohttp.ClientSession(
        **client_session_options, connector=aiohttp.TCPConnector(**tcp_connector_options))
    try:
        last_url: Optional[str] = None
        last_status_code: Optional[int] = None
        while True:
            async with semaphore:
                try:
                    reqinfo: RequestInfo = profile.generate_request(
                        worker_id=worker_id,
                        last_url=last_url,
                        last_status_code=last_status_code,
                    )
                    async with own_session.request(
                        method=str(reqinfo.method),
                        url=reqinfo.url,
                        headers=reqinfo.headers,
                        server_hostname=reqinfo.hostname,
                        data=reqinfo.body,
                        allow_redirects=False,
                    ) as response:
                        if args.body:
                            await response.read()
                        await stats.add_request(response.status)
                        last_url = reqinfo.url
                        last_status_code = response.status
                except Exception as e:
                    await stats.add_request(-1)
                    logging.error(f"Request failed: {e}")

    except asyncio.exceptions.CancelledError:
        pass
    finally:
        logging.debug("Worker finished")
        if session is None:
            await own_session.close()


async def debug_worker(
    session: Optional[aiohttp.ClientSession],
    url_getter: UrlGetter,
    headers: dict[str, str],
    hostname: str,
    semaphore: asyncio.Semaphore,
    client_session_options: ClientSessionOptions
) -> None:
    raise NotImplementedError("Debug worker is not implemented yet.")
