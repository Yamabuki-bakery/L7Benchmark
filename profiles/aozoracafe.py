"""
    Profile for Aozoracafe.com@Yuzu
    URL base: https://api.aozoracafe.com
    We are going to benchmark these interfaces:
        - /api/home/list?page=1&pageSize=18&search=<random_string>
        - /api/rating/<random_number>
        - /api/page/<random_number>
        - [POST] /api/ranking/download/<random_number>
"""

from collections import OrderedDict
from mytypes import BaseProfile, HttpMethod
from mytypes import Args, RequestInfo
from typing import Optional
import random

from urlparse import get_base_url
import copy


class AozoracafeProfile(BaseProfile):
    def __init__(self, args: Args, first_url: str, hostname: str):
        super().__init__(args=args, first_url=first_url, hostname=hostname)
        self.base_url = get_base_url(first_url)
        # self.custom_headers.update(fake_headers)
        # Deep copy 4 different fake headers and use them as custom headers
        self.custom_header_pool: list[OrderedDict[str, str]] = []
        for header in fake_headers:
            new_headers = copy.deepcopy(self.custom_headers)
            new_headers.update(header)
            self.custom_header_pool.append(new_headers)

    def generate_request(
        self,
        worker_id: int,
        last_url: Optional[str],
        last_status_code: Optional[int],
    ) -> RequestInfo:
        method = HttpMethod.GET
        match worker_id % 4:
            case 0:
                # GET /api/home/list?page=1&pageSize=18&search=<random_string>
                path = "/api/home/list"
                params = f"?page=1&pageSize=18&search={random.randint(0, 10000)}"
            case 1:
                # GET /api/rating/<random_number>
                path = "/api/rating"
                params = f"/{random.randint(0, 10000)}"
            case 2:
                # GET /api/page/<random_number>
                path = "/api/page"
                params = f"/{random.randint(0, 10000)}"
            case 3:
                # POST /api/ranking/download/<random_number>
                path = "/api/ranking/download"
                params = f"/{random.randint(0, 10000)}"
                method = HttpMethod.POST
            case _:
                raise ValueError("Invalid worker_id")

        this_url = f"{self.base_url}{path}{params}"
        return RequestInfo(
            method=method,
            url=this_url,
            hostname=self.hostname,
            headers=random.choice(self.custom_header_pool),
            body=None
        )


ExportedProfile = AozoracafeProfile


fake_headers = [{
    "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "dnt": "1",
    "upgrade-insecure-requests": "1",
    "origin": "https://aozoracafe.com",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "referer": "https://aozoracafe.com/",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7,ja;q=0.6,zh-CN;q=0.5",
    "priority": "u=1, i",
}, {
    "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"macOS\"",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7,ja;q=0.6"
},
    {
    "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7,zh-CN;q=0.5"
},
    {
    "sec-ch-ua": "\"Chromium\";v=\"122\", \"Not(A:Brand\";v=\"24\", \"Google Chrome\";v=\"122\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "accept": "application/json, text/plain, */*",
    "sec-fetch-site": "same-site",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9,zh;q=0.7,ja;q=0.6,zh-CN;q=0.5"
}


]
