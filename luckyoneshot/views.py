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

from pyramid.view import view_config
import sys # For flushing stdout
from luckyoneshot.scannedcode import ScannedCode
import socket
import base64
from datetime import datetime
import os # For removing feedback image file

try:
    IS_DEV_BOX = (os.environ['IS_DEV_BOX'].lower()=="true")
except:
    IS_DEV_BOX = False
print("Python: IS_DEV_BOX=" + str(IS_DEV_BOX))

# TODO -- use varargs to avoid unnecessary concatenation in prod
def trace(str):
    if IS_DEV_BOX: print(str)

def checkForWin(scannedCodeList, bigWins10, bigWins2, partialWins, consolationWins):
    for sc in scannedCodeList:
        trace("Checking: " + str(sc))

        # May-June comp        
        MAY_FIRST = 1060501
        JULY_FIRST = 1060701
        checkForBigWin10(bigWins10, sc, "99768846", MAY_FIRST, JULY_FIRST)
        checkForBigWin2(bigWins2, sc, "83660478", MAY_FIRST, JULY_FIRST)
        checkForPartial(partialWins, sc, "70628612", MAY_FIRST, JULY_FIRST)
        checkForPartial(partialWins, sc, "87596250", MAY_FIRST, JULY_FIRST)
        checkForPartial(partialWins, sc, "97294175", MAY_FIRST, JULY_FIRST)
        trace("PARTIAL WINS may/june =" + str(partialWins))
        checkForConsolation(consolationWins, sc, "904", MAY_FIRST, JULY_FIRST)
        trace("CONSOLATION WINS may/june=" + str(consolationWins))

        # July-Aug comp
        SEPT_FIRST = 1060901        
        checkForBigWin10(bigWins10, sc, "33612092", JULY_FIRST, SEPT_FIRST)
        checkForBigWin2(bigWins2, sc, "06840705", JULY_FIRST, SEPT_FIRST)
        checkForPartial(partialWins, sc, "12182003", JULY_FIRST, SEPT_FIRST)
        checkForPartial(partialWins, sc, "48794532", JULY_FIRST, SEPT_FIRST)
        checkForPartial(partialWins, sc, "77127885", JULY_FIRST, SEPT_FIRST)
        trace("PARTIAL WINS july/aug =" + str(partialWins))
        checkForConsolation(consolationWins, sc, "136", JULY_FIRST, SEPT_FIRST)
        checkForConsolation(consolationWins, sc, "873", JULY_FIRST, SEPT_FIRST)
        checkForConsolation(consolationWins, sc, "474", JULY_FIRST, SEPT_FIRST)
        trace("CONSOLATION WINS july/aug=" + str(consolationWins))


def checkForBigWin10(bigWins10, sc, targetNumber, minDateIncl, maxDateExcl):
    trace("checkForBigWin10: " + str(sc) + " vs " + str(targetNumber))
    if (sc.invoiceNumber==targetNumber and sc.date>=minDateIncl and sc.date<maxDateExcl):
        # Print dont trace wins, want to see them on prod too
        print("BIG WIN $10mil on " + str(sc))
        bigWins10.append(sc)

def checkForBigWin2(bigWins2, sc, targetNumber, minDateIncl, maxDateExcl):
    trace("checkForBigWin2: " + sc.invoiceNumber + " vs " + str(targetNumber))
    trace("    and " + str(sc.date) + " vs " + str(minDateIncl) + ":" + str(maxDateExcl))
    if (sc.invoiceNumber==targetNumber and sc.date>=minDateIncl and sc.date<maxDateExcl):
        print("BIG WIN $2mil on " + str(sc))
        bigWins2.append(sc)

