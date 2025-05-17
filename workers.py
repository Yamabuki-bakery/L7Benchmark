import asyncio
import aiohttp
from typing import Optional
from mytypes import Args, BaseProfile, RequestInfo
import logging
from stats import Stats
from config import client_session_options, tcp_connector_options
import pprint
from zstd import ZSTD_uncompress


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
                except Exception as _:
                    await stats.add_request(-1)
                    # logging.error(f"Request failed: {e}")

    except asyncio.exceptions.CancelledError:
        pass
    finally:
        logging.debug("Worker finished")
        if session is None:
            await own_session.close()


async def debug_worker(
    session: Optional[aiohttp.ClientSession],
    profile: BaseProfile,
    semaphore: asyncio.Semaphore,
    stats: Stats,
    args: Args,
    worker_id: int,
) -> None:
    own_session: aiohttp.ClientSession = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            auto_decompress=True,
            connector=aiohttp.TCPConnector(**tcp_connector_options)
        )
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
                    logging.info(f'[Profile] {reqinfo.method} {reqinfo.url}')
                    logging.info(f'[Profile] Sending hostname: {reqinfo.hostname}')
                    logging.info(f'[Profile] Headers:')
                    pprint.pprint(reqinfo.headers)
                    logging.info(f'[Profile] Body Size: {len(reqinfo.body or [])}')

                    async with own_session.request(
                        method=str(reqinfo.method),
                        url=reqinfo.url,
                        headers=reqinfo.headers,
                        server_hostname=reqinfo.hostname,
                        data=reqinfo.body,
                        allow_redirects=False,
                    ) as response:
                        data = await response.read()
                        last_url = reqinfo.url
                        last_status_code = response.status

                        logging.info(f'[Resp] ({response.status}) {len(data)} bytes')
                        logging.info(f'[Resp] Headers:')
                        pprint.pprint([(k, v) for k, v in response.headers.items()])
                        logging.info(f'[Resp] Body:')
                        try:
                            if response.headers.get('Content-Encoding') == 'zstd':
                                data = ZSTD_uncompress(data)
                            text = data.decode('utf-8', errors='replace')
                            pprint.pprint(text[:1024])
                        except UnicodeDecodeError:
                            pprint.pprint(data[:1024])

                except Exception as e:
                    await stats.add_request(-1)
                    logging.error(f"Request failed: {e}")

            input("[Debug Session] Press Enter to continue or Ctrl+C to exit...")

    except asyncio.exceptions.CancelledError:
        pass
    finally:
        logging.debug("Debug worker finished")
        if session is None:
            await own_session.close()
