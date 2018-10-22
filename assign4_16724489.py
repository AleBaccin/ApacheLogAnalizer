#!/usr/bin/env python
"""USAGE

Alessandro Paolo Baccin - 16724489 - baccin.alessandro@gmail.com

-h: Help
-n: number of unique ips
-t k: show top k recurrent ips
-v k: number of visits from a k
-L k: show all requests from k
-d k: show all requests on k day

END"""

#Note: The features works fine except for some invalid ips that get validated because of the regex I have tried to use socket.inet_aton to validate them but they still get validated. I decided to use regex cause it seems the most used way to parse apache log files

import socket
import sys
import re
import getopt
from datetime import datetime, date, timedelta
from collections import Counter
from sets import Set


parts = [
    r'(?P<host>\S+)',                   # host
    r'\S+',                             # indent
    r'(?P<user>\S+)',                   # user
    r'\[(?P<time>.+)\]',                # time
    r'"(?P<request>.*)"',               # request
    r'(?P<status>[0-9]+)',              # status
    r'(?P<size>\S+)',                   # size
    r'"(?P<referrer>.*)"',              # referrer
    r'"(?P<agent>.*)"',                 # user agent
]
REGEX = re.compile(r'\s+'.join(parts)+r'\s*\Z')

REGEX_IP = r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b'
 

def output(line):
    Ress = re.match(REGEX, line)
    if Ress:
        return Ress.groups()


def report_requests(log_file, ip):
    for line in log_file:
        line_dict = output(line)
	requests(line_dict, ip)


def report_visits(log_file, ip):
    my_possible_visits = []
    for line in log_file:
        line_dict = output(line) 
        if requests_per_ip(line_dict, ip) is not None:
            my_possible_visits.append(requests_per_ip(line_dict, ip))
    return(my_possible_visits)


def report_requests_date(log_file, date):
    my_possible_visits = []
    for line in log_file:
        line_dict = output(line)
	if requests_per_date(line_dict, date) is not None:
            my_possible_visits.append(requests_per_date(line_dict, date))
    return(my_possible_visits)


def calculate_visits_date(requests_list_date):
    total_ips = Set(requests_list_date)
    already_checked = dict()
    for ip in total_ips:
	if(ip[0] not in already_checked):
	    print("IP: " + str(ip[0]) + " Count: " + str(calculate_visits(requests_list_date, str(ip[0]))))
            already_checked[ip[0]] = True


def calculate_visits(possible_visits, ip):
    if not possible_visits:
	return 0
    counter = 0
    start = possible_visits[0] 	
    for line in possible_visits:
	if (start[1] not in line[1] and ip in line[0]):
	    start_time = datetime.strptime(start[1][:-6], "%d/%b/%Y:%H:%M:%S")
	    line_time = datetime.strptime(line[1][:-6], "%d/%b/%Y:%H:%M:%S")
	    if abs(line_time - start_time).days > 0:
		counter = counter + 1
	    else:
		if abs(line_time - start_time).seconds > 3600:
		    counter = counter + 1
	    start = line
	elif counter == 0:
	        counter = 1 #If there is a request we initialize counter to 1
    return counter


def unique_ips(log_file):
    c = 0
    with log_file as f:
        log = f.read()
        my_iplist = re.findall(REGEX_IP,log)
    	ipcount = Counter(my_iplist)
	for ip, count in ipcount.items():
	    try:
    		socket.inet_aton(str(ip))
	        c = c + 1
	    except socket.error:
		pass		    
    f.close()
    return(c)


def top_requests(log_file, n):
    with log_file as f:
        log = f.read()
        my_iplist = re.findall(REGEX_IP,log)
        ipcount = Counter(my_iplist)
        for ip, count in ipcount.most_common(n):
            print("IP: " + ip + " Count: " + str(count))
    f.close()


def requests(line, ip):
    if line[0] in ip:
        print("IP: " + line[0] + " Request: " + line[3])


def requests_per_ip(line, ip):
    if line[0] in ip:
        return(line[0], line[2])


def requests_per_date(line, date):
    if (date[:2] in line[2][:2] and date[2:5] in line[2][3:6] and date[6:] in line[2][7:11]):
        return(line[0],line[2])


if __name__ == "__main__":
    if not len(sys.argv) > 1:
        print (__doc__)
        sys.exit(1)
    input_file = sys.argv[1]
    try:
        infile = open(input_file, 'r')
    except IOError:
        print ("You must specify a valid file to parse")
        print (__doc__)
	sys.exit(1)
    try:
        opts, args = getopt.getopt(sys.argv[2:], "hnt:v:L:d:", ["help","number","list","visits","requests","date"])
    except getopt.GetoptError:
        print (__doc__)
        sys.exit(2)
    t = 0
    v = None
    l = None
    d = None
    for opt, arg in opts:
	if opt in ("-h"):
            print (__doc__)
            sys.exit(1)
        if opt in ("-n"):
            total_ips = unique_ips(infile)
            print(total_ips)
            sys.exit(1)
        if opt in ("-t"):
            t = int(arg)
            top_requests(infile, t)
            sys.exit(1)
        if opt in ("-v"):
            v = str(arg)
            print(calculate_visits(report_visits(infile, v), v))
            sys.exit(1)
        if opt in ("-L"):
            l = str(arg)
            report_requests(infile, l)
            sys.exit(1)
        if opt in ("-d"):
            d = str(arg)
            visits_on_date = calculate_visits_date(report_requests_date(infile, d))
	    print(visits_on_date)
            sys.exit(1)
    infile.close()

