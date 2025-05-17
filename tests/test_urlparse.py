import unittest
from urlparse import modify_hostname, extract_hostname, is_ipaddress, get_base_url, get_path

class TestModifyHostname(unittest.TestCase):
    def test_replace_with_hostname_no_port(self):
        # Test replacing a hostname without a port
        original_url = "https://example.com/path?query=value#fragment"
        new_hostname = "newhost.com"
        expected_url = "https://newhost.com/path?query=value#fragment"
        
        result = modify_hostname(original_url, new_hostname)
        self.assertTrue(result.is_ok())
        self.assertEqual(result.unwrap(), expected_url)
        
    def test_replace_with_hostname_with_port(self):
        # Test replacing a hostname with a port
        original_url = "https://example.com:8443/path?query=value#fragment"
        new_hostname = "newhost.com"
        expected_url = "https://newhost.com:8443/path?query=value#fragment"
        
        result = modify_hostname(original_url, new_hostname)
        self.assertTrue(result.is_ok())
        self.assertEqual(result.unwrap(), expected_url)

    def test_replace_with_ipv4_no_port(self):
        # Test replacing a hostname with an IPv4 address without a port
        original_url = "https://example.com/path?query=value#fragment"
        new_hostname = "192.168.1.1"
        expected_url = "https://192.168.1.1/path?query=value#fragment"
        
        result = modify_hostname(original_url, new_hostname)
        self.assertTrue(result.is_ok())
        self.assertEqual(result.unwrap(), expected_url)
    
    def test_replace_with_ipv4_with_port(self):
        # Test replacing a hostname with an IPv4 address with a port
        original_url = "https://example.com:8443/path?query=value#fragment"
        new_hostname = "192.168.1.1"
        expected_url = "https://192.168.1.1:8443/path?query=value#fragment"
        
        result = modify_hostname(original_url, new_hostname)
        self.assertTrue(result.is_ok())
        self.assertEqual(result.unwrap(), expected_url)
    
    def test_replace_with_ipv6_no_port(self):
        # Test replacing a hostname with an IPv6 address without a port
        original_url = "https://example.com/path?query=value#fragment"
        new_hostname = "2001:db8::1"
        expected_url = "https://[2001:db8::1]/path?query=value#fragment"
        
        result = modify_hostname(original_url, new_hostname)
        self.assertTrue(result.is_ok())
        self.assertEqual(result.unwrap(), expected_url)
    
    def test_replace_with_ipv6_with_port(self):
        # Test replacing a hostname with an IPv6 address with a port
        original_url = "https://example.com:8443/path?query=value#fragment"
        new_hostname = "2001:db8::1"
        expected_url = "https://[2001:db8::1]:8443/path?query=value#fragment"
        
        result = modify_hostname(original_url, new_hostname)
        self.assertTrue(result.is_ok())
        self.assertEqual(result.unwrap(), expected_url)
    
    def test_replace_ipv4_with_ipv6(self):
        # Test replacing an IPv4 address with an IPv6 address
        original_url = "http://192.168.0.1/api"
        new_hostname = "2001:db8::1"
        expected_url = "http://[2001:db8::1]/api"
        
        result = modify_hostname(original_url, new_hostname)
        self.assertTrue(result.is_ok())
        self.assertEqual(result.unwrap(), expected_url)
    
    def test_replace_ipv6_with_ipv4(self):
        # Test replacing an IPv6 address with an IPv4 address
        original_url = "http://[2001:db8::1]/api"
        new_hostname = "192.168.1.1"
        expected_url = "http://192.168.1.1/api"
        
        result = modify_hostname(original_url, new_hostname)
        self.assertTrue(result.is_ok())
        self.assertEqual(result.unwrap(), expected_url)
    
    def test_replace_ipv6_with_ipv6(self):
        # Test replacing an IPv6 address with another IPv6 address
        original_url = "http://[2001:db8::1]/api"
        new_hostname = "2001:db8::2"
        expected_url = "http://[2001:db8::2]/api"
        
        result = modify_hostname(original_url, new_hostname)
        self.assertTrue(result.is_ok())
        self.assertEqual(result.unwrap(), expected_url)

    def test_preserve_scheme_and_path(self):
        # Test that scheme and path are preserved
        original_url = "ftp://example.com/downloads/file.zip"
        new_hostname = "192.168.1.1"
        expected_url = "ftp://192.168.1.1/downloads/file.zip"
        
        result = modify_hostname(original_url, new_hostname)
        self.assertTrue(result.is_ok())
        self.assertEqual(result.unwrap(), expected_url)

