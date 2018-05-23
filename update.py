#!/usr/bin/python2

import ipaddress
import sys

big_networks = []
networks_16 = set()

def parse_file(filename):
    sys.stderr.write('parsing '+filename+'\n');
    for line in open(filename):
        net = ipaddress.ip_network(unicode(line.rstrip()))
        if not net.is_global:
            sys.stderr.write('skipping non-global ip/network '+str(net)+'\n')
            continue
        if net.prefixlen < 16:
            big_networks.append(net)
            continue
        nip = int(net.network_address)
        networks_16.add(nip >> 16)

parse_file('iplist_blockedbyip.txt')
parse_file('iplist.txt')

def print_net(net):
    print('push "route '+str(net.network_address)+' '+str(net.netmask)+'"')

for net in sorted(big_networks):
    print_net(net)

for x in sorted(networks_16):
    net = ipaddress.ip_network(unicode(str(x>>8)+'.'+str(x&255)+'.0.0/16'))
    if any(net.overlaps(other) for other in big_networks): continue
    print_net(net)
