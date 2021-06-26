from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import SuspiciousFileOperation, PermissionDenied
from storageInterface.models import StorageUser
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.core.files.base import ContentFile
from django.http import JsonResponse
from django.http import HttpResponse
from .models import Bucket, StorageUser, AppTokens
from quantumStorage.settings import STORAGE_ROOT,STORAGE_DELETE
import os
import shutil
import time


# All requests are exempt from csrf since no forms are used - hence its not applicable
@csrf_exempt
def index(request):
    # Authentication and method checks
    if not request.META.get('HTTP_X_API_KEY') or not authenticate(request, token=request.META.get('HTTP_X_API_KEY')):
        return HttpResponse('401 Unauthorized',status=401)
    if request.method != 'POST':
        return HttpResponse('401 Unauthorized',status=405)



    # received_json_data = json.loads(request.body.decode("utf-8"))

    # fs = FileSystemStorage(location='S:/TEST', base_url=None)
    # path = fs.save('file.txt', ContentFile(b'new content'))
    # try:
    #     print(fs.listdir('../'))
    # except SuspiciousFileOperation:
    #     print(1)
    #     return HttpResponse("INVALID OPERATION")
    response = {
        'msg': "Hello, world. You're at the root."
    }
    return JsonResponse(response)
    # print(fs.url(path))
    # return HttpResponse("Hello, world. You're at the root.")



#==========================
# Token management
#==========================
@csrf_exempt
def token_add(request):
    return None
@csrf_exempt
def token_remove(request):
    return None
#==========================

#==========================
# Bucket management
#==========================

@csrf_exempt
def bucket_list(request):
    # GET
    # ++++++++++++++++++++++++++++++++
    # Authentication and method checks
    # ++++++++++++++++++++++++++++++++
    error, isMasterKey, user = validateRequest(request, reqType='GET')
    if error:
        return error
    if not isMasterKey:
        return errorResponse('UNAUTHORIZED', 403)
    # ++++++++++++++++++++++++++++++++

    data = { "Buckets" : list(Bucket.objects.filter(owner=user).values_list('name',flat=True)) }
    return successResponse('Buckets retrieved successfully', data)

@csrf_exempt
def bucket_add(request, bucket_name):
    # ++++++++++++++++++++++++++++++++
    # Authentication and method checks
    # ++++++++++++++++++++++++++++++++
    error, isMasterKey, user = validateRequest(request)
    if error:
        return error
    if not isMasterKey:
        return errorResponse('UNAUTHORIZED', 403)
    # ++++++++++++++++++++++++++++++++

    # Checks to see if request is valid
    if Bucket.objects.filter(owner=user,name=bucket_name).exists():
        return errorResponse('BUCKET_EXISTS')

    # valid request, create the bucket
    newBucket = Bucket.objects.create(owner=user,name=bucket_name)
    # create bucket folder, set least priviledge (u+rw)
    os.mkdir(os.path.join(STORAGE_ROOT, str(newBucket.id)),0o600)

    return successResponse('Bucket add successfull')

@csrf_exempt
def bucket_remove(request, bucket_name):
    # ++++++++++++++++++++++++++++++++
    # Authentication and method checks
    # ++++++++++++++++++++++++++++++++
    error, isMasterKey, user, currBucket = validateRequest(request, bucket_name=bucket_name)
    if error:
        return error
    if not isMasterKey:
        return errorResponse('UNAUTHORIZED', 403)
    # ++++++++++++++++++++++++++++++++
    # currBucket = Bucket.objects.filter(owner=user, name=bucket_name)
    # if not currBucket.exists():
    #     return errorResponse('BUCKET_DNE', 404)
    # currBucket = currBucket.first()


    if STORAGE_DELETE:
        # "safe delete" move to folder for later delete, for recovery or forensics
        # moves to STORAGE_DELETE location and prepends current time to name
        shutil.move(os.path.join(STORAGE_ROOT, str(currBucket.id)), os.path.join(STORAGE_DELETE, str(time.time())+'_'+str(currBucket.id)))
    else:
        # delete bucket and all its content
        shutil.rmtree(os.path.join(STORAGE_ROOT, str(currBucket.id)))

    currBucket.delete()
    return successResponse('Bucket remove successful')

#==========================


#==========================
# File operations
#==========================
@csrf_exempt
def file_quota(request):
    # GET
    # ++++++++++++++++++++++++++++++++
    # Authentication and method checks
    # ++++++++++++++++++++++++++++++++
    error, isMasterKey, user = validateRequest(request, reqType='GET')
    if error:
        return error
    # ++++++++++++++++++++++++++++++++)
    data = {"space_left": user.quota - getsize(user)}
    return successResponse('File quota retrieved successfully', data)

