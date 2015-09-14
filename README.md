# Elasticsearch Nagios Checks

## Overview

This is a simple Nagios check script to monitor all nodes of your Elasticsearch Cluster. 

## Authors

### Main Author
 Fedele Mantuano (**Twitter**: [@fedelemantuano](https://twitter.com/fedelemantuano))


## Installation

In your Nagios plugins directory run

<pre><code>git clone https://github.com/fedelemantuano/nagios-plugin-elasticsearch.git</code></pre>

## Usage

### Install in Nagios (Example Heap Used Percent)

Edit your _commands.cfg_ and add the following

<pre><code>
define command {
    command_name    check_heap_used_percent
    command_line    /opt/nagios-plugin-elasticsearch/check_elasticsearch.py -D -n $ARG1$ -c $ARG2$ node --heap-used-percent
}
</code></pre>

(add `-D` to the command if you want to add perfdata to the output)

(add `-G` to the command if you want only output)

(add `-D -G` to the command if you want only output and graph)

Then you can reference it like the following.

#### Check Heap Used Percent
<pre><code>
define service {
    use                     generic-service
    host_name               node_cluster
    service_description     ELASTICSEARCH - Node Heap used percent
    check_command           check_heap_used_percent!node_name!client_node
}
</code></pre>

![Heap used percent](https://github.com/fedelemantuano/nagios-plugin-elasticsearch/blob/develop/images/heap_used_percent.png)
