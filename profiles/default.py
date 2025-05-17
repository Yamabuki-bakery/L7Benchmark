

from mytypes import BaseProfile
from mytypes import Args, RequestInfo
from typing import Optional


class DefaultProfile(BaseProfile):
    """
    Default profile for generating requests.
    This class provides a basic behavior of following the command line arguments
    """
    def __init__(self, args: Args, first_url: str, hostname: str):
        """
        Initialize the DefaultProfile with the given arguments.
        """
        super().__init__(args=args, first_url=first_url, hostname=hostname)
        self.last_url: str = first_url
        self.last_status_code: int = 200
        

    def generate_request(self, 
          worker_id: int,
          last_url: Optional[str],
          last_status_code: Optional[int],        
        ) -> RequestInfo:
        """
        Generate a request based on the last URL and status code.
        """
        method = self.args.method
        this_url = self.last_url
        
        return RequestInfo(
            method=method,
            url=this_url,
            hostname=self.hostname,
            headers=self.custom_headers,
            body=None
        )
    
ExportedProfile = DefaultProfile