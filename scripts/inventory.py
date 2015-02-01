#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Dynamic Inventory that can collect inventory abount web,app,dbs servers
#
import os
import re
import sys
import ConfigParser

from novaclient import client as nova_client

try:
    import json
except:
    import simplejson as json


FILENAME = 'inventory.ini'
STACK_SECTION = 'stack'
HOST_SECTION = 'test'
CONFIG_FILES = ['%s/%s' % (os.getcwd(), FILENAME),
                os.path.expanduser(
                    os.environ.get('ANSIBLE_CONFIG', '~/' + FILENAME)),
                "/etc/ansible/" + FILENAME]

config = ConfigParser.SafeConfigParser()


def get_nova_client():
    # create novaclient that is described information in stack_inventory.ini
    # result = nova.client.Client(...)
    version = config.get(STACK_SECTION, 'api_version')
    username = os.environ.get('OS_USERNAME')
    password = os.environ.get('OS_PASSWORD')
    auth_url = os.environ.get('OS_AUTH_URL')
    tenant_name = os.environ.get('OS_TENANT_NAME')

    instance = nova_client.Client(version,
                                  username,
                                  password,
                                  tenant_name,
                                  auth_url,
                                  insecure=True)
    return instance


def name_filter(servers):
    # create list of server instance that is filtered by hostname
    # result = { TARGET: [Server-A, Server-B, ...] }
    result = {}
    node_list = []
    pattern = '^%s' % config.get(HOST_SECTION, 'hostname_prefix')
    for server in servers:
        if re.match(pattern, server.name):
            node_list.append(server)
    if len(node_list) > 0:
        result['test'] = node_list
    return result


def do_list(target_list):
    # get a inventory for all hosts
    return _create_inventory(target_list)


def do_host(target_list, host):
    # get a inventory for particular host
    # it is same information as hostvars in _meta section
    groups = _create_inventory(target_list)
    if host in groups['_meta']['hostvars']:
        return groups['_meta']['hostvars'][host]
    return {}


def usage():
    print('Usage: stack_inventory --list')
    print('       stack_inventory --host <hostname|IPAddress>')
    sys.exit(1)


def _create_inventory(target_list):
    groups = {
        'localhost': {
            'hosts': ['localhost'],
            'vars': {
                'ansible_connection': 'local'
            }
        }
    }
    meta = dict(hostvars=dict())

    # create group entory to inventory data
    for key in target_list.keys():
        groups[key] = dict(hosts=list(), vars=dict())
        for server in target_list[key]:
            info = server.addresses
            groups[key]['hosts'].append(info['work-net'][0]['addr'])

    # create _meta section for each host
    for key in target_list.keys():
        for host in groups[key]['hosts']:
            if key == 'test':
                meta['hostvars'][host] = dict()
    groups['_meta'] = meta
    return groups


def main(host=None):
    nova = get_nova_client()
    target_list = name_filter(nova.servers.list())
    if host is None:
        print(json.dumps(do_list(target_list), sort_keys=True, indent=2))
    else:
        print(json.dumps(do_host(target_list, host), sort_keys=True, indent=2))


if __name__ == '__main__':
    for path in CONFIG_FILES:
        if os.path.exists(path):
            config.read(path)
    if len(sys.argv) == 2 and sys.argv[1] == '--list':
        main()
    elif len(sys.argv) == 3 and sys.argv[1] == '--host':
        main(sys.argv[2])
    else:
        usage()


#
# [EOF]
#
