# Simple Python3 script that updates freemyip.com dynamic DNS hosts.
# Author: Said Bakr <said_ fox@yhaoo.com>
# Licence: Free but mention the author
#
from urllib.request import urlopen
from requests import get
from datetime import datetime
import csv
import re
import time
import sys
import os
# Configurations values
base_url = 'https://freemyip.com/update'
tokens_file = 'tokens.csv'
log_file = 'log.csv'
no_update_time = 3600 # The time in seconds between  successive updates with fixed IP
timeout = 100
# End of Configurations
data = {}
log_data = {}
ip = ' '
forceUpdate = False

def load_tokens(tokens_file):
    try:
        with open(tokens_file) as csvDataFile:
            csvReader = csv.reader(csvDataFile)
            for row in csvReader:
                data[row[0]] = row[1].strip()
    except IOError:
        print("Error: Tokens file [{}] is not found.".format(tokens_file))
        exit()

def public_ip():
    #Get Public IP from api.ipify.org
    try:
        my_ip = get('https://api.ipify.org').text
    except IOError:
        my_ip = ' '
    return my_ip

def read_domain_log(domain):
    # Extract the last IP and timestamp of the last update of the domain
    try:
        f = open(log_file,'r')
    except IOError:
        return {'ip':' ','time':0}
    log = f.read()
    pattern = domain+".*"
    try:
        items = re.search(pattern,log).group().split(',')
    except:
        return {'ip':' ','time':0}
    return {'ip':items[1],'time':float(items[2])}

def create_url(domain,token):
    return base_url + '?token=' + token + '&doamin=' + domain + '&verbose=yes'

def extract_ip(msg):
    #Extracting the IP address from the response body of freemyip.com
    pattern = "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"    
    return re.search(pattern,msg).group()

def not_allowed(domain_log,public_ip):
    global no_update_time, forceUpdate
    if forceUpdate:
        return False
    barier = no_update_time + domain_log['time']
    if barier > time.time() and public_ip == domain_log['ip']:
        return True
    else:
        return False

def check_url(url,domain = None, public_ip = ' '):
    #Accessing the updating host URL of freemyip.com
    global ip, timeout
    #Validating last logged IP and timestamp
    domain_log = read_domain_log(domain)
    if not_allowed(domain_log,public_ip):
        ip = domain_log['ip']
        prep_log({domain: [ip,domain_log['time']]})
        return 'NRU*'        
    try:
        output = urlopen(url,None,timeout)
    except IOError:
        #print("Error: The URL could not be opened!\nCheckout the Internet Connectivity to freemyip.com.")
        ip = 'Connection Error'
        return 'Error'
       # exit()
    msg = output.read().decode('utf-8')
    if "ERROR" in msg:
        ip = '__Bad Token__'
        prep_log({domain:[ip,time.time()]})
        return False
    else:       
        ip = extract_ip(msg)   
        prep_log({domain:[ip,time.time()]})     
        return True

def prep_log(l):
    #Prepare the logging data
    global log_data
    log_data.update(l)

def create_log(log_file):
    #Creating/Replacing the log file
    try:
        f = open(log_file,'w+')
    except IOError:
        print('Error: The log file could not be written.')       
    for domain,i in log_data.items():
        #Writing the domain,IP,timestamp in each line of the log file
        f.write(domain+','+i[0]+','+str(i[1])+'\n')            
    f.close()
    print('Log file ['+log_file+'] has been created.')

def print_log(log_file):
    output = '\033[1mThe log file is below:\x1b[0m\n'
    try:
        f = open(log_file,'r')
    except IOError:
        print('Error: The log file [{}] could not be opened.'.format(log_file))
        exit()
    output += "\n\x1b[1;32mDomain\x1b[0m   \t\t\t\t\t \x1b[6;30;42mIP\x1b[0m  \t\t\t  \x1b[6;30;42mDatetime\x1b[0m\n"
    for line in f:
        timestamp = re.search('[+-]?([0-9]*[.])?[0-9]+$',line).group()
        ts = float(timestamp)
        dt = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
        output += line.replace(',',' \t\t').replace(' ','\t').replace(timestamp+'\n',dt+'\n')
    
    f.close()
    output += '===== \n\x1b[6;30;42mShow log is completed!\x1b[0m'
    print(output)
def printHelp():
    return "[Command] [Param]\n\nParameters:\n\n\tlog: Display log.\n\n\tlogpath: Display log file path.\n\n\tt=X: Use custom connection timeout where X must be an integer represents the timeout in milliseconds, ex: t=35.\n\n\tf: Force update i.e. update even the last update time does not exceed the limit and the IP does not has changed.\n\n\th: Display this help message."

#Executing the script
def exec():  
    global timeout, forceUpdate
    param = ''
    try:
        
        if len(sys.argv) > 1:
            param = sys.argv[1]
            if param == 'f':
                forceUpdate = True
            elif param == 'log':
                print_log(log_file)
                exit()
            elif param == 'logpath':
                print('Log file path:\n')
                print(os.getcwd()+os.sep+log_file)
                exit()
            elif 't=' in param:
                t = param[2:]
                try:
                    t = int(t)
                except:
                    print ('Timeout value is not integer')
                    exit()
                timeout = t
            elif param == 'h':
                print(printHelp())
                exit()
            else:
                print('Error: Not supported parameter value.\nUse h parameter to display help.')
                exit()
    except IOError:        
        if param != None:
            print('Params Error')
            exit()

    load_tokens(tokens_file)
    ipublic_ip = public_ip()
    print('Domain'+'\t\t\t\t'+'Updated'+'\t\t'+'IP')
    for domain,token in data.items():
        print(domain,'\t\t',check_url(create_url(domain, token),domain, ipublic_ip),'\t', ip)   
    print('=====\nUpdate has been done as shown above!\nAt connection timeout {} ms'.format(timeout))
    print('*NRU: Not Require Update. i.e. the public IP still the same in the last [{}] seconds.'.format(no_update_time))
    create_log(log_file)
exec()
