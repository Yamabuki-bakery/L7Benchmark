import argparse
import asyncio
from multiprocessing import connection
import time
import aiohttp
from mytypes import Args, BaseProfile, HttpMethod
from urlparse import generate_new_url_and_hostname
import logging
from stats import Stats
from workers import worker, debug_worker
from result import Ok, Err
from config import tcp_connector_options
from profile_loader import load_profile
import uvloop

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
stats = Stats()

parser = argparse.ArgumentParser(description="🚀 Website Benchmark Tool")
parser.add_argument('-u', "--url", required=True, help="URL to test")
parser.add_argument('-c', "--connection", type=int, default=10, help="Concurrent connections")
parser.add_argument("--ip", help="Override DNS resolution")
parser.add_argument('-t', "--time", type=int, default=10, help="Test duration in seconds")
parser.add_argument('-b', "--body", action="store_true", default=False, help="Download response body")
# parser.add_argument("--shared-session", action="store_true", default=False, help="Share single client session across all workers")
parser.add_argument('-H', '--header', action='append', default=[], 
                   help="Add custom header to request (can be used multiple times). Format: 'Name: Value'")
parser.add_argument("-p", "--profile", 
                   type=str, default='default',
                   help="Path to request generator profile or profile name (default: 'default')")
parser.add_argument("-X", "--method",
                   type=HttpMethod, choices=list(HttpMethod), default=HttpMethod.GET,
                   help="HTTP method to use for requests (default: GET)")
parser.add_argument('--debug', action='store_true', default=False, help="Enable debug mode, inspect every request and response")
parser.add_argument('--timeout', type=int, default=60, help="Timeout for each request in seconds, default: 60")

cmdargs = parser.parse_args()

args = Args(
    url=cmdargs.url,
    connection=cmdargs.connection,
    ip=cmdargs.ip,
    time=cmdargs.time,
    # shared_session=cmdargs.shared_session,
    body=cmdargs.body,
    header=cmdargs.header,
    profile=cmdargs.profile,
    method=cmdargs.method,
    debug=cmdargs.debug,
    timeout=cmdargs.timeout,
)


async def main():
    # 準備好必要的參數，傳給 profile，之後的狀態管理就交給 profile 去做
    gen_result = await generate_new_url_and_hostname(args.url, args.ip)
    match gen_result:
        case Ok((new_url, hostname)):
            logging.info(f"Generated URL: {new_url}")
        case Err(e):
            logging.error(f"Error generating URL: {e}")
            return
        
    try:
        ProfileClass = load_profile(args.profile)
        logging.info(f"Using profile: {ProfileClass.__name__}")
        profile: BaseProfile = ProfileClass(args, new_url, hostname)
    except RuntimeError as e:
        logging.error(f"Error loading profile: {e}")
        return

    end_time = time.time() + args.time
    session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=args.timeout),
        auto_decompress=False,
        connector=aiohttp.TCPConnector(**tcp_connector_options),
    ) # if args.shared_session else None

    assert isinstance(new_url, str)

    if args.debug:
        logging.info("Debug mode enabled")
        selected_worker = debug_worker
        pool_size = 1
    else:
        selected_worker = worker
        pool_size = args.connection

    tasks = [
        asyncio.create_task(selected_worker(
            session=session, 
            profile=profile,
            stats=stats,
            args=args,
            worker_id=i,
        ))
        for i in range(pool_size)  
    ]
    print()
    connection_counter = lambda: len(session._connector._acquired) # type: ignore
    stats_task = asyncio.create_task(stats.print_stats(end_time, connection_counter))

    try:
        await asyncio.sleep(999999999 if args.debug else args.time)
    except asyncio.exceptions.CancelledError:
        pass

    for task in tasks:
        task.cancel()
    stats_task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)
    await asyncio.gather(stats_task, return_exceptions=True)

    if session:
        await session.close()

    print_final_stats(stats)

def print_final_stats(stats: Stats) -> None:
    print("\n\n🏁 Final Results:")
    print(f"Total Requests: {stats.sum_requests()}")
    print(f"2xx: {stats.get_2xx_requests()}")
    print(f"3xx: {stats.get_3xx_requests()}")
    print(f"4xx: {stats.get_4xx_requests()}")
    print(f"5xx: {stats.get_5xx_requests()}")
    print(f"Timeout: {stats.get_timeout_requests()}")
    print(f"Elapsed Time: {args.time} seconds")

        
if __name__ == "__main__":
    uvloop.run(main())
