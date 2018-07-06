#!/usr/bin/env python

import difflib
import argparse
from argparse import RawTextHelpFormatter

## author : "Adam Szi"

### Setting up arguments ###
parser = argparse.ArgumentParser(description='',
    formatter_class=RawTextHelpFormatter)

# required named arguments
requiredNamed = parser.add_argument_group('required named arguments')
requiredNamed.add_argument('-o','--old', dest='old', required=True,
    help='file name of the txt containing the old lw3 tree')
requiredNamed.add_argument('-n','--new', dest='new', required=True,
    help='file name of the txt containing the new lw3 tree')

# optional named arguments
parser.add_argument('-out','--output', dest='output', default='diffHTML',
    help='output filename (default: diffHTML)')

# parse
args = parser.parse_args()


### Opening the files ###
oldFile = open(args.old, 'r')
newFile = open(args.new, 'r')
htmlFile = open(args.output + '.html', 'w')
diffFile = open(args.output + '.diff', 'w')

### Generate HTML diff ###
diff = difflib.HtmlDiff().make_file(oldFile, newFile)
htmlFile.write(diff)


### Repening the files because of readlines ###
oldFile = open(args.old, 'r')
newFile = open(args.new, 'r')

### Generate .diff file ###
diff = difflib.unified_diff(oldFile.readlines(), newFile.readlines())
diffFile.write(''.join(diff))


### Closing files ###
oldFile.close()
newFile.close()
htmlFile.close()
diffFile.close()