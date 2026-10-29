"""
Unit tests for SSRF protection and URL validation.
"""

from unittest.mock import patch
import socket
from crawler.ssrf import validate_url_ssrf, is_ip_disallowed


def mock_getaddrinfo(host, port, *args, **kwargs):
    # Mock DNS lookup for testing without relying on live external DNS
    if host in ("example.com", "www.google.com", "github.com"):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("93.184.216.34", port))]
    if host == "malicious-internal.test":
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.168.1.50", port))]
    raise socket.gaierror(socket.EAI_NONAME, "Name or service not known")


def test_valid_public_urls():
    valid_urls = [
        "https://example.com",
        "https://www.google.com/search?q=test",
        "http://github.com/torvalds/linux",
    ]
    with patch("socket.getaddrinfo", side_effect=mock_getaddrinfo):
        for url in valid_urls:
            is_safe, msg = validate_url_ssrf(url)
            assert is_safe is True, f"Failed for {url}: {msg}"


def test_blocked_schemes():
    invalid_schemes = [
        "ftp://example.com",
        "file:///etc/passwd",
        "gopher://example.com",
        "javascript:alert(1)",
        "data:text/html,<html></html>",
        "",
        "not_a_url",
    ]
    for url in invalid_schemes:
        is_safe, msg = validate_url_ssrf(url)
        assert is_safe is False
        assert len(msg) > 0


def test_ssrf_localhost_and_loopback():
    loopbacks = [
        "http://localhost",
        "http://localhost:8080",
        "http://127.0.0.1",
        "http://127.0.0.2:3000",
        "http://[::1]",
        "http://sub.localhost",
    ]
    for url in loopbacks:
        is_safe, msg = validate_url_ssrf(url)
        assert is_safe is False, f"Loopback not blocked: {url}"


def test_ssrf_private_and_cloud_metadata():
    private_targets = [
        "http://169.254.169.254/latest/meta-data/",
        "http://metadata.google.internal/computeMetadata/v1/",
        "http://10.0.0.1",
        "http://10.255.255.255",
        "http://172.16.0.1",
        "http://172.31.255.255",
        "http://192.168.1.1",
        "http://192.168.0.254",
        "http://100.64.0.1",  # CGNAT
    ]
    for url in private_targets:
        is_safe, msg = validate_url_ssrf(url)
        assert is_safe is False, f"Private/metadata endpoint not blocked: {url}"


def test_ssrf_dns_rebinding_to_private_ip():
    with patch("socket.getaddrinfo", side_effect=mock_getaddrinfo):
        is_safe, msg = validate_url_ssrf("http://malicious-internal.test")
        assert is_safe is False
        assert "restricted" in msg


def test_blocked_internal_ports():
    ports_urls = [
        "http://example.com:22",
        "http://example.com:3306",
        "http://example.com:6379",
        "http://example.com:27017",
    ]
    for url in ports_urls:
        is_safe, msg = validate_url_ssrf(url)
        assert is_safe is False


def test_allow_test_local_flag():
    is_safe, _ = validate_url_ssrf("http://127.0.0.1:8000", allow_test_local=True)
    assert is_safe is True
