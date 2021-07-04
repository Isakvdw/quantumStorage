import requests

print('==================')
print('|    test 1      |')
print('==================')

m_key = '3e122606ab557721d279750a875abc551f69345a'
base_url = 'http://127.0.0.1:8000/API'

# create bucket
url = base_url+"/bucket/create/main2bucket"
payload={}
files={}
headers = {
  'X-API-MKEY': m_key
}
response = requests.request("POST", url, headers=headers, data=payload, files=files)
print('bucket create:')
print(response.text)

# User quota
def quota():
    url = base_url + "/file/quota"
    payload={}
    headers = {
      'X-API-MKEY': m_key
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    print('User quota:')
    print(response.text+'\n')

quota()

# Add file
url = base_url+"/file/add/main2bucket/"
payload={}
files=[
  ('files',('test.txt',open('test.txt','rb'),'text/plain'))
]
headers = {
  'X-API-MKEY': m_key
}

response = requests.request("POST", url, headers=headers, data=payload, files=files)
print('Add file:')
print(response.text)

# quota after file add
quota()

# get file token
url = base_url+"/file/get/main2bucket/test.txt"

payload={}
headers = {
  'X-API-MKEY': m_key
}
response = requests.request("GET", url, headers=headers, data=payload)
file_token = response.json().get('data').get('file_token')
print('Get file token:')
print(response.text)

# download file
url = base_url+"/file/download/"+file_token
payload={}
headers = {
  'X-API-MKEY': m_key
}
response = requests.request("GET", url, headers=headers, data=payload)
print('download file:')
print(response.text)

# delete bucket
url = base_url+"/bucket/remove/main2bucket"
payload={}
files={}
headers = {
  'X-API-MKEY': m_key
}
response = requests.request("POST", url, headers=headers, data=payload, files=files)
print('bucket delete:')
print(response.text)

