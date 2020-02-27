from urllib.request import urlopen
import csv
import re
# Configurations values
base_url = 'https://freemyip.com/update'
tokens_file = 'tokens.csv'
# End of Configurations
data = {}
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

def check_url(url):
    global ip
    try:
        output = urlopen(url)
    except IOError:
        print("The URL could not be opened!\nCheckout the Internet connectivity to freemyip.com")
        exit()
    msg = output.read().decode('utf-8')
    if "ERROR" in msg:
        ip = ''
        return False
    else:       
        ip = extract_ip(msg)        
        return True

load_tokens(tokens_file)
print('Domain'+'\t\t\t'+'Status'+'\t'+'IP')
for domain,token in data.items():
    print(domain,'\t',check_url(create_url(domain, token)),'\t', ip)
