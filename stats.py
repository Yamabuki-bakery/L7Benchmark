import asyncio

class Stats:
    def __init__(self):
        self._2xx_requests = 0
        self._3xx_requests = 0
        self._4xx_requests = 0
        self._5xx_requests = 0
        self.other_requests = 0
        self.download_bytes = 0
        self.upload_bytes = 0
        self.mutex = asyncio.Lock()

    async def reset(self):
        """ Reset all statistics to zero. """
        async with self.mutex:
            self._2xx_requests = 0
            self._3xx_requests = 0
            self._4xx_requests = 0
            self._5xx_requests = 0
            self.other_requests = 0
            self.download_bytes = 0
            self.upload_bytes = 0


    async def add_download_bytes(self, bytes: int):
        """ Add bytes to the download statistics.
        Args:
            bytes (int): The number of bytes to add to the download statistics.
        """
        async with self.mutex:
            self.download_bytes += bytes

    async def add_upload_bytes(self, bytes: int):
        """ Add bytes to the upload statistics.
        Args:
            bytes (int): The number of bytes to add to the upload statistics.
        """
        async with self.mutex:
            self.upload_bytes += bytes

    async def add_request(self, status_code: int):
        """ Categorize the request based on its status code.

        Args:
            status_code (int): The HTTP status code of the response.
            -1 for unknown status codes
        """
        async with self.mutex:
            if 200 <= status_code < 300:
                self._2xx_requests += 1
            elif 300 <= status_code < 400:
                self._3xx_requests += 1
            elif 400 <= status_code < 500:
                self._4xx_requests += 1
            elif 500 <= status_code < 600:
                self._5xx_requests += 1
            else:
                self.other_requests += 1

    def sum_requests(self) -> int:
        """ Calculate the total number of requests.

        Returns:
            int: The total number of requests.
        """
        return self._2xx_requests + self._3xx_requests + self._4xx_requests + self._5xx_requests + self.other_requests
    
    def get_2xx_requests(self) -> int:
        """ Get the number of 2xx requests.

        Returns:
            int: The number of 2xx requests.
        """
        return self._2xx_requests
    def get_3xx_requests(self) -> int:
        """ Get the number of 3xx requests.
        Returns:
            int: The number of 3xx requests.
        """
        return self._3xx_requests
    def get_4xx_requests(self) -> int:
        """ Get the number of 4xx requests.
        Returns:
            int: The number of 4xx requests.
        """
        return self._4xx_requests
    def get_5xx_requests(self) -> int:
        """ Get the number of 5xx requests.
        Returns:
            int: The number of 5xx requests.
        """
        return self._5xx_requests
    def get_other_requests(self) -> int:
        """ Get the number of other requests.
        Returns:
            int: The number of other requests.
        """
        return self.other_requests