#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function

import sys
import yaml
from dns_ops import NamecheapDnsOps


def load_namecheap_conf(path):
    with open(path) as fp:
        return yaml.load(fp, Loader=yaml.FullLoader)

def build_ops_client_from_root_config(namecheap_conf):
    api_key = namecheap_conf.get("accessKey").get("namecheap").get("api_key")
    username = namecheap_conf.get("accessKey").get("namecheap").get("username")
    ip = namecheap_conf.get("accessKey").get("namecheap").get("ip")
    sandbox = namecheap_conf.get("accessKey").get("namecheap").get("sandbox")
    return NamecheapDnsOps(api_key, username, ip, sandbox)

def load_and_update_dns_config(cfg_path):
    namecheap_conf = load_namecheap_conf(cfg_path)
    ops = build_ops_client_from_root_config(namecheap_conf)

    for config in namecheap_conf.get("dns"):
        domain = config.get("domain")
        online_records = ops.get_domain_records(domain)
        for record in config.get("records"):
            rr = record.get("rr")
            record_type = record.get("type")
            value = record.get("value")
            ttl = record.get("ttl")

            matches_records = _find_matches_records(online_records, rr, record_type)

            # create record if not exists
            while len(matches_records) == 0 or matches_records[0]['Address'] != value:
                print("try add record [{}] {}.{} -> {}".format(record_type, rr, domain, value))
                print(ops.add_domain_record(domain, rr, record_type, value, ttl))
                online_records = ops.get_domain_records(domain)
                matches_records = _find_matches_records(online_records, rr, record_type)
            print("status now [{}] {}.{} -> {}".format(record_type, rr, domain, value))

    print("Done.")


def show_online_config(cfg_path):
    namecheap_conf = load_namecheap_conf(cfg_path)
    ops = build_ops_client_from_root_config(namecheap_conf)

    for config in namecheap_conf.get("dns"):
        domain = config.get("domain")
        online_records = ops.get_domain_records(domain)

        for record in config.get("records"):
            rr = record.get("rr")
            record_type = record.get("type")
            _print_matches_records(online_records, domain, rr, record_type)

    print("End.")

def _print_matches_records(records, domain, rr, record_type):
    matches_records = _find_matches_records(records, rr, record_type)
    if len(matches_records) == 0:
        print("status now [{}] {}.{} -> nil".format(record_type, rr, domain))

    for record in matches_records:
        print("status now [{}] {}.{} -> {}, TTL: {}s".format(record_type, rr, domain, record['Address'], record['TTL']))

def _find_matches_records(records, rr, record_type):
    return [record for record in records if record['Type'] == record_type and record['Name'] == rr]


guide = '''\
Usage:
    namecheap-dns-manager <command> [/path/to/dns/config]

Commands:
    status    show current dns status
    update    load dns config from local, flush local config to namecheap
'''


def main():
    params = sys.argv[1:]

    if len(params) < 2:
        print(guide)
        return

    command = params[0]
    cfg_path = params[1]

    if command == 'update':
        load_and_update_dns_config(cfg_path)
    elif command == 'status':
        show_online_config(cfg_path)
    else:
        print("unknown command", command)


if __name__ == '__main__':
    main()
