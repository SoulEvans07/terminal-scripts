#!/usr/bin/env python

import lw3
import re
import tcpip
import manparser
import nodeprinters
import argparse
from argparse import RawTextHelpFormatter

## author : "Adam Szi"
## credits : ["Adam Szi", "Milan Tenk"]

### Setting up arguments ###
parser = argparse.ArgumentParser(description='',
    formatter_class=RawTextHelpFormatter)

# required named arguments
requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument('-i','--ip', dest='ip', required=True,
    help='the IP address of the device you want to connect')

# optional named arguments
parser.add_argument('-m','--mode', dest='mode', default='tree',
    help='mode selector [tree, manual] (default: tree)')
parser.add_argument('-p','--port', dest='port', default=6107, type=int,
    help='lw3 port (default: 6107)')
parser.add_argument('-o','--output', dest='output', default='output',
    help='output filename (default: output)')

# parse
args = parser.parse_args()


### Set variables ###
device = lw3.LW3(tcpip.TcpIp(args.ip, args.port))
targetFile = open(args.output + '.txt', 'w')



### Run selected mode ###
if(args.mode == 'tree'):
    nodeprinters.printNodeInfo(device, targetFile, '/', nodeprinters.NodeInfoFunctions.HIERARCHY)
elif (args.mode == 'manual'):
    nodeprinters.printNodeInfo(device, targetFile, '/', nodeprinters.NodeInfoFunctions.MISSING_MANUAL)
else:
    print('\'' + args.mode + '\' is not a recognised mode\n')
    parser.print_help()