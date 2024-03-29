#!/usr/bin/env python
# coding=utf-8

from namecheap import Api


class NamecheapDnsOps:
    def __init__(self, api_key, username, ip_address, sandbox, debug):
        self.api = Api(username, api_key, username, ip_address, sandbox=sandbox, debug=debug)

    def get_domain_records(self, domain):
        return self.api.domains_dns_getHosts(domain)

    def add_domain_record(self, domain, rr, record_type, value, ttl=1799, mxpref=10):
        record = {
            'Type': record_type,
            'Name': rr,
            'Address': value,
            'TTL': str(ttl),
            'MXPref': str(mxpref)
        }
        return self.api.domains_dns_addHost(domain, record)

    def delete_domain_record(self, domain, rr, record_type, value):
        record = {
            'Type': record_type,
            'Name': rr,
            'Address': value
        }
        return self.api.domains_dns_delHost(domain, record)
