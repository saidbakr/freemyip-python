from urllib.request import urlopen
import csv
import re
import time
# Configurations values
base_url = 'https://freemyip.com/update'
tokens_file = 'tokens.csv'
log_file = 'log.csv'
# End of Configurations
data = {}
log_data = {}
ip = ''

def load_tokens(tokens_file):
    with open(tokens_file) as csvDataFile:
        csvReader = csv.reader(csvDataFile)
        for row in csvReader:
            data[row[0]] = row[1].strip()


def create_url(domain,token):
    return base_url + '?token=' + token + '&doamin=' + domain + '&verbose=yes'

def extract_ip(msg):
    pattern = "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"    
    return re.search(pattern,msg).group()

def check_url(url,domain = None):
    global ip
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
    global log_data
    log_data.update(l)


def create_log(log_file):
    try:
        f = open(log_file,'w+')
    except IOError:
        print('The log file could not be written!')   
    
    for domain,i in log_data.items():
        #print(i[1],domain)
        f.write(domain+','+i[0]+','+str(i[1])+'\n')
            
    f.close()


load_tokens(tokens_file)
print('Domain'+'\t\t\t'+'Status'+'\t'+'IP')
for domain,token in data.items():
    print(domain,'\t',check_url(create_url(domain, token),domain),'\t', ip)

create_log(log_file)
