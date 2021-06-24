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
from .models import Bucket, StorageUser
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

    fs = FileSystemStorage(location='S:/TEST', base_url=None)
    path = fs.save('file.txt', ContentFile(b'new content'))
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
def bucket_list(request): # GET
    # ++++++++++++++++++++++++++++++++
    # Authentication and method checks
    # ++++++++++++++++++++++++++++++++
    validateR = validateRequest(request, 'GET')
    if not isinstance(validateR, StorageUser):
        return validateR

    user = validateR
    # ++++++++++++++++++++++++++++++++
    data = list(Bucket.objects.filter(owner=user).values_list('name',flat=True))

    return successResponse('Buckets retrieved successfully', data)

@csrf_exempt
def bucket_add(request, bucket_name):
    # ++++++++++++++++++++++++++++++++
    # Authentication and method checks
    # ++++++++++++++++++++++++++++++++
    authResult = validateRequest(request)
    if not isinstance(authResult, StorageUser):
        return authResult

    user = authResult
    # ++++++++++++++++++++++++++++++++

    # Checks to see if request is valid
    if Bucket.objects.filter(owner=user,name=bucket_name).exists():
        return errorResponse('DUPLICATE_NAME')

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
    validateR = validateRequest(request)
    if not isinstance(validateR, StorageUser):
        return validateR

    user = validateR
    # ++++++++++++++++++++++++++++++++
    currBucket = Bucket.objects.filter(owner=user, name=bucket_name)
    if not currBucket.exists():
        return errorResponse('BUCKET_DNE', 404)
    currBucket = currBucket.first()


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
    return None

@csrf_exempt
def file_add(request, bucket_name, location=''):
    # ++++++++++++++++++++++++++++++++
    # Authentication and method checks
    # ++++++++++++++++++++++++++++++++
    validateR = validateRequest(request)
    if not isinstance(validateR, StorageUser):
        return validateR

    user = validateR
    # ++++++++++++++++++++++++++++++++
    currBucket = Bucket.objects.filter(owner=user, name=bucket_name)
    if not currBucket.exists():
        return errorResponse('BUCKET_DNE', 404)
    currBucket = currBucket.first()

    # create fss object that has root location of bucket for extra security
    fs = FileSystemStorage(location=os.path.join(STORAGE_ROOT, str(currBucket.id)), base_url=None)
    # ++++++++++++++++++++++++++++++++


    files = request.FILES.getlist('files')
    # Iterate through all files and save at correct location
    # FileSystemStorage.save() ensures that files are not overwritten
    # This method also provides automatic folder creation
    for f in files:
        try:
            fs.save(os.path.join(location, os.path.basename(f.name)), f)
        except SuspiciousFileOperation:
            return errorResponse('INVALID_PATH')

    return successResponse('File add successful')

@csrf_exempt
def file_remove(request):
    return None
@csrf_exempt
def file_mkdir(request):
    return None
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


# checks if request is valid, returns user if valide, and error response if not
# can be converted to UserPassesTestMixin or middleware in future
def validateRequest(request, reqType='POST'):
    if request.method != reqType:
        return errorResponse('REQ_METHOD_INVALID',405)

    key = request.META.get('HTTP_X_API_KEY')
    if not key:
        return errorResponse('UNAUTHORIZED', 401)

    user = authenticate(request, token=key)
    if not user:
        return errorResponse('UNAUTHORIZED', 401)

    return user