def checkForPartial(partialWins, sc, targetNumber, minDateIncl, maxDateExcl):
    trace("")
    trace("checkForPartial: " + sc.invoiceNumber + " vs " + targetNumber)
    if sc.date>=minDateIncl and sc.date<maxDateExcl:
        for digits in range(8, 2, -1):
            startIndex = 8-digits
            lnPartial = sc.invoiceNumber[startIndex:]
            targetPartial = targetNumber[startIndex:]
            trace("Checking last " + str(digits) + ": " + lnPartial + " vs " + targetPartial)
            
            if (lnPartial==targetPartial):
                print("PARTIAL WIN -- appending " + sc.invoiceNumber + " to entry " + str(digits))
                partialWins[digits].append(sc.invoiceNumber)
                return

def checkForConsolation(consolationWins, sc, targetNumber, minDateIncl, maxDateExcl):
    last3 = sc.invoiceNumber[5:]
    trace("Checking last3=" + last3 + " for consolation win")
    if last3==targetNumber and sc.date>=minDateIncl and sc.date<maxDateExcl:
        print("CONSOLATION WIN with " + sc.invoiceNumber)
        consolationWins.append(sc.invoiceNumber)

def formatPartialWins(partialWinsN, context):
    # If the list is empty for this number of digits, nothing to display
    if len(partialWinsN)==0: return ""

    pwHTML = ""
    for partialWin in partialWinsN:
        pwHTML += partialWin + context
    return pwHTML

@view_config(route_name='home', renderer='templates/los_template.jinja2')
def homepageView(request):
    # For now, print all requests
    print("========================================")
    print(str(datetime.now()) + " Request=" + str(request))
    print()
    print("Request type=" + str(type(request)))
    print("Session=" + str(request.session))
    print("Remote addr=" + str(request.remote_addr))
    print( str(datetime.now()) + " User-Agent=" + str(request.headers.get('User-Agent')) )
    print("========================================")

    session = request.session
    if 'captchaPassed' not in session:
        # Display captcha and check it before submitting
        captchaMarkup = "<div id='recaptcha' class='g-recaptcha' data-sitekey='6LfGECMUAAAAALuZE1w7ZicCIT3lMjgaGlohaJaD' data-callback='submitForm' data-size='invisible'></div> "
        submitButtonOnChange = 'validateForm'
    else:
        # Don't display captcha and submit directly.
        captchaMarkup = ""
        submitButtonOnChange = 'submitForm'

    if 'scannedCodes' in session:
        scannedCodes = session['scannedCodes']
    else:
        scannedCodes = None

    # Debugging param to check win detection logic
    if 'fakeCodes88' in request.GET:
        scannedCodes = request.GET['fakeCodes88']
   
    if None==scannedCodes:
        sys.stdout.flush() # Else logs are empty under nohup

        return {'project': 'luckyoneshot', 
                'captchaMarkup':captchaMarkup,
                'submitButtonOnChange':submitButtonOnChange }
    else:
        return onScannedCodesParamExists(session, scannedCodes, captchaMarkup, submitButtonOnChange)

def onScannedCodesParamExists(session, scannedCodes, captchaMarkup, submitButtonOnChange):
    print("Retrieved from session: scannedCodes=" + scannedCodes)

    # No way to genuinely remove from session, it seems
    session['scannedCodes'] = None

    if 'feedbackImageFile' in session and None!=session['feedbackImageFile']:
        feedbackImageHTML = generateFeedbackImageMarkupAndDelete(session)
    else:
        feedbackImageHTML = ""

    if len(scannedCodes)==0:
        # NB. Dont display the feedbackImage to the user if no scannedCodes, seems pointless
        # (above code still needed to delete the temp file though)
        noReceiptsReadHTML = "抱歉，這個系統無法辨識您的發票。請參考我們的FAQ"
        return {'project': 'luckyoneshot', 
                'noReceiptsReadHTML':noReceiptsReadHTML,
                'captchaMarkup':captchaMarkup,
                'submitButtonOnChange':submitButtonOnChange }
    else:
        return checkScannedCodes(scannedCodes, feedbackImageHTML, captchaMarkup, submitButtonOnChange)

