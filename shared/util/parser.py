import re
import ipaddress
from typing import List

IP_PATTERN = re.compile(r'^(\d{1,3}(?:\.\d{1,3}){3})(?:\/(\d{1,2})|\-(\d{1,3}))?$')

def parse_ips(addresses: str, split_cidr: bool = False) -> List[str]:
    # 192.168.0.2-10, 192.168.1.0/24, 192.168.2.2
    # split on commas
    unique_entries = []

    cidrs = set()
    individuals = set()

    parts = [p.strip() for p in addresses.split(',')]

    for part in parts:
        match = IP_PATTERN.match(part)
        if not match:
            # TODO: invalid formatting
            continue

        base_ip, cidr_bits, range_end = match.groups()

        # Handle IPs in CIDR notation
        if cidr_bits:
            try:
                net = ipaddress.ip_network(part, strict=False)
                # If the user specified to split CIDR get each ip address
                if split_cidr:
                    for ip in [cidr for cidr in net]:
                        individuals.add(ip)
                else:
                    cidrs.add(str(net))
            except ValueError:
                #TODO: invalid CIDR?
                continue
    
        elif range_end:
            # prefix, start_octet = base_ip.rsplit('.', 1)
            # start_num, end_num = int(start_val), int(range_end)
            prefix, hosts = base_ip.rsplit('.', 1)
            l, r = hosts.split('-', 1)
            beg = int(l)
            end = int(r)
        
            if beg < end <= 255:
                for i in range(beg, end + 1):
                    individuals.add(f"{prefix}.{i}")
            else:
                # TODO: invalid range
                pass
        else:
            individuals.add(base_ip)

    # Combining individual and CIDR addresses only necessary if we do not split the CIDRS
    if not split_cidr:
        # Keep only individual IPs that are not covered by a CIDR
        for ip in individuals:
            ip_obj = ipaddress.ip_address(ip)
            if not any(ip_obj in net for net in cidrs):
                unique_entries.append(ip)

        # Append each CIDR entry
        for cidr in cidrs:
            unique_entries.append(str(cidr))

    # Sort the list numerically
    return sorted(unique_entries, key=lambda x: ipaddress.ip_address(x.split('/')[0]))