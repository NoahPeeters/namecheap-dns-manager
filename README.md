Namecheap DNS Manager
---

A command line tool to help you manage namecheap dns records

## Install

```
pip install https://github.com/fangwentong/namecheap-dns-manager/archive/master.zip
```

## Usage

Write your config file (refer to [namecheap_sample.yml](conf/namecheap_sample.yml)), pass the file path to the command.


```
$ namecheap-dns-manager

Usage:
    namecheap-dns-manager <command> [/path/to/dns/config]

Commands:
    status    show current dns status
    update    load dns config from local, flush local config to namecheap


$ namecheap-dns-manager status namecheap_sample.yml

status now [A] @.example.com -> 93.184.216.34
status now [A] www.example.com -> 93.184.216.34
status now [A] plus.example.com -> nil
```
