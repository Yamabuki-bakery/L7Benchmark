import asyncio, time
from typing import Callable

class Stats:
    def __init__(self):
        self.resp_records : dict[int, int] = {}  # -1 for timeout, -2 for unknown error
        self.req_sent = 0
        self.mutex = asyncio.Lock()

    async def reset(self):
        """ Reset all statistics to zero. """
        async with self.mutex:
            self.resp_records = {}

    async def add_req(self):
        """ Increment the number of requests sent. """
        async with self.mutex:
            self.req_sent += 1

    async def add_resp(self, status_code: int):
        """ Categorize the response based on its status code.

        Args:
            status_code (int): The HTTP status code of the response.
            -1 for unknown status codes
        """
        async with self.mutex:
            if status_code not in self.resp_records:
                self.resp_records[status_code] = 0
            self.resp_records[status_code] += 1

    def sum_requests(self) -> int:
        """ Calculate the total number of requests.

        Returns:
            int: The total number of requests.
        """
        return sum(self.resp_records.values())
    
    
    def get_2xx_requests(self) -> int:
        """ Get the number of 2xx requests.

        Returns:
            int: The number of 2xx requests.
        """
        return sum([v for k, v in self.resp_records.items() if 200 <= k < 300])
    
    def get_3xx_requests(self) -> int:
        """ Get the number of 3xx requests.
        Returns:
            int: The number of 3xx requests.
        """
        return sum([v for k, v in self.resp_records.items() if 300 <= k < 400])
    
    def get_4xx_requests(self) -> int:
        """ Get the number of 4xx requests.
        Returns:
            int: The number of 4xx requests.
        """
        return sum([v for k, v in self.resp_records.items() if 400 <= k < 500])
    
    def get_5xx_requests(self) -> int:
        """ Get the number of 5xx requests.
        Returns:
            int: The number of 5xx requests.
        """
        return sum([v for k, v in self.resp_records.items() if 500 <= k < 600])
    
    def get_timeout_requests(self) -> int:
        """ Get the number of timeout requests.
        Returns:
            int: The number of timeout requests.
        """
        return self.resp_records.get(-1, 0)
    
    async def print_stats(
            self, 
            end_time: float,
            sum_connection: Callable[[], int] 
            ) -> None:
        self.next = True
        start = time.time()
        while time.time() < end_time:
            await asyncio.sleep(0.25)
            # Sort the status codes and print non-zero values
            status_codes = sorted([k for k in self.resp_records.keys() if k > 0])
            status_str_parts: list[str] = []
            
            # Add the req/resp summary
            status_str_parts.append(
                f"{'🌕' if self.next else '🌑'}Req/Resp/Conn: {self.req_sent}/{self.sum_requests()}/{sum_connection()}"
            )
            
            # Add individual status codes
            for code in status_codes:
                count = self.resp_records[code]
                color: str = ''
                if 200 <= code < 300:
                    color = '🟢'
                elif 300 <= code < 400:
                    color = '🟡'
                elif 400 <= code < 500:
                    color = '🔴'
                elif 500 <= code < 600:
                    color = '🟣'
                else:
                    color = ''
                if count > 0:
                    status_str_parts.append(f"{color}{code}: {count}")
            
            # Add timeout count if any
            timeout_count = self.get_timeout_requests()
            if timeout_count > 0:
                status_str_parts.append(f"Timeout: {timeout_count}")

            # Add unknown error count if any
            unknown_count = self.resp_records.get(-2, 0)
            if unknown_count > 0:
                status_str_parts.append(f"❌Err: {unknown_count}")

            # show elapsed time
            elapsed = time.time() - start
            status_str_parts.append(f"🕑Elapsed: {elapsed:.2f}s")
            
            # Join all parts with separator and print
            status_str = " | ".join(status_str_parts)
            print("\r" + status_str, end="")
            self.next = not self.next

