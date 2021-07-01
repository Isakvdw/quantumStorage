# Quantum Storage
![](https://img.shields.io/badge/Python-3.9.4-yellow)  ![](https://img.shields.io/badge/Django-3.2.4-yellowgreen)


---
## API endpoints

Endpoint list:
```django
[GET] /status
[GET] /bucket
[POST] /bucket/create/<bucket_name>
[POST] /bucket/remove/<bucket_name>
[POST] /token/create/<bucket_name>
[POST] /token/remove/<token>
[POST] /file/add/<bucket_name>/<location>
[POST] /file/mkdir/<bucket_name>/<location>
[POST] /file/remove/<bucket_name>/<file_location>
[GET] /file/get/<bucket_name>/<file_location>
[GET] /file/download/<file_token>
[GET] /file/quota
```
---
`[GET] /status`

Returns server status info, data contents:
- system_load
- memory_free
- disk_free
- kernel_version
- upgradable_packages []

---
`[GET] /bucket`

Lists all buckets of current user

---
`[POST] /bucket/create/<bucket_name>`

Create a new bucket identified by a unique bucket name.

---
`[POST] /bucket/remove/<bucket_name>`

Delete the bucket identified by its unique name

---
`[POST] /token/create/<bucket_name>`

Create a new token for a specified bucket

---
`[POST] /token/remove/<token>`

Delete a token

---
`[POST] /file/add/<bucket_name>/<location>`

> Format: form-data  
> Parameters: ['files','force']  

files: files to upload  
force: boolean, file overwrite

Add file(s) to a bucket 

---
`[POST] /file/mkdir/<bucket_name>/<location>`

Create a new directory in a bucket.  
Specified by the bucket name as bucket_name and with folder location+name specified as location.

---
`[POST] /file/remove/<bucket_name>/<file_location>`

Delete a file or folder in a bucket.  
Specified by the bucket name as bucket_name and file/folder location+name specified as file_location

---
`[GET] /file/get/<bucket_name>/<file_location>`

Create a download token for a specified file in a bucket.  
If multiple tokens are generated for the same file, they will all be invalidated once one token is used or if the file is changed.

---
`[GET] /file/download/<file_token>`

Download a file with a given download token generated with `/file/get`.  
A token can only be used once.

---
`[GET] /file/quota`

Returns the storage quota that the user has remaining in Bytes.

--- 
## API response

### __Success__
Along with a 200 status code,  
successful requests will result in the following basic JSON structure:
```json
{
    "status": "success",
    "message": <response_msg>,
    "data": { <data_items> }
}
```
The data parameter will only be present for some requests

### __Failure__
An erroneous request will return a response with a 400,401,403,404 or 405 response code depending on the error;  
It will also contain an error code in the response for more details on the issue.  
The following basic JSON structure will be returned:
```json
{
    "status": "error", 
    "message": <error_code>
}
```

|     | error code          | description                                       |
|-----|---------------------|---------------------------------------------------|
| 401 | UNAUTHORIZED        | Invalid API key                                   |
| 403 | UNAUTHORIZED        | Master key required                               |
| 405 | REQ_METHOD_INVALID  | Wrong request method                              |
| 400 | INSUFFICIENT_SPACE  | User storage quota depleted                       |
| 400 | BUCKET_EXISTS       | Bucket with name already exists                   |
| 404 | BUCKET_DNE          | Bucket with given name does not exist             |
| 404 | NOT_A_FILE          | Specified location is not file                    |
| 400 | FILE_ALREADY_EXISTS | File already exists (use force=true to overwrite) |
| 404 | FILE_DNE            | Specified file location does not exist            |
| 404 | TOKEN_DNE           | Token does not exist                              |
| 400 | INVALID_PATH        | Stop trying to break the server                   |
| 400 | INVALID_DIR         | Directory name is invalid                         |
| 400 | INVALID_TOKEN       | invalid download token                            |
| 400 | INVALID_BUCKET      | wrong application token                           |