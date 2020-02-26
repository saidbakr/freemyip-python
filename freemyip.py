from urllib.request import urlopen
import csv
data = {}
base_url = 'https://freemyip.com/update?'
tokens_file = 'tokens.csv'

def load_tokens(tokens_file):
    with open(tokens_file) as csvDataFile:
        csvReader = csv.reader(csvDataFile)
        for row in csvReader:
            data[row[0]] = row[1].strip()


def create_url(domain,token):

    return base_url + 'token=' + token + '&doamin=' + domain


def check_url(url):
    output = urlopen(url)
    msg = output.read().decode('utf-8')

    if "ERROR" in msg:
        return False
    else:
        return True


load_tokens(tokens_file)
print('Domain'+'\t\t\t'+'Status')
for domain,token in data.items():
    print(domain,'\t',check_url(create_url(domain, token)))



