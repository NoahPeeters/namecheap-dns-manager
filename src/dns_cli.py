#!/usr/bin/env python
# coding=utf-8

from __future__ import print_function

import sys
import yaml
from . dns_ops import NamecheapDnsOps


def load_namecheap_conf(path):
    with open(path) as fp:
        return yaml.load(fp, Loader=yaml.FullLoader)

def build_ops_client_from_root_config(namecheap_conf):
    api_key = namecheap_conf.get("accessKey").get("namecheap").get("api_key")
    username = namecheap_conf.get("accessKey").get("namecheap").get("username")
    ip = namecheap_conf.get("accessKey").get("namecheap").get("ip")
    sandbox = namecheap_conf.get("accessKey").get("namecheap").get("sandbox")
    debug = namecheap_conf.get("accessKey").get("namecheap").get("debug")
    return NamecheapDnsOps(api_key, username, ip, sandbox, debug)

def _load_dns_records(config):
    newRecords = []
    for record in config.get("records"):
        rr = record.get("rr")
        record_type = record.get("type")
        values = record.get("value")

        if not isinstance(values, list):
            values = [values]


        for value in values:
            address = None
            ttl = None
            mxpref = None
            if isinstance(value, str):
                address = value
            else:
                address = value.get('value')
                ttl = value.get("ttl")
                mxpref = value.get('mxpref')

            if ttl == None:
                ttl = 1799
            if mxpref == None:
                mxpref = 10

            newRecords.append({
                'Name': rr,
                'Type': record_type,
                'Address': address,
                'TTL': ttl,
                'MXPref': mxpref
            })
        
    return newRecords

def _matches(local, online):
    return local['Name'] == online['Name'] and \
           local['Type'] == online['Type'] and \
           local['Address'] == online['Address'] and \
           str(local['TTL']) == online['TTL'] and \
           str(local['MXPref']) == online['MXPref']

def load_and_update_dns_config(cfg_path, dryrun):
    namecheap_conf = load_namecheap_conf(cfg_path)
    ops = build_ops_client_from_root_config(namecheap_conf)

    for config in namecheap_conf.get("dns"):
        domain = config.get("domain")
        online_records = ops.get_domain_records(domain)

        records = _load_dns_records(config)

        # delete old ones
        for online_record in online_records:
            found_match = False
            for record in records:
                if _matches(record, online_record):
                    found_match = True

            if not found_match:
                print_record("deleting", domain, online_record)
                if not dryrun:
                    ops.delete_domain_record(domain, record["Name"], record["Type"], record["Address"])
        
        # adding new ones
        for record in records:
            found_match = False
            for online_record in online_records:
                if _matches(record, online_record):
                    found_match = True

            if not found_match:
                print_record("adding  ", domain, record)
                if not dryrun:
                    print(ops.add_domain_record(domain, record["Name"], record["Type"], record["Address"], record["TTL"], record["MXPref"]))
    print("Done.")


def show_online_config(cfg_path):
    namecheap_conf = load_namecheap_conf(cfg_path)
    ops = build_ops_client_from_root_config(namecheap_conf)

    for config in namecheap_conf.get("dns"):
        domain = config.get("domain")
        online_records = ops.get_domain_records(domain)

        for record in online_records:
            print_record("status now", domain, record)
            

    print("End.")

def print_record(prefix, domain, record):
    if record["Type"] == "MX" and record["MXPref"]:
        print("{} [{}] {}.{} -> {} Pref: {}, TTL: {}s"
            .format(prefix, record["Type"], record["Name"], domain, record["Address"], record["MXPref"], record["TTL"]))
    else:
        print("{} [{}] {}.{} -> {} TTL: {}s"
            .format(prefix, record["Type"], record["Name"], domain, record["Address"], record["TTL"]))

def _print_matches_records(records, domain, rr, record_type):
    matches_records = _find_matches_records(records, rr, record_type)
    if not matches_records:
        print("status now [{}] {}.{} -> nil".format(record_type, rr, domain))

    for record in matches_records:
        print("status now [{}] {}.{} -> {} TTL: {}s"
              .format(record_type, rr, domain, record['Address'], record['TTL']))

def _find_matches_records(records, rr, record_type):
    return [record for record in records if record['Type'] == record_type and record['Name'] == rr]


GUIDE_DOC = '''\
Usage:
    namecheap-dns-manager <command> [/path/to/dns/config]

Commands:
    status    show current dns status
    update    load dns config from local, flush local config to namecheap
    dryrun    print what would be done during a dryrun
'''


def main():
    params = sys.argv[1:]

    if len(params) < 2:
        print(GUIDE_DOC)
        return

    command = params[0]
    cfg_path = params[1]

    if command == 'update':
        load_and_update_dns_config(cfg_path, False)
    elif command == 'dryrun':
        load_and_update_dns_config(cfg_path, True)
    elif command == 'status':
        show_online_config(cfg_path)
    else:
        print("unknown command", command)


if __name__ == '__main__':
    main()
