"""
SSRF Protection and URL Validation module.
Ensures requests are not made to internal networks, localhost, private subnets,
or cloud metadata endpoints.
"""

import ipaddress
import socket
from urllib.parse import urlparse

# Cloud metadata and internal hostnames
BLOCKED_HOSTNAMES = {
    "localhost",
    "metadata.google.internal",
    "metadata",
    "instance-data",
    "169.254.169.254",
}

# Dangerous port ranges (prevent hitting common internal services)
BLOCKED_PORTS = {22, 23, 25, 110, 143, 3306, 5432, 6379, 27017, 9200, 11211}

# Reserved / private IP networks to block
DISALLOWED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),          # Current network
    ipaddress.ip_network("10.0.0.0/8"),         # Private RFC1918
    ipaddress.ip_network("100.64.0.0/10"),      # Shared Address (CGNAT)
    ipaddress.ip_network("127.0.0.0/8"),        # Loopback
    ipaddress.ip_network("169.254.0.0/16"),     # Link Local / Cloud metadata
    ipaddress.ip_network("172.16.0.0/12"),      # Private RFC1918
    ipaddress.ip_network("192.0.0.0/24"),       # IETF Protocol Assignments
    ipaddress.ip_network("192.0.2.0/24"),       # TEST-NET-1
    ipaddress.ip_network("192.88.99.0/24"),     # 6to4 Relay Anycast
    ipaddress.ip_network("192.168.0.0/16"),     # Private RFC1918
    ipaddress.ip_network("198.18.0.0/15"),      # Network Interconnect Benchmarking
    ipaddress.ip_network("198.51.100.0/24"),    # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),     # TEST-NET-3
    ipaddress.ip_network("224.0.0.0/4"),        # Multicast
    ipaddress.ip_network("240.0.0.0/4"),        # Reserved for Future Use
    ipaddress.ip_network("255.255.255.255/32"), # Limited Broadcast
    # IPv6
    ipaddress.ip_network("::1/128"),            # Loopback
    ipaddress.ip_network("::/128"),             # Unspecified
    ipaddress.ip_network("fc00::/7"),           # Unique Local Address (ULA)
    ipaddress.ip_network("fe80::/10"),          # Link-local
    ipaddress.ip_network("ff00::/8"),           # Multicast
    ipaddress.ip_network("::ffff:0:0/96"),      # IPv4-mapped IPv6
]


def is_ip_disallowed(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Check if an IP address belongs to any restricted or private network."""
    # Handle IPv4-mapped IPv6
    if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped:
        ip = ip.ipv4_mapped

    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved or ip.is_unspecified:
        return True

    for net in DISALLOWED_NETWORKS:
        try:
            if ip in net:
                return True
        except TypeError:
            continue
    return False


def validate_url_ssrf(url: str, allow_test_local: bool = False) -> tuple[bool, str]:
    """
    Validate a URL for SSRF vulnerabilities and protocol correctness.
    Returns: (is_valid: bool, error_message: str)
    """
    if not url or not isinstance(url, str):
        return False, "URL cannot be empty."

    url = url.strip()
    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"Failed to parse URL: {e}"

    # Only HTTP and HTTPS
    if parsed.scheme.lower() not in ("http", "https"):
        return False, f"Invalid scheme '{parsed.scheme}'. Only http:// and https:// URLs are permitted."

    hostname = parsed.hostname
    if not hostname:
        return False, "URL must include a valid hostname (e.g. https://example.com)."

    hostname_lower = hostname.lower()

    if allow_test_local:
        # In test mode, allow localhost/127.0.0.1 for local mock server tests
        return True, ""

    # Check blocked hostnames
    if hostname_lower in BLOCKED_HOSTNAMES or hostname_lower.endswith(".localhost") or hostname_lower.endswith(".internal"):
        return False, f"Access to '{hostname}' is blocked for security reasons."

    # Check blocked ports
    if parsed.port and parsed.port in BLOCKED_PORTS:
        return False, f"Port {parsed.port} is blocked for security reasons."

    # Direct IP literal check
    try:
        direct_ip = ipaddress.ip_address(hostname_lower)
        if is_ip_disallowed(direct_ip):
            return False, f"Access to IP address '{hostname}' is restricted (internal/private address)."
    except ValueError:
        # Not a direct IP literal; perform DNS resolution check
        pass

    # Resolve hostname to all associated IPs to prevent DNS rebinding / private resolution
    try:
        addr_info = socket.getaddrinfo(hostname, parsed.port or (443 if parsed.scheme == "https" else 80), proto=socket.IPPROTO_TCP)
        if not addr_info:
            return False, f"Could not resolve host '{hostname}'."

        for entry in addr_info:
            ip_str = entry[4][0]
            try:
                ip = ipaddress.ip_address(ip_str)
                if is_ip_disallowed(ip):
                    return False, f"Resolved IP '{ip_str}' for host '{hostname}' is restricted."
            except ValueError:
                return False, f"Invalid IP returned for host '{hostname}': {ip_str}"

    except socket.gaierror as e:
        return False, f"DNS resolution failed for '{hostname}': {e.strerror or 'host not found'}."
    except Exception as e:
        return False, f"DNS validation error for '{hostname}': {e}"

    return True, ""
