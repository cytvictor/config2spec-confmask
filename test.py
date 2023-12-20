import re
ip_regex = "[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}"

acl_regex = ("^(?P<name>\S+):(?P<type>deny|permit)(\s+ip|\s+)"
            "(?P<source>any|host\s+{ip_regex}|{ip_regex}\s+{ip_regex})"
            "(\s+(?P<destination>any|host\s+{ip_regex}|{ip_regex}\s+{ip_regex})|)$"
                .format(ip_regex=ip_regex))
print(acl_regex)
line = "1:deny 2.128.3.0 0.0.0.255"
acl_match = re.match(acl_regex, line)
if acl_match is None:
    acl_data = {}
else:
    acl_data = acl_match.groupdict()
print(acl_data)
print(acl_data['source'].split()[1])
# source = TopologyBuilder.get_prefix(acl_data["source"])
# destination = TopologyBuilder.get_prefix(acl_data["destination"])