@csrf_exempt
def file_add(request, bucket_name, location=''):
    # ++++++++++++++++++++++++++++++++
    # Authentication and method checks
    # ++++++++++++++++++++++++++++++++
    error, isMasterKey, user, currBucket = validateRequest(request, bucket_name=bucket_name)
    if error:
        return error
    # ++++++++++++++++++++++++++++++++
    # create fss object that has root location of bucket for extra security

    currRoot = os.path.join(STORAGE_ROOT, str(currBucket.id))
    fs = FileSystemStorage(location=currRoot, base_url=None, file_permissions_mode=0o600, directory_permissions_mode=0o600)
    # ++++++++++++++++++++++++++++++++

    files = request.FILES.getlist('files')
    # Iterate through all files and save at correct location
    # Files are not automatically overwriten, force=true can be set in the request to automatically overwrite
    # This method also provides automatic folder creation
    for f in files:
        try:
            fileLoc = os.path.join(location, os.path.basename(f.name))
            # Likely not suitable for very high amounts of traffic, but most accurate and error tolerant
            if getsize(user) + f.size > user.quota:
                return errorResponse('INSUFFICIENT_SPACE', 400)
            if fs.exists(fileLoc):
                if request.POST.get('force') == 'true':
                    fs.delete(fileLoc)
                else:
                    return errorResponse('FILE_ALREADY_EXISTS')

            fs.save(fileLoc, f)
        except SuspiciousFileOperation:
            return errorResponse('INVALID_PATH')

    return successResponse('File add successful')

@csrf_exempt
def file_remove(request, bucket_name, file_location):
    # ++++++++++++++++++++++++++++++++
    # Authentication and method checks
    # ++++++++++++++++++++++++++++++++
    error, isMasterKey, user, currBucket = validateRequest(request, bucket_name=bucket_name)
    if error:
        return error
    # ++++++++++++++++++++++++++++++++
    # create fss object that has root location of bucket for extra security

    currRoot = os.path.join(STORAGE_ROOT, str(currBucket.id))
    fs = FileSystemStorage(location=currRoot, base_url=None, file_permissions_mode=0o600, directory_permissions_mode=0o600)
    # ++++++++++++++++++++++++++++++++

    # if its a directory, then check if its empty
    if os.path.isdir(fs.path(file_location)) and not len(os.listdir(fs.path(file_location))):
        return errorResponse('DIR_NOT_EMPTY', 400)

    # finally delete it, if item DNE it wont throw error
    fs.delete(file_location)

    return successResponse('File delete completed')
@csrf_exempt
def file_mkdir(request, bucket_name, location):
    # ++++++++++++++++++++++++++++++++
    # Authentication and method checks
    # ++++++++++++++++++++++++++++++++
    error, isMasterKey, user, currBucket = validateRequest(request, bucket_name=bucket_name)
    if error:
        return error
    # ++++++++++++++++++++++++++++++++
    # create fss object that has root location of bucket for extra security

    currRoot = os.path.join(STORAGE_ROOT, str(currBucket.id))
    fs = FileSystemStorage(location=currRoot, base_url=None, file_permissions_mode=0o600, directory_permissions_mode=0o600)
    # ++++++++++++++++++++++++++++++++

    # Create the directory by using a temp file, not the most efficient but ensures security by using fss
    temp = os.path.join(location,'.TEMP')
    fs.save(temp, ContentFile(''))
    fs.delete(temp)

    return successResponse('mkdir successful')
@csrf_exempt
def file_get(request):

    return None
#==========================

#==========================
# Server status
#==========================
def serv_status(request):
    # GET
    return None

#==========================
# Functions
#==========================
# response for an invalid request
def errorResponse(errmsg, code=400):
    return JsonResponse({'status': 'error', 'message': errmsg}, status=code)

# response for a valid request
def successResponse(msg, data=None,code=200):
    if data is not None:
        return JsonResponse({'status': 'success', 'message': msg, 'data': data}, status=code)
    else:
        return JsonResponse({'status': 'success', 'message': msg}, status=code)

# checks if request is valid and authorized, returns user if valide, and error response if not
# can perhaps be converted to UserPassesTestMixin or middleware in future
# @returns (error: JsonResponse, isMasterKey: Boolean, user: StorageUser, bucket: Bucket)
def validateRequest(request, reqType='POST', bucket_name=None):
    if request.method != reqType:
        return errorResponse('REQ_METHOD_INVALID', 405),None,None,None

    master = False
    linked_bucket = None
    master_key = request.META.get('HTTP_X_API_MKEY')
    application_key = request.META.get('HTTP_X_API_AKEY')

    if master_key:
        user = authenticate(request, token=master_key)
        master = True
    elif application_key:
        user, linked_bucket = AppTokens.objects.authenticate(app_token=application_key)
    else:
        return errorResponse('UNAUTHORIZED', 401),None,None,None

    if not user:
        return errorResponse('UNAUTHORIZED', 401),None,None,None

    if bucket_name:
        # if application token, check if bucket is correct
        if not master:
            if bucket_name == linked_bucket:
                return None, master, user, linked_bucket
            else:
                return errorResponse('INVALID_BUCKET'),None,None,None

        # if master token, check if bucket is valid
        currBucket = Bucket.objects.filter(owner=user, name=bucket_name)
        if not currBucket.exists():
            return errorResponse('BUCKET_DNE', 404),None,None,None

        return None, master, user, currBucket.first()

    return None, master, user


# Gets size of all folder content to check against user quota
# @parm (user: StorageUser)
# @return (size: int) used size of user in bytes
def getsize(user) -> int:
    buckets = list(Bucket.objects.filter(owner=user).values_list(flat=True))
    size = 0
    for bucket in buckets:
        bucket_path = os.path.join(STORAGE_ROOT, str(bucket))
        for path, dirs, files in os.walk(bucket_path):
            for f in files:
                fp = os.path.join(path, f)
                size += os.path.getsize(fp)
    return size