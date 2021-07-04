import requests

print('==================')
print('|    test 1      |')
print('==================')

m_key = '3e122606ab557721d279750a875abc551f69345a'
base_url = 'http://127.0.0.1:8000/API'

# create bucket
url = base_url+"/bucket/create/mainbucket"
payload={}
files={}
headers = {
  'X-API-MKEY': m_key
}
response = requests.request("POST", url, headers=headers, data=payload, files=files)
print('bucket create:')
print(response.text)

# create token
def create_token():
    url_ = base_url+"/token/create/mainbucket"
    payload_={}
    headers_ = {
      'X-API-MKEY': m_key
    }

    response_ = requests.request("POST", url_, headers=headers_, data=payload_)
    return response_

token_response = create_token()
app_token = token_response.json().get('data').get('token')
print('token create:')
print(token_response.text)

# token remove

url = base_url+"/token/remove/"+app_token
payload={}
headers = {
  'X-API-MKEY': m_key
}
response = requests.request("POST", url, headers=headers, data=payload)
print('token delete:')
print(response.text)

token_response = create_token()
app_token = token_response.json().get('data').get('token')

# token remove by bucket
url = base_url+"/token/remove/b/mainbucket"

payload={}
headers = {
  'X-API-MKEY': m_key
}

response = requests.request("POST", url, headers=headers, data=payload)
print('token delete by bucket:')
print(response.text)

token_response = create_token()
app_token = token_response.json().get('data').get('token')

# Add file - using app_token
url = base_url+"/file/add/mainbucket/test_dir"
payload={}
files=[
  ('files',('test.txt',open('test.txt','rb'),'text/plain'))
]
headers = {
  'X-API-AKEY': app_token
}

response = requests.request("POST", url, headers=headers, data=payload, files=files)
print('Add file:')
print(response.text)

# delete file
url = base_url+"/file/remove/mainbucket/test_dir/test.txt"
payload={}
headers = {
  'X-API-MKEY': m_key
}
response = requests.request("POST", url, headers=headers, data=payload)
print('Remove file:')
print(response.text)

# create folder
url = base_url+"/file/mkdir/mainbucket/second_test_dir"
payload={}
headers = {
  'X-API-MKEY': m_key
}
response = requests.request("POST", url, headers=headers, data=payload)
print('Create directory:')
print(response.text)


# delete bucket
url = base_url+"/bucket/remove/mainbucket"
payload={}
files={}
headers = {
  'X-API-MKEY': m_key
}
response = requests.request("POST", url, headers=headers, data=payload, files=files)
print('bucket delete:')
print(response.text)


