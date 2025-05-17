from urllib.parse import urlparse, urlunparse
import ipaddress
from result import Result, Ok, Err
from typing import Optional, Tuple
import logging
from dns import resolve_hostname


def modify_hostname(url: str, new_hostname: str) -> Result[str, str]:
    """
    Parse a URL string, modify the hostname, and return the modified URL.
    
    Args:
        url: The original URL string
        new_hostname: The new hostname to replace the original one
        
    Returns:
        A new URL string with the modified hostname
    """
    # Parse the URL into components
    parsed_url = urlparse(url)

    # Check if the new hostname is an IPv6 address
    try:
        ip = ipaddress.ip_address(new_hostname)
        is_ipv6 = ip.version == 6
    except ValueError:
        is_ipv6 = False

    # Create new netloc (hostname:port)
    if is_ipv6:
        if parsed_url.port:
            new_netloc = f"[{new_hostname}]:{parsed_url.port}"
        else:
            new_netloc = f"[{new_hostname}]"
    else:
        if parsed_url.port:
            new_netloc = f"{new_hostname}:{parsed_url.port}"
        else:
            new_netloc = new_hostname
    
    # Create a new set of components with the modified hostname
    modified_components = parsed_url._replace(netloc=new_netloc)
    
    # Convert the components back to a URL string
    modified_url = urlunparse(modified_components)
    
    return Ok(modified_url)


def extract_hostname(url: str) -> Result[str, str]:
    """
    Extract the hostname from a URL string.
    
    Args:
        url: The URL string
        
    Returns:
        The hostname as a string
    """
    parsed_url = urlparse(url)
    if parsed_url.hostname:
        return Ok(parsed_url.hostname)
    else:
        return Err("Invalid URL: No hostname found")
    

def is_ipaddress(hostname: str) -> bool:
    """
    Check if the given hostname is an IP address (IPv4 or IPv6).
    
    Args:
        hostname: The hostname to check
        
    Returns:
        True if the hostname is an IP address, False otherwise
    """
    try:
        ipaddress.ip_address(hostname)
        return True
    except ValueError:
        return False


async def generate_new_url_and_hostname(origin_url: str, ip: Optional[str]) -> Result[Tuple[str, str], str]:
    """
    Generate a new URL and hostname based on the original URL and IP address.
    
    Args:
        origin_url: The original URL string
        ip: The override IP address (if any)
    
    Returns:
        A Result containing the new URL and hostname, or an error message
    """
    hostname = extract_hostname(origin_url)
    match hostname:
        case Ok(hostname):
            logging.info(f"Extracted hostname: {hostname}")
        case Err(e):
            logging.error(f"Error extracting hostname: {e}")
            return Err(e)
        
    new_url = origin_url
    if ip:
        # 不需要 resolve 了，構造新的 URL 和 Host header
        new_url = modify_hostname(origin_url, ip)
        match new_url:
            case Ok(new_url):
                logging.debug(f"Modified URL: {new_url}")
            case Err(e):
                logging.error(f"Error modifying URL: {e}")
                return Err(e)
    else:
        # 使用 DNS 解析
        result = resolve_hostname(hostname)
        match result:
            case Ok(ip_addresses):
                logging.info(f"Resolved IP addresses: {ip_addresses}")
                if len(ip_addresses) == 0:
                    logging.error("No IP addresses found")
                    return Err("No IP addresses found")
                new_url = modify_hostname(origin_url, ip_addresses[0])
                match new_url:
                    case Ok(new_url):
                        logging.debug(f"Modified URL: {new_url}")
                    case Err(e):
                        logging.error(f"Error modifying URL: {e}")
                        return Err(e)
            case Err(e):
                logging.error(f"Error resolving hostname: {e}")
                return Err(e)
    return Ok((new_url, hostname))


def get_base_url(url: str) -> str:
    """
    Get the base URL from a full URL.
    
    Args:
        url: The full URL string
        
    Returns:
        The base URL string
    """
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def get_path(url: str) -> str:
    """
    Get the path from a full URL.
    """
    parsed_url = urlparse(url)
    return parsed_url.path
