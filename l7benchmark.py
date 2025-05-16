import argparse
import asyncio
import time
from urllib.parse import urlparse
import aiohttp
from typing import Optional, Any
from mytypes import Args, UrlGetter, ClientSessionOptions
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

client_session_options: ClientSessionOptions = {
    # 'connector': aiohttp.TCPConnector(ssl=False),
    'timeout': aiohttp.ClientTimeout(total=10),
    'auto_decompress': False,
}
tcp_connector_options: dict[str, Any]  = {
    'ssl': False,
    'ttl_dns_cache': 120,
}

# 全局統計變量和鎖
_2xx_requests = 0
_3xx_requests = 0
_4xx_requests = 0
_5xx_requests = 0
other_requests = 0
stat_lock = asyncio.Lock()

async def worker(
        session: Optional[aiohttp.ClientSession], 
        url_getter: UrlGetter, 
        headers, 
        semaphore,
        end_time,
        client_session_options: ClientSessionOptions
    ) -> None:
    global _2xx_requests, _3xx_requests, _4xx_requests, _5xx_requests, other_requests
    own_session: aiohttp.ClientSession = session or aiohttp.ClientSession(**client_session_options, connector=aiohttp.TCPConnector(**tcp_connector_options))
    try:
        while time.time() < end_time:
            async with semaphore:
                try:
                    url = url_getter()
                    async with own_session.get(url, headers=headers) as response:
                        if args.body:
                            await response.read()
                        async with stat_lock:
                            if 200 <= response.status < 300:
                                _2xx_requests += 1
                            elif 300 <= response.status < 400:
                                _3xx_requests += 1
                            elif 400 <= response.status < 500:
                                _4xx_requests += 1
                            elif 500 <= response.status < 600:
                                _5xx_requests += 1
                            else:
                                other_requests += 1
                except Exception as e:
                    async with stat_lock:
                        other_requests += 1
                        logging.error(f"Request failed: {e}")

    except asyncio.exceptions.CancelledError:
        pass
    finally:
        logging.debug("Worker finished")
        if session is None:
            await own_session.close()

async def print_stats(end_time):
    start = time.time()
    while time.time() < end_time:
        await asyncio.sleep(0.25)
        async with stat_lock:
            _2 = _2xx_requests
            _3 = _3xx_requests
            _4 = _4xx_requests
            _5 = _5xx_requests
            other = other_requests
            t = _2 + _3 + _4 + _5 + other
        elapsed = time.time() - start
        print(f"\rRequests: {t} | 2xx: {_2} | "
              f"3xx: {_3} | 4xx: {_4} | "
              f"5xx: {_5} | Other: {other} | "
              f"Elapsed: {elapsed:.2f}s", end="")


parser = argparse.ArgumentParser(description="🚀 Website Benchmark Tool")
parser.add_argument('-u', "--url", required=True, help="URL to test")
parser.add_argument('-c', "--connection", type=int, default=10, help="Concurrent connections")
parser.add_argument("--ip", help="Override DNS resolution")
parser.add_argument('-t', "--time", type=int, default=10, help="Test duration in seconds")
parser.add_argument('-b', "--body", action="store_true", default=False, help="Download response body")
parser.add_argument("--shared-session", action="store_true", default=False, help="Share single client session across all workers")
cmdargs = parser.parse_args()

args = Args(
    url=cmdargs.url,
    connection=cmdargs.connection,
    ip=cmdargs.ip,
    time=cmdargs.time,
    shared_session=cmdargs.shared_session,
    body=cmdargs.body
)

async def main():
    # 處理 URL 和 headers
    parsed_url = urlparse(args.url)
    headers = {}
    new_url = args.url

    if args.ip:
        # 構造新的 URL 和 Host header
        netloc = args.ip
        if parsed_url.port:
            netloc += f":{parsed_url.port}"
        new_url = parsed_url._replace(netloc=netloc).geturl()
        headers["Host"] = parsed_url.hostname


    semaphore = asyncio.Semaphore(args.connection)
    end_time = time.time() + args.time

    session = aiohttp.ClientSession(
        **client_session_options, 
        connector=aiohttp.TCPConnector(**tcp_connector_options),
    ) if args.shared_session else None

    # 創建工作任務
    tasks = [
        asyncio.create_task(worker(
            session=session, 
            url_getter=lambda: new_url, 
            headers=headers, 
            semaphore=semaphore, 
            end_time=end_time,
            client_session_options=client_session_options
        ))
        for _ in range(args.connection * 2 if session is not None else args.connection)  # 在共享 Session 的情況下，多準備幾個 workers，然後用 semaphore 控制
    ]
    stats_task = asyncio.create_task(print_stats(end_time))

    # 等待測試時間結束
    try:
        await asyncio.sleep(args.time)
    except asyncio.exceptions.CancelledError:
        pass

    # 取消所有任務
    for task in tasks:
        task.cancel()
    stats_task.cancel()

    # 等待任務完成
    await asyncio.gather(*tasks, return_exceptions=True)
    await asyncio.gather(stats_task, return_exceptions=True)

    # 關閉 session
    if session:
        await session.close()

    # 打印最終結果
    async with stat_lock:
        print("\n\n🏁 Final Results:")
        print(f"Total Requests: {_2xx_requests + _3xx_requests + _4xx_requests + _5xx_requests + other_requests}")
        print(f"2xx: {_2xx_requests}")
        print(f"3xx: {_3xx_requests}")
        print(f"4xx: {_4xx_requests}")
        print(f"5xx: {_5xx_requests}")
        print(f"Other: {other_requests}")
        print(f"Elapsed Time: {args.time} seconds")


if __name__ == "__main__":
    asyncio.run(main())