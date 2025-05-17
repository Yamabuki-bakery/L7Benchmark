import socket
from result import Ok, Err, Result

def resolve_hostname(hostname: str) -> Result[list[str], str]:
    """
    Resolves a hostname to a list of IP addresses.
    
    Args:
        hostname (str): The hostname to resolve.
        
    Returns:
        list: A list of IP addresses as strings.
    """
    try:
        # Get address info for the hostname
        addr_info = socket.getaddrinfo(hostname, None)
        
        # Extract unique IP addresses
        ip_addresses: list[str] = []
        for addr in addr_info:
            ip: str = addr[4][0]  # type: ignore # The IP address is in position 4, index 0
            if ip not in ip_addresses:
                ip_addresses.append(ip)
        
        return Ok(ip_addresses)
    except socket.gaierror:
        # Handle case where hostname cannot be resolved
        # print(f"Could not resolve hostname: {hostname}")
        return Err(f"Could not resolve hostname: {hostname}")

