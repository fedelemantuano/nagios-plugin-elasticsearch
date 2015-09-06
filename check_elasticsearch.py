#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import sys
import urllib2


VERSION = 0.2


def getAPI(url):
    try:
        data = urllib2.urlopen(url=url)
        return json.load(data)
    except:
        print("CRITICAL - Unable to get API url '{}'".format(url))
        sys.exit(2)


def is_number(x):
    return isinstance(x, (int, long, float, complex))


def check_status(value, message, critical, warning, ok=None):
    if (is_number(value) and is_number(critical) and is_number(warning)):
        if value >= critical:
            print("CRITICAL - {}".format(message))
            sys.exit(2)
        elif value >= warning:
            print("WARNING - {}".format(message))
            sys.exit(1)
        else:
            print("OK - {}".format(message))
            sys.exit(0)
    else:
        if value in critical:
            print("CRITICAL - {}".format(message))
            sys.exit(2)
        elif value in warning:
            print("WARNING - {}".format(message))
            sys.exit(1)
        elif value in ok:
            print("OK - {}".format(message))
            sys.exit(0)
        else:
            print("UNKNOWN - Unexpected value: {}".format(value))
            sys.exit(3)


def parser_command_line():
    parser = argparse.ArgumentParser(
        description='Elasticsearch Nagios checks'
    )
    subparsers = parser.add_subparsers(
        help='All Elasticsearch checks groups',
        dest='subparser_name',
    )

    # Common args
    parser.add_argument(
        '-n',
        '--node-name',
        default='_local',
        help='Node name in the Cluster',
        dest='node_name',
    )

    parser.add_argument(
        '-c',
        '--client-node',
        default='localhost',
        help='Client node name (FQDN) for HTTP communication',
        dest='client_node',
    )

    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version='%(prog)s {}'.format(VERSION)
    )

    # Cluster Checks
    cluster = subparsers.add_parser(
        'cluster',
        help='All Cluster checks',
    )
    cluster.add_argument(
        '--cluster-health',
        action='store_true',
        help='Check the Cluster health (green, yellow, red)',
    )

    # Node Checks
    node = subparsers.add_parser(
        'node',
        help='All Node checks',
    )
    node.add_argument(
        '--heap-used-percent',
        action='store_true',
        help='Check the Heap used percent',
    )

    return parser.parse_args()


def check_cluster_health(result):
    critical = 'red'
    warning = 'yellow'
    ok = 'green'
    message = 'The cluster health status is {}'.format(result)
    check_status(
        result,
        message,
        critical,
        warning,
        ok,
    )


def check_heap_used_percent(result, critical=None, warning=None):
    critical = critical or 90
    warning = warning or 75
    message = 'The Heap used percent is {}'.format(result)
    check_status(
        result,
        message,
        critical,
        warning,
    )


if __name__ == '__main__':
    args = parser_command_line()

    if args.subparser_name == 'cluster':
        API_CLUSTER_HEALTH = 'http://{}:9200/_cluster/health'.format(
            args.client_node
        )

        if args.cluster_health:
            result = getAPI(API_CLUSTER_HEALTH)
            check_cluster_health(result['status'])

    if args.subparser_name == 'node':
        API_NODES_STATS = 'http://{}:9200/_nodes/{}/stats'.format(
            args.client_node,
            args.node_name,
        )

        if args.heap_used_percent:
            result = getAPI(API_NODES_STATS)
            node = result["nodes"].values()[0]
            check_heap_used_percent(
                node['jvm']['mem']['heap_used_percent']
            )
