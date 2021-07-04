import requests

print('==================')
print('|  Static info   |')
print('==================')

m_key = '3e122606ab557721d279750a875abc551f69345a'
base_url = 'http://127.0.0.1:8000/API'

# status
url = base_url + "/status"
payload={}
headers = { 'X-API-MKEY': m_key }
response = requests.request("GET", url, headers=headers, data=payload)
print('status:')
print(response.text+'\n')

# List buckets
url = base_url + "/bucket"
payload={}
headers = {
  'X-API-MKEY': m_key
}
response = requests.request("GET", url, headers=headers, data=payload)
print('List buckets:')
print(response.text+'\n')

# User quota
url = base_url + "/file/quota"
payload={}
headers = {
  'X-API-MKEY': m_key
}
response = requests.request("GET", url, headers=headers, data=payload)
print('User quota:')
print(response.text+'\n')

print('==================')