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

import unittest

from pyramid import testing
from luckyoneshot.scannedcode import ScannedCode

K200 = 200000

# views.py:homepageView() expects remote_addr
class DummyRequest2(testing.DummyRequest):
    remote_addr = "99.99.99.99"

class ViewTests(unittest.TestCase):

    def tcommon_checkForWin(self,shopCode,invoiceNo,date,bw10Wins,bw2Wins,pwWinAt,cwWins):
        from .views import checkForWin
        sc = list()
        sc.append( ScannedCode(shopCode,invoiceNo,date) )
        bw10 = list()
        bw2 = list()
        pw = [None] * 9
        for i in range(0,9): pw[i] = list()
        cw = list()
        checkForWin(sc, bw10, bw2, pw, cw)     
        self.assertEqual(len(bw10), bw10Wins)
        self.assertEqual(len(bw2), bw2Wins)

        if (pwWinAt!=0):
            print("Partial wins at index=" + str(pwWinAt) + "=" + str(pw[pwWinAt]))
            self.assertEqual(len(pw[pwWinAt]), 1)
        else:
            for i in range(0,8):
                self.assertEqual(len(pw[i]), 0)
        self.assertEqual(len(cw), cwWins)

    def tcommon_checkForWin_big10(self,shopCode,invoiceNo,date,winExpected):
        if winExpected:
            bw10ExpectedWins = 1
        else:
            bw10ExpectedWins = 0
        self.tcommon_checkForWin(shopCode,invoiceNo,date,bw10ExpectedWins,0,0,0)

    def tcommon_checkForWin_big2(self,shopCode,invoiceNo,date,winExpected):
        if winExpected:
            bw2ExpectedWins = 1
        else:
            bw2ExpectedWins = 0
        self.tcommon_checkForWin(shopCode,invoiceNo,date,0,bw2ExpectedWins,0,0)

    def tcommon_checkForWin_partial(self,shopCode,invoiceNo,date,indexExpectedAt):
        self.tcommon_checkForWin(shopCode,invoiceNo,date,0,0,indexExpectedAt,0)

    def setUp(self):
        self.config = testing.setUp()

    def tearDown(self):
        testing.tearDown()

    def test_homepageView(self):
        from .views import homepageView
        request = DummyRequest2()
        info = homepageView(request)
        self.assertEqual(info['project'], 'luckyoneshot')

    def tcommon_homepageView_bigWins10HTML(self,scannedCodeStr):
        from .views import homepageView
        request = DummyRequest2()
        session = request.session
        session['scannedCodes'] = scannedCodeStr
        info = homepageView(request)
        self.assertTrue('NT$10,000,000' in info['bigWins10HTML'])
        self.assertEqual(info['bigWins2HTML'],"")

    def test_homepageView_bigWins10HTML(self):
        #self.tcommon_homepageView_bigWins10HTML("JF828851301060210") #jan/feb
        #self.tcommon_homepageView_bigWins10HTML("MA747488741060415") #mar/apr
        self.tcommon_homepageView_bigWins10HTML("AA997688461060510") #may/june
        self.tcommon_homepageView_bigWins10HTML("BB336120921060715") #july/aug

    def tcommon_homepageView_bigWins2HTML(self,scannedCodeStr):
        from .views import homepageView
        request = DummyRequest2()
        session = request.session
        session['scannedCodes'] = scannedCodeStr
        info = homepageView(request)
        self.assertTrue('NT$2,000,000' in info['bigWins2HTML'])
        self.assertEqual(info['bigWins10HTML'],"")

    def test_homepageView_bigWins2HTML(self):
        #self.tcommon_homepageView_bigWins2HTML("JF597298841060210") #jan/feb
        #self.tcommon_homepageView_bigWins2HTML("MA825289181060422") #mar/apr
        self.tcommon_homepageView_bigWins2HTML("AA836604781060510") #may/june
        self.tcommon_homepageView_bigWins2HTML("BB068407051060715") #july/aug

    def tcommon_homepageView_pwN(self, scannedCode, expectedKey, expectedPrize):
        from .views import homepageView
        request = DummyRequest2()
        session = request.session
        session['scannedCodes'] = scannedCode
        info = homepageView(request)
        self.assertTrue(expectedPrize in info[expectedKey])

    def test_homepageView_pw8(self):
        # may/june
        self.tcommon_homepageView_pwN("AA706286121060510", "pw8", "NT$200,000")
        self.tcommon_homepageView_pwN("AA875962501060510", "pw8", "NT$200,000")
        self.tcommon_homepageView_pwN("AA972941751060510", "pw8", "NT$200,000")
        #
        # july/aug
        self.tcommon_homepageView_pwN("BB121820031060730", "pw8", "NT$200,000")
        self.tcommon_homepageView_pwN("BB487945321060730", "pw8", "NT$200,000")
        self.tcommon_homepageView_pwN("BB771278851060730", "pw8", "NT$200,000")

    def test_homepageView_pw7(self):
        # may/june
        self.tcommon_homepageView_pwN("AAa06286121060510", "pw7", "NT$40,000")
        self.tcommon_homepageView_pwN("AAa75962501060510", "pw7", "NT$40,000")
        self.tcommon_homepageView_pwN("AAa72941751060510", "pw7", "NT$40,000")
        #
        # july/aug
        self.tcommon_homepageView_pwN("BBa21820031060730", "pw7", "NT$40,000")
        self.tcommon_homepageView_pwN("BBa87945321060730", "pw7", "NT$40,000")
        self.tcommon_homepageView_pwN("BBa71278851060730", "pw7", "NT$40,000")

    def test_homepageView_pw6(self):
        # may/june
        self.tcommon_homepageView_pwN("AAaa6286121060510", "pw6", "NT$10,000")
        self.tcommon_homepageView_pwN("AAaa5962501060510", "pw6", "NT$10,000")
        self.tcommon_homepageView_pwN("AAaa2941751060510", "pw6", "NT$10,000")
        #
        # july/aug
        self.tcommon_homepageView_pwN("BBaa1820031060730", "pw6", "NT$10,000")
        self.tcommon_homepageView_pwN("BBaa7945321060730", "pw6", "NT$10,000")
        self.tcommon_homepageView_pwN("BBaa1278851060730", "pw6", "NT$10,000")

    def test_homepageView_pw5(self):
        # may/june
        self.tcommon_homepageView_pwN("AAaaa286121060510", "pw5", "NT$4,000")
        self.tcommon_homepageView_pwN("AAaaa962501060510", "pw5", "NT$4,000")
        self.tcommon_homepageView_pwN("AAaaa941751060510", "pw5", "NT$4,000")
        #
        # july/aug
        self.tcommon_homepageView_pwN("BBaaa820031060730", "pw5", "NT$4,000")
        self.tcommon_homepageView_pwN("BBaaa945321060730", "pw5", "NT$4,000")
        self.tcommon_homepageView_pwN("BBaaa278851060730", "pw5", "NT$4,000")

    def test_homepageView_pw4(self):
        # may/june
        self.tcommon_homepageView_pwN("AAaaaa86121060510", "pw4", "NT$1,000")
        self.tcommon_homepageView_pwN("AAaaaa62501060510", "pw4", "NT$1,000")
        self.tcommon_homepageView_pwN("AAaaaa41751060510", "pw4", "NT$1,000")
        #
        # july/aug
        self.tcommon_homepageView_pwN("BBaaaa20031060730", "pw4", "NT$1,000")
        self.tcommon_homepageView_pwN("BBaaaa45321060730", "pw4", "NT$1,000")
        self.tcommon_homepageView_pwN("BBaaaa78851060730", "pw4", "NT$1,000")

    def test_homepageView_pw3(self):
        # may/june
        self.tcommon_homepageView_pwN("AAaaaaa6121060510", "pw3", "NT$200")
        self.tcommon_homepageView_pwN("AAaaaaa2501060510", "pw3", "NT$200")
        self.tcommon_homepageView_pwN("AAaaaaa1751060510", "pw3", "NT$200")
        #
        # july/aug
        self.tcommon_homepageView_pwN("BBaaaaa0031060730", "pw3", "NT$200")
        self.tcommon_homepageView_pwN("BBaaaaa5321060730", "pw3", "NT$200")
        self.tcommon_homepageView_pwN("BBaaaaa8851060730", "pw3", "NT$200")

    def tcommon_homepageView_consolationWinsHTML(self, scannedCode, expectedKey, expectedPrize):
        from .views import homepageView
        request = DummyRequest2()
        session = request.session
        session['scannedCodes'] = scannedCode
        info = homepageView(request)
        self.assertTrue(expectedPrize in info[expectedKey])

    def test_homepageView_consolationWinsHTML(self):
        # may/june
        self.tcommon_homepageView_consolationWinsHTML("AAxxxxx9041060510", "consolationWinsHTML", "NT$200")
        self.tcommon_homepageView_consolationWinsHTML("AAxxxxx8881060510", "consolationWinsHTML", "")
        #
        # july/aug
        self.tcommon_homepageView_consolationWinsHTML("BBxxxxx1361060730", "consolationWinsHTML", "NT$200")
        self.tcommon_homepageView_consolationWinsHTML("BBxxxxx8731060730", "consolationWinsHTML", "NT$200")
        self.tcommon_homepageView_consolationWinsHTML("BBxxxxx4741060730", "consolationWinsHTML", "NT$200")
        self.tcommon_homepageView_consolationWinsHTML("BBxxxxx8881060730", "consolationWinsHTML", "")

    ###########################################################################
    def test_checkForWin_big10(self):
        # may/june
        self.tcommon_checkForWin_big10("AA","99768846",1051231,False)
        self.tcommon_checkForWin_big10("AA","99768846",1060615,True)
        self.tcommon_checkForWin_big10("AA","99768846",1060701,False)

    def test_checkForWin_big2(self):
        # may/june
        self.tcommon_checkForWin_big2("AA","83660478",1051231,False)
        self.tcommon_checkForWin_big2("AA","83660478",1060501,True)
        self.tcommon_checkForWin_big2("AA","83660478",1060801,False)

    def test_checkForWin_partial_mayJune(self):
        self.tcommon_checkForWin_partial("UN","70628612",1051231,0)
        self.tcommon_checkForWin_partial("UN","70628612",1060501,8)
        self.tcommon_checkForWin_partial("UN","x0628612",1060501,7)
        self.tcommon_checkForWin_partial("UN","xx628612",1060501,6)
        self.tcommon_checkForWin_partial("UN","xxx28612",1060501,5)
        self.tcommon_checkForWin_partial("UN","xxxx8612",1060501,4)
        self.tcommon_checkForWin_partial("UN","xxxxx612",1060501,3)
        self.tcommon_checkForWin_partial("UN","xxxxxx12",1060501,0)
        self.tcommon_checkForWin_partial("UN","70628612",1060901,0)
        #
        self.tcommon_checkForWin_partial("UN","87596250",1051231,0)
        self.tcommon_checkForWin_partial("UN","87596250",1060501,8)
        self.tcommon_checkForWin_partial("UN","x7596250",1060501,7)
        self.tcommon_checkForWin_partial("UN","xx596250",1060501,6)
        self.tcommon_checkForWin_partial("UN","xxx96250",1060501,5)
        self.tcommon_checkForWin_partial("UN","xxxx6250",1060501,4)
        self.tcommon_checkForWin_partial("UN","xxxxx250",1060501,3)
        self.tcommon_checkForWin_partial("UN","xxxxxx50",1060501,0)
        self.tcommon_checkForWin_partial("UN","87596250",1060901,0)
        #
        self.tcommon_checkForWin_partial("UN","97294175",1051231,0)
        self.tcommon_checkForWin_partial("UN","97294175",1060501,8)
        self.tcommon_checkForWin_partial("UN","x7294175",1060501,7)
        self.tcommon_checkForWin_partial("UN","xx294175",1060501,6)
        self.tcommon_checkForWin_partial("UN","xxx94175",1060501,5)
        self.tcommon_checkForWin_partial("UN","xxxx4175",1060501,4)
        self.tcommon_checkForWin_partial("UN","xxxxx175",1060501,3)
        self.tcommon_checkForWin_partial("UN","xxxxxx75",1060501,0)
        self.tcommon_checkForWin_partial("UN","97294175",1060901,0)
        #
        self.tcommon_checkForWin_partial("UN","99999999",1060201,0)

    def test_checkForWin_partial_julyAug(self):
        self.tcommon_checkForWin_partial("BB","12182003",1051231,0)
        self.tcommon_checkForWin_partial("BB","12182003",1060701,8)
        self.tcommon_checkForWin_partial("BB","x2182003",1060701,7)
        self.tcommon_checkForWin_partial("BB","xx182003",1060701,6)
        self.tcommon_checkForWin_partial("BB","xxx82003",1060701,5)
        self.tcommon_checkForWin_partial("BB","xxxx2003",1060701,4)
        self.tcommon_checkForWin_partial("BB","xxxxx003",1060701,3)
        self.tcommon_checkForWin_partial("BB","xxxxxx03",1060701,0)
        self.tcommon_checkForWin_partial("BB","12182003",1060901,0)
        #
        self.tcommon_checkForWin_partial("BB","48794532",1051231,0)
        self.tcommon_checkForWin_partial("BB","48794532",1060701,8)
        self.tcommon_checkForWin_partial("BB","x8794532",1060701,7)
        self.tcommon_checkForWin_partial("BB","xx794532",1060701,6)
        self.tcommon_checkForWin_partial("BB","xxx94532",1060701,5)
        self.tcommon_checkForWin_partial("BB","xxxx4532",1060701,4)
        self.tcommon_checkForWin_partial("BB","xxxxx532",1060701,3)
        self.tcommon_checkForWin_partial("BB","xxxxxx32",1060701,0)
        self.tcommon_checkForWin_partial("BB","48794532",1060901,0)
        #
        self.tcommon_checkForWin_partial("BB","77127885",1051231,0)
        self.tcommon_checkForWin_partial("BB","77127885",1060701,8)
        self.tcommon_checkForWin_partial("BB","x7127885",1060701,7)
        self.tcommon_checkForWin_partial("BB","xx127885",1060701,6)
        self.tcommon_checkForWin_partial("BB","xxx27885",1060701,5)
        self.tcommon_checkForWin_partial("BB","xxxx7885",1060701,4)
        self.tcommon_checkForWin_partial("BB","xxxxx885",1060701,3)
        self.tcommon_checkForWin_partial("BB","xxxxxx85",1060701,0)
        self.tcommon_checkForWin_partial("BB","77127885",1060901,0)

class FunctionalTests(unittest.TestCase):
    def setUp(self):
        from luckyoneshot import main
        app = main({})
        from webtest import TestApp
        self.testapp = TestApp(app)

    def test_root(self):
        res = self.testapp.get('/', status=200)
        self.assertTrue(b'Lucky One Shot' in res.body)
