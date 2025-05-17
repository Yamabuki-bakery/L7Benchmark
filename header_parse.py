import logging
from collections import OrderedDict

def parse_header(headers: list[str]) -> OrderedDict[str, str]:
    """
    Parse a list of headers into a dictionary.
    
    Args:
        headers: A list of strings representing headers in the format "Name: Value"
        
    Returns:
        A dictionary with header names as keys and header values as values
    """
    parsed_headers: OrderedDict[str, str] = OrderedDict()
    for header in headers:
        try:
            name, value = header.split(':', 1)
            # HTTP/2 While uppercase headers can be used at the application level, they will always be sent as lowercase.
            parsed_headers[name.strip().lower()] = value.strip()
        except ValueError:
            logging.warning(f"Invalid header format: {header}. Should be 'Name: Value'")
    return parsed_headers