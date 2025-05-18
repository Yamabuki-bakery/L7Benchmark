import asyncio
import aiohttp
from typing import Optional
from mytypes import Args, BaseProfile, RequestInfo
import logging
from stats import Stats
import pprint
from zstd import ZSTD_uncompress


# SNI hostname feature is tested by Wireshark
async def worker(
    session: aiohttp.ClientSession,
    profile: BaseProfile,
    stats: Stats,
    args: Args,
    worker_id: int,
) -> None:
    try:
        last_url: Optional[str] = None
        last_status_code: Optional[int] = None
        while True:
            try:
                reqinfo: RequestInfo = profile.generate_request(
                    worker_id=worker_id,
                    last_url=last_url,
                    last_status_code=last_status_code,
                )
                async with session.request(
                    method=reqinfo.method.value,
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

    except asyncio.exceptions.CancelledError:
        pass



async def debug_worker(
    session: aiohttp.ClientSession,
    profile: BaseProfile,
    stats: Stats,
    args: Args,
    worker_id: int,
) -> None:
    try:
        last_url: Optional[str] = None
        last_status_code: Optional[int] = None
        while True:
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

                async with session.request(
                    method=str(reqinfo.method),
                    url=reqinfo.url,
                    headers=reqinfo.headers,
                    server_hostname=reqinfo.hostname,
                    data=reqinfo.body,
                    allow_redirects=False,
                    auto_decompress=True,
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
                    await stats.add_request(response.status)

            except Exception as e:
                await stats.add_request(-1)
                logging.error(f"Request failed: {e}")

            input("[Debug Session] Press Enter to continue or Ctrl+C to exit...")

    except asyncio.exceptions.CancelledError:
        pass

