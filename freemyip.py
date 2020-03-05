# Simple Python3 script that updates freemyip.com dynamic DNS hosts.
# Author: Said Bakr <said_ fox@yhaoo.com>
# Licence: Free but mention the author
#
from urllib.request import urlopen
from requests import get
import csv
import re
import time
import sys
# Configurations values
base_url = 'https://freemyip.com/update'
tokens_file = 'tokens.csv'
log_file = 'log.csv'
no_update_time = 3600 # The time in seconds between  successive updates with fixed IP
# End of Configurations
data = {}
log_data = {}
ip = ''

def load_tokens(tokens_file):
    try:

        with open(tokens_file) as csvDataFile:
            csvReader = csv.reader(csvDataFile)
            for row in csvReader:
                data[row[0]] = row[1].strip()
    except IOError:
        print("Tokens file [{}] is not found!".format(tokens_file))
        exit()

def public_ip():
    #Get Public IP from api.ipify.org
    try:
        my_ip = get('https://api.ipify.org').text
    except IOError:
        my_ip = ''
    return my_ip

def read_domain_log(domain):
    # Extract the last IP and timestamp of the last update of the domain
    try:
        f = open(log_file,'r')
    except IOError:
        return {'ip':'','time':0}
    log = f.read()
    pattern = domain+".*"
    try:
        items = re.search(pattern,log).group().split(',')
    except:
        return {'ip':'','time':0}

    return {'ip':items[1],'time':float(items[2])}



def create_url(domain,token):
    return base_url + '?token=' + token + '&doamin=' + domain + '&verbose=yes'

def extract_ip(msg):
    #Extracting the IP address from the response body of freemyip.com
    pattern = "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"    
    return re.search(pattern,msg).group()

def not_allowed(domain_log,public_ip):
    global no_update_time
    barier = no_update_time + domain_log['time']
    if barier > time.time() and public_ip == domain_log['ip']:
        return True
    else:
        return False

def check_url(url,domain = None, public_ip = ''):
    #Accessing the updating host URL of freemyip.com
    global ip
    #Validating last logged IP and timestamp
    domain_log = read_domain_log(domain)
    if not_allowed(domain_log,public_ip):
        ip = domain_log['ip']
        prep_log({domain: [ip,domain_log['time']]})
        return 'N.R.U*'
        
    try:
        output = urlopen(url)
    except IOError:
        print("The URL could not be opened!\nCheckout the Internet connectivity to freemyip.com")
        exit()
    msg = output.read().decode('utf-8')
    if "ERROR" in msg:
        ip = ''
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
        print('The log file could not be written!')   
    
    for domain,i in log_data.items():
        #Writing the domain,IP,timestamp in each line of the log file
        f.write(domain+','+i[0]+','+str(i[1])+'\n')
            
    f.close()
    print('Log file ['+log_file+'] has been created.')

def print_log(log_file):
    output = 'The log file below:\n'
    try:
        f = open(log_file,'r')
    except IOError:
        print('The log file [{}] could not be opened.'.format(log_file))
        exit()
    
    output += f.read()
    f.close()
    output += '===== \nShow log is finished.'
    return output


#Executing the script
param = None
try:
    param = sys.argv[1]
    if param == 'log':
        print(print_log(log_file))
        exit()
    else:
        print('Not supported parameter value.')
        exit()
    
    
except:
    if param != None:
        exit()




load_tokens(tokens_file)
public_ip = public_ip()
print('Domain'+'\t\t\t'+'Status'+'\t\t'+'IP')
for domain,token in data.items():
    print(domain,'\t',check_url(create_url(domain, token),domain, public_ip),'\t', ip)   
print('=====\nUpdate has been done!')
print('*N.R.U: Not Require Update. i.e. the public IP still the same in the last [{}] seconds.'.format(no_update_time))

create_log(log_file)


