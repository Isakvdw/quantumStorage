from django.shortcuts import render
from storageInterface.views import sys_info


def status(request):
    # run script to get sysinfo and send that to the page. 
    # If page will receive high traffic, then change to using env variables and script running seperately every 5min with cronjob
    return render(request, 'statusInfo/status.html', sys_info())