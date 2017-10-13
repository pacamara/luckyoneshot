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

class ScannedCode(object):
    shopCode = ""
    invoiceNumber = "" # String because leading zeros matter
    date = 0 # Int so we can easily compare dates

    def __init__(self, sc:str,invNo:str,dateParam:int):
        self.shopCode = sc
        self.invoiceNumber = invNo
        self.date = dateParam

    def invoiceCodeDisplay(self):
        return self.shopCode + "-" + self.invoiceNumber

