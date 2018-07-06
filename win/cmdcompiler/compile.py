#!/usr/bin/env python

import glob
import os
import subprocess
import argparse
from argparse import RawTextHelpFormatter

## author : "Adam Szi"

### Setting up 3 optional arguments ###
parser = argparse.ArgumentParser(description='Compile only the changed files!'+
	'\n\t1. Put the .java files you want to compile in the \'java\' folder.'+
	'\n\t2. Put the .jar file in the main folder.'+
	'\n\t3. Profit!',
	formatter_class=RawTextHelpFormatter)

# optional named arguments
parser.add_argument('-j', dest='jar', default='UPBSW.jar',
	help='the .jar you want to compile into (default: UPBSW.jar)')
parser.add_argument('-s', dest='src', default='java',
	help='.java source folder (default: java)')
parser.add_argument('-f', dest='folder', default='lightware',
	help='base package of the .jar (default: lightware)')

# parse
args = parser.parse_args()


### Setting up 3 optional arguments ###
globregx = "\\*.java"
files = glob.glob(args.src + globregx)


### Remove old backup ###
if(os.path.isdir(args.folder+"_old")):
	print("# Remove '"+args.folder+"_old' backup folder")
	subprocess.run(["rm", "-r", args.folder+"_old"])


### Create backup from prev build ###
if(os.path.isdir(args.folder)):
	print("# Create backup as '"+args.folder+"_old' folder")
	os.rename(args.folder, args.folder+"_old")


### Search for .java files then compile them ###
for java in files:
	with open(java, 'r') as f:
		directory = f.readline()[8:].replace(';\n','')

	# compile .java
	if directory != '':
		subprocess.run(["javac", "-cp", args.jar, java, "-d", "./"])
		print("# Compiled: " + directory+'.'+java[5:].replace('.java', ''))


### Copy compiled .class files to .jar ###
if(os.path.isdir(args.folder)):
	# 7zip output void
	log = open("log.txt", 'w')

	subprocess.run(["7z", "u", args.jar, args.folder], stdout=log)
	print("# "+args.folder+"\\ copied into "+args.jar)

	# 7zip output void clearing
	log.close()
	subprocess.run(["rm", "log.txt"])
else:
	print("# Nothing to do! No "+args.folder+"\\ folder")