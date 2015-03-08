#! /usr/bin/env python
# encoding: utf-8

"""
Copyright (c) 2014-2015 ourren
author: ourren <i@ourren.com>
"""
import sys
import os
import hashlib
import json
import re
import requests
from thirdlib import threadpool

class WhatWeb(object):
    def __init__(self, url):
        with open("./rules/whatweb.json") as f:
            self.rules = json.load(f)
        self.url = url
        self.thread_num = 10
        self.result = ''

    def identify_cms(self, cms):
        for rule in self.rules[cms]:
            try:
                r = requests.get(self.url + rule["url"], timeout=5)
                r.encoding = r.apparent_encoding
                r.close()
                if "md5" in rule and hashlib.md5(r.content).hexdigest() == rule["md5"]:
                    return cms

                elif "field" in rule and rule["field"] in r.headers and rule["value"] in r.headers[rule["field"]]:
                    return cms

                elif "text" in rule:
                    if type(rule["text"]) is list:
                        for itext in rule["text"]:
                            if itext in r.text:
                                return cms
                    elif rule["text"] in r.text:
                            return cms

                elif "regexp" in rule:
                    if type(rule["regexp"]) is list:
                        for reg in rule["regexp"]:
                            if re.search(reg, r.text):
                                return cms
                    elif re.search(rule["regexp"], r.text):
                            return cms
            except Exception:
                pass

    def log(self, request, result):
        # callback function
        if result:
            self.result = "%s: %s" % (self.url, result)
            raise threadpool.NoResultsPending

    def run(self):
        pool = threadpool.ThreadPool(self.thread_num)
        reqs = threadpool.makeRequests(self.identify_cms, self.rules, self.log)
        for req in reqs:
            pool.putRequest(req)
        pool.wait()


def main():
    print 'WhatWeb testing...'
    URL = 'http://wiki.lizhaoweb.net'
    w = WhatWeb(URL)
    w.run()
    print 'Final:' + w.result

if __name__ == "__main__":
    main()