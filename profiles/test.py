from mytypes import BaseProfile, HttpMethod
from mytypes import Args, RequestInfo
from typing import Optional
import random

from urlparse import get_base_url

class TestRandomProfile(BaseProfile):
    def __init__(self, args: Args, first_url: str, hostname: str):
        super().__init__(args=args, first_url=first_url, hostname=hostname)
        self.last_url: str = first_url
        self.last_status_code: int = 200

    def generate_request(
        self, 
        worker_id: int,
        last_url: Optional[str],
        last_status_code: Optional[int],        
    ) -> RequestInfo:
        base_url = get_base_url(self.first_url)
        path = random.choice(["/", "/path2", "/path3"])
        
        return RequestInfo(
            method=HttpMethod.GET,
            url=f"{base_url}{path}",
            hostname=self.hostname,
            headers=self.custom_headers,
            body=None
        )
    

ExportedProfile = TestRandomProfile