class TestExtractHostname(unittest.TestCase):
    def test_extract_regular_hostname(self):
        # Test extracting a regular hostname
        url = "https://example.com/path?query=value#fragment"
        expected_hostname = "example.com"
        
        result = extract_hostname(url)
        self.assertTrue(result.is_ok())
        self.assertEqual(result.unwrap(), expected_hostname)
    
    def test_extract_hostname_with_port(self):
        # Test extracting a hostname from URL with port
        url = "https://example.org:8443/path"
        expected_hostname = "example.org"
        
        result = extract_hostname(url)
        self.assertTrue(result.is_ok())
        self.assertEqual(result.unwrap(), expected_hostname)
    
    def test_extract_ipv4_hostname(self):
        # Test extracting an IPv4 address
        url = "http://192.168.1.1/api"
        expected_hostname = "192.168.1.1"
        
        result = extract_hostname(url)
        self.assertTrue(result.is_ok())
        self.assertEqual(result.unwrap(), expected_hostname)
    
    def test_extract_ipv6_hostname(self):
        # Test extracting an IPv6 address
        url = "http://[2001:db8::1]/api"
        expected_hostname = "2001:db8::1"
        
        result = extract_hostname(url)
        self.assertTrue(result.is_ok())
        self.assertEqual(result.unwrap(), expected_hostname)
    
    def test_extract_ipv6_hostname_with_port(self):
        # Test extracting an IPv6 address with port
        url = "https://[2001:db8::1]:8443/secure"
        expected_hostname = "2001:db8::1"
        
        result = extract_hostname(url)
        self.assertTrue(result.is_ok())
        self.assertEqual(result.unwrap(), expected_hostname)
    
    def test_extract_hostname_subdomain(self):
        # Test extracting a hostname with subdomains
        url = "https://api.subdomain.example.com/v2/resource"
        expected_hostname = "api.subdomain.example.com"
        
        result = extract_hostname(url)
        self.assertTrue(result.is_ok())
        self.assertEqual(result.unwrap(), expected_hostname)
    
    def test_extract_invalid_url(self):
        # Test extracting hostname from an invalid URL
        url = "not a valid url"
        
        result = extract_hostname(url)
        self.assertTrue(result.is_err())
        self.assertEqual(result.unwrap_err(), "Invalid URL: No hostname found")
    
    def test_extract_url_without_hostname(self):
        # Test extracting from a URL without hostname
        url = "file:///path/to/file.txt"
        
        result = extract_hostname(url)
        self.assertTrue(result.is_err())
        self.assertEqual(result.unwrap_err(), "Invalid URL: No hostname found")


class TestIsIpaddress(unittest.TestCase):
    def test_is_ipv4(self):
        # Test with a valid IPv4 address
        self.assertTrue(is_ipaddress("1.1.1.1"))

    def test_is_ipv6(self):
        # Test with a valid IPv6 address
        self.assertTrue(is_ipaddress("2001:0db8:85a3:0000:0000:8a2e:0370:7334"))

    def test_is_not_ip(self):
        # Test with a non-IP address
        self.assertFalse(is_ipaddress("example.com"))


class TestUrlHelpers(unittest.TestCase):
    def test_get_base_url_with_standard_url(self):
        # Test with a standard URL
        url = "https://example.com/path/to/resource?query=value#fragment"
        expected = "https://example.com"
        self.assertEqual(get_base_url(url), expected)
    
    def test_get_base_url_with_port(self):
        # Test with a URL that includes a port
        url = "https://example.com:8443/path/to/resource"
        expected = "https://example.com:8443"
        self.assertEqual(get_base_url(url), expected)
    
    def test_get_base_url_with_ipv4(self):
        # Test with an IPv4 address
        url = "http://192.168.1.1/api/endpoint"
        expected = "http://192.168.1.1"
        self.assertEqual(get_base_url(url), expected)
    
    def test_get_base_url_with_ipv6(self):
        # Test with an IPv6 address
        url = "http://[2001:db8::1]/api/endpoint"
        expected = "http://[2001:db8::1]"
        self.assertEqual(get_base_url(url), expected)
    
    def test_get_base_url_with_subdomain(self):
        # Test with a subdomain
        url = "https://api.example.com/v1/resource"
        expected = "https://api.example.com"
        self.assertEqual(get_base_url(url), expected)
    
    def test_get_base_url_without_path(self):
        # Test with a URL without a path
        url = "https://example.com"
        expected = "https://example.com"
        self.assertEqual(get_base_url(url), expected)
    
    def test_get_path_with_standard_url(self):
        # Test with a standard URL
        url = "https://example.com/path/to/resource?query=value#fragment"
        expected = "/path/to/resource"
        self.assertEqual(get_path(url), expected)
    
    def test_get_path_without_path(self):
        # Test with a URL without a path
        url = "https://example.com"
        expected = ""
        self.assertEqual(get_path(url), expected)
    
    def test_get_path_with_root_path(self):
        # Test with a URL with just a root path
        url = "https://example.com/?query=value"
        expected = "/"
        self.assertEqual(get_path(url), expected)
    
    def test_get_path_with_complex_path(self):
        # Test with a URL containing a complex path
        url = "https://example.com/api/v2/users/123/profile"
        expected = "/api/v2/users/123/profile"
        self.assertEqual(get_path(url), expected)


if __name__ == "__main__":
    unittest.main()
