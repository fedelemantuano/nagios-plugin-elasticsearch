#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import json
import sys
import urllib2


VERSION = 0.5


def getAPI(url):
    try:
        data = urllib2.urlopen(url=url)
        return json.load(data)
    except:
        print("CRITICAL - Unable to get API url '{}'".format(url))
        sys.exit(2)


def is_number(x):
    return isinstance(x, (int, long, float, complex))


def check_status(
    value,
    message,
    only_graph=False,
    critical=None,
    warning=None,
    ok=None,
):
    if only_graph:
        print("{}".format(message))
        sys.exit(0)

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
        '-D',
        '--perf-data',
        action='store_true',
        help='Enable Nagios performance data (Valid for all checks groups)',
        dest='perf_data',
    )

    parser.add_argument(
        '-G',
        '--only-graph',
        action='store_true',
        help='Enable Nagios to print only message',
        dest='only_graph',
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
    node.add_argument(
        '--documents-count',
        action='store_true',
        help='Documents on node',
    )
    node.add_argument(
        '--ratio-search-query-time',
        action='store_true',
        help='Ratio search query_time_in_millis/query_total',
    )

    # Indices Checks
    indices = subparsers.add_parser(
        'indices',
        help='All indices checks',
    )
    indices.add_argument(
        '--index',
        default=None,
        help='Index name',
    )
    indices.add_argument(
        '--prefix',
        default=None,
        help='Include only indices beginning with prefix',
    )

    return parser.parse_args()


def check_cluster_health(
    result,
    perf_data=None,
    only_graph=False
):
    critical = 'red'
    warning = 'yellow'
    ok = 'green'
    message = 'The cluster health status is {}'.format(result)
    if perf_data:
        lookup = {
            'green': 2,
            'yellow': 1,
            'red': 0,
        }
        message += " | cluster_status={}".format(lookup[result])
    check_status(
        result,
        message,
        only_graph,
        critical,
        warning,
        ok,
    )


def check_heap_used_percent(
    result,
    perf_data=None,
    only_graph=False,
    critical=None,
    warning=None,
):
    critical = critical or 90
    warning = warning or 75
    message = 'The Heap used percent is {}%'.format(result)
    if perf_data:
        message += " | heap_used_percent={}".format(result)
    check_status(
        result,
        message,
        only_graph,
        critical,
        warning,
    )


def check_documents_count(
    result,
    perf_data=None,
    only_graph=False,
    critical=None,
    warning=None,
):
    critical = critical or 0
    warning = warning or 0
    message = 'The documents count is {}'.format(result)
    if perf_data:
        message += " | documents_count={}".format(result)
    check_status(
        result,
        message,
        only_graph,
        critical,
        warning,
    )


def check_ratio_search_query_time(
    result,
    perf_data=None,
    only_graph=False,
    critical=None,
    warning=None,
):
    critical = critical or 0
    warning = warning or 0
    message = 'The ratio query_time_in_millis/query_total is {}'.format(result)
    if perf_data:
        message += " | ratio_search_query_time={}".format(result)
    check_status(
        result,
        message,
        only_graph,
        critical,
        warning,
    )


def check_last_entry(
    result,
    perf_data=None,
    only_graph=False,
    critical=None,
    warning=None,
):
    critical = critical or 600
    warning = warning or 300
    message = 'Last entry {} seconds ago'.format(result)
    if perf_data:
        message += " | seconds={}".format(result)
    check_status(
        result,
        message,
        only_graph,
        critical,
        warning,
    )


def get_indices(url):
    indices_dict = getAPI(url)
    return sorted(indices_dict.keys())


def get_last_index(indices):
    return indices[-1]


if __name__ == '__main__':
    args = parser_command_line()

    if args.subparser_name == 'cluster':
        API_CLUSTER_HEALTH = 'http://{}:9200/_cluster/health'.format(
            args.client_node
        )

        if args.cluster_health:
            result = getAPI(API_CLUSTER_HEALTH)
            check_cluster_health(
                result['status'],
                args.perf_data,
                args.only_graph,
            )

    if args.subparser_name == 'node':
        API_NODES_STATS = 'http://{}:9200/_nodes/{}/stats'.format(
            args.client_node,
            args.node_name,
        )

        if args.heap_used_percent:
            result = getAPI(API_NODES_STATS)
            node = result["nodes"].values()[0]
            check_heap_used_percent(
                node['jvm']['mem']['heap_used_percent'],
                args.perf_data,
                args.only_graph,
            )

        if args.documents_count:
            result = getAPI(API_NODES_STATS)
            node = result["nodes"].values()[0]
            check_documents_count(
                node['indices']['docs']['count'],
                args.perf_data,
                args.only_graph,
            )

        if args.ratio_search_query_time:
            result = getAPI(API_NODES_STATS)
            node = result["nodes"].values()[0]
            query_time_in_millis = float(
                node['indices']['search']['query_time_in_millis']
            )
            query_total = float(
                node['indices']['search']['query_total']
            )
            ratio = round(
                query_time_in_millis/query_total,
                2
            )
            check_ratio_search_query_time(
                ratio,
                args.perf_data,
                args.only_graph,
            )