def generateFeedbackImageMarkupAndDelete(session):
    feedbackImageFilename = session['feedbackImageFile']
    session['feedbackImageFile'] = None

    fFeedbackImage = open(feedbackImageFilename,"rb")
    print("Opened feedback image file=" + str(fFeedbackImage))
    fileContent = fFeedbackImage.read()
    print("Read file ok")
    fFeedbackImage.close()
    print("Closed file ok")
    encoded = base64.b64encode(fileContent)
    feedbackImageHTML = "<img src='data:image/jpg;base64," + encoded.decode("ascii") + "' />"
    
    # The C++ code replaces the uploaded file with this,
    # so once this is removed, file cleanup is finished
    try:
        os.remove(feedbackImageFilename)
        print("Successfully removed feedbackImageFile=" + feedbackImageFilename)
    except:
        print("Exception removing file_path=" + feedbackImageFilename)

    return feedbackImageHTML

def checkScannedCodes(scannedCodes, feedbackImageHTML, captchaMarkup, submitButtonOnChange):
    scStrList = scannedCodes.split(",")
    luckyNumbersHTML = "您的<b>" + str(len(scStrList)) + "個</b>發票號碼："
    scannedCodeList = list()
    for sc in scStrList:
        shopCode = sc[:2] 
        invoiceNo = sc[2:10]
        dateDisplay = sc[10:13] + "-" + sc[13:15] + "-" + sc[15:]
        luckyNumbersHTML += "<br>🐱&nbsp&nbsp" + shopCode + "-" + invoiceNo + "&nbsp&nbsp" + dateDisplay
        dateInt = int(sc[10:])
        scObj = ScannedCode(sc[:2], sc[2:10], dateInt)
        scannedCodeList.append(scObj)

    bigWins10 = list()
    bigWins2 = list()
    partialWins = [None] * 9
    for i in range(0,9): partialWins[i] = list()
    consolationWins = list()

    checkForWin(scannedCodeList,bigWins10, bigWins2, partialWins, consolationWins)

    bigWins10HTML = ""
    for bigWin10 in bigWins10:
        bigWins10HTML += bigWin10.invoiceCodeDisplay() + " = 大獎 NT$10,000,000!\n"

    bigWins2HTML = ""
    for bigWin2 in bigWins2:
        bigWins2HTML += bigWin2.invoiceCodeDisplay() + " = 大獎 NT$2,000,000!\n"

    pw8 = formatPartialWins(partialWins[8], " = 八個數字 NT$200,000!")
    pw7 = formatPartialWins(partialWins[7], " = 七個數字 NT$40,000!")
    pw6 = formatPartialWins(partialWins[6], " = 六個數字 NT$10,000!")
    pw5 = formatPartialWins(partialWins[5], " = 五個數字 NT$4,000!")
    pw4 = formatPartialWins(partialWins[4], " = 四個數字 NT$1,000!")
    pw3 = formatPartialWins(partialWins[3], " = 三個數字 NT$200!")

    cwHTML = ""
    for cw in consolationWins:
        cwHTML += cw + " = NT$200, 加油!\n"

    if (bigWins10HTML=="" and bigWins2HTML=="" and pw8=="" and pw7=="" and pw6=="" and pw5=="" and pw4=="" and pw3=="" and cwHTML==""):
        sorry = "抱歉，您的發票沒中獎。。。加油，再上傳一次！"
    else:
        sorry = ""

    sys.stdout.flush() # Else logs are empty under nohup

    return {'project': 'luckyoneshot', 
            'luckyNumbersHTML' : luckyNumbersHTML, 
            'bigWins10HTML':bigWins10HTML,
            'bigWins2HTML':bigWins2HTML,
            'pw8':pw8, 'pw7':pw7, 'pw6':pw6,
            'pw5':pw5, 'pw4':pw4, 'pw3':pw3,
            'consolationWinsHTML':cwHTML,
            'sorryNoWinHTML':sorry,
            'feedbackImageHTML':feedbackImageHTML,
            'captchaMarkup':captchaMarkup,
            'submitButtonOnChange':submitButtonOnChange }

