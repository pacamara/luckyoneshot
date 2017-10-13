#
# Copyright (C) 2017 Cryobrew Software
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import uuid
import shutil
from pyramid.response import Response

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
import subprocess
import urllib
import json
from webob import Response
import sys
import timeit
import socket # So we can test the hostname

# Check the Google captcha
def checkCaptcha(request):
    recaptchaResponse = request.POST.get('g-recaptcha-response')

    if (None==recaptchaResponse):
        json_string = '{ "success" : "false" }' # NB must be double quotes around the prop and value
        return json.loads(json_string)

    print("Got g-recaptcha-response=" + recaptchaResponse)

    url = 'https://www.google.com/recaptcha/api/siteverify'
    values = {
        'secret': os.environ['RECAPTCHA_SECRET'],
        'response': recaptchaResponse
    }

    data = urllib.parse.urlencode(values).encode()
    req =  urllib.request.Request(url, data=data)
    response = urllib.request.urlopen(req)
    result = json.loads(response.read().decode())
    return result

@view_config(route_name='storeImageRoute')
def storeImage(request):
    # Generate random filename (ignore filename in request, it could be an attack)
    filePath = os.path.join(os.environ['IMAGE_DIR'], '%s.jpg' % uuid.uuid4())

    # Use intermediate file first to prevent partial files
    intermediateFilePath = filePath + '~'

    try:
        response = storeImageInner(request, filePath, intermediateFilePath)
    except:
        e = sys.exc_info()[0]
        print("ERROR: Exception in store_image! e=" + str(e))
        response = HTTPResponse("OK")

    # NB. filePath is now removed in views.py, because the C++ layer overwrites it with
    # the feedback image.

    try:
        # Would only need removing if exception occurred during upload (due to size overrun?)
        os.remove(intermediateFilePath)
        print("Removed (unexpected!) intermediateFilePath=" + intermediateFilePath)
    except:
        print("Exception (expected) removing intermediateFilePath=" + intermediateFilePath)

    return response


def storeImageInner(request, filePath, intermediateFilePath):
    session = request.session

    if 'captchaPassed' not in session:
        result = checkCaptcha(request)
        if result['success']:
            print("Captcha passed")
            session['captchaPassed'] = 'yes'
        else:
            print("Captcha failed")
            return HTTPFound(location='/')

    # Write file data from request to intermediate file
    fileData = request.POST['pic'].file
    fileData.seek(0)
    with open(intermediateFilePath, 'wb') as outputFile:
        shutil.copyfileobj(fileData, outputFile)

    # Rename the intermediate file to the final file
    os.rename(intermediateFilePath, filePath)

    startTime = timeit.default_timer()

    # Eg on AWS CPP_EXE="/home/ubuntu/luckyoneshot_cpp"
    CPP_EXE = os.environ['CPP_EXE']
    p = subprocess.Popen(CPP_EXE + " " + filePath, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # The scannedCodes are shopCode+invoiceNo+kmtDate (17 chars)
    scannedCodesStr = ""
    for line in p.stdout.readlines():
        print(line)
        lineStr = line.decode("utf-8") 
        if ('scannedCodes=' in lineStr):
            start = len('scannedCodes=')
            # Already sorted in ascending num order by the C++ layer
            scannedCodesStr = lineStr[start:]
            if (scannedCodesStr=="\n"): scannedCodesStr = ""
            print (scannedCodesStr)
    retval = p.wait()

    print("Time taken calling C++ layer:")
    print(timeit.default_timer() - startTime)

    ## .........................................................................
    ## Pass the scannedCodes and feedbackImageFile location via session values
    session['scannedCodes'] = scannedCodesStr
    print("Set scannedCodes in session=" +scannedCodesStr)
    session['feedbackImageFile'] = filePath
    print("Set feedbackImageFile in session=" +filePath)
    return HTTPFound(location='/')

