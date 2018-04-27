#!/usr/bin/python2

import os
import time
import csv
import cfscrape
import ipaddress
import ast
import sys

scraper = cfscrape.create_scraper()

def download(url, filename):
    if os.path.isfile(filename) and time.mktime(time.gmtime()) - os.path.getmtime(filename) < 3600:
        return
    sys.stderr.write('downloading '+filename)
    r = scraper.get(url)
    if r.status_code != 200: raise ValueError(str(r.status_code)+'\t'+r.text)
    file = open(filename, 'wb')
    for chunk in r.iter_content(chunk_size=1024):
        file.write(chunk)

big_networks = []
networks_16 = set()

download('https://reestr.rublacklist.net/api/v2/ips/csv', 'ips.csv')
sys.stderr.write('parsing ips.csv\n')
for line in open('ips.csv'):
    ip = ipaddress.ip_address(unicode(line.rstrip('\n')))
    if not ip.is_global:
        sys.stderr.write('skipping non-global ip '+line)
        continue
    networks_16.add(int(ip) >> 16)

download('https://reestr.rublacklist.net/api/v2/current/csv', 'last.csv')
sys.stderr.write('parsing last.csv\n')
reader = csv.reader(open('last.csv'))
next(reader, None)
for row in reader:
    for ip in ast.literal_eval(row[0]):
        if len(ip) == 0: continue
        net = ipaddress.ip_network(unicode(ip))
        if not net.is_global:
            sys.stderr.write('skipping non-global network '+net+'\n')
            continue
        if net.prefixlen < 16:
            big_networks.append(net)
        nip = int(net.network_address)
        networks_16.add(nip >> 16)

def print_net(net):
    print('push "route '+str(net.network_address)+' '+str(net.netmask)+'"')

for net in sorted(big_networks):
    print_net(net)

for x in sorted(networks_16):
    net = ipaddress.ip_network(unicode(str(x>>8)+'.'+str(x&255)+'.0.0/16'))
    if any(net.overlaps(other) for other in big_networks): continue
    print_net(net)
