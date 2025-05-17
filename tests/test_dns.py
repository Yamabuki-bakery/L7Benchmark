import unittest
import socket
from dns import resolve_hostname
from result import Ok, Err

class TestDNSResolver(unittest.TestCase):
    
    def test_resolve_valid_ipv4_domain(self):
        """Test resolving a domain that should have IPv4 addresses"""
        result = resolve_hostname("ipv4.google.com")
        self.assertTrue(isinstance(result, Ok))
        self.assertTrue(len(result.value) > 0)
        # Check that at least one IPv4 address is returned
        ipv4_found = any('.' in ip for ip in result.value)
        self.assertTrue(ipv4_found)
    
    def test_resolve_google(self):
        """Test resolving www.google.com which should have both IPv4 and possibly IPv6"""
        result = resolve_hostname("www.google.com")
        self.assertTrue(isinstance(result, Ok))
        self.assertTrue(len(result.value) > 0)
        # Google should always resolve to something
        self.assertGreater(len(result.value), 0)
    
    def test_resolve_ipv6_domain(self):
        """Test resolving a domain with IPv6 support"""
        # IPv6 test (may be skipped if the system doesn't support IPv6)
        has_ipv6 = False
        try:
            # Try to create an IPv6 socket to check if IPv6 is supported
            socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
            has_ipv6 = True
        except socket.error:
            pass
        
        if has_ipv6:
            # ipv6.google.com should return IPv6 addresses
            result = resolve_hostname("ipv6.google.com")
            self.assertTrue(isinstance(result, Ok))
            # Check if at least one IPv6 address is returned
            ipv6_found = any(':' in ip for ip in result.value)
            self.assertTrue(ipv6_found)
        else:
            print("IPv6 is not supported on this system. Skipping IPv6 test.")
    
    def test_resolve_invalid_domain(self):
        """Test resolving a non-existent domain"""
        result = resolve_hostname("this-domain-does-not-exist-12345.com")
        self.assertTrue(isinstance(result, Err))
        self.assertIn("Could not resolve hostname", result.value)
    
    def test_localhost_resolution(self):
        """Test resolving localhost which should return at least 127.0.0.1"""
        result = resolve_hostname("localhost")
        self.assertTrue(isinstance(result, Ok))
        self.assertIn("127.0.0.1", result.value)

if __name__ == "__main__":
    unittest.main()
