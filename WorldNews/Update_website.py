# -*- coding: utf-8 -*-
"""
Created on Tue Jan 26 16:47:46 2021

@author: user
"""

import NewsReader as nr
import gitpush as gp
import os
import time

while True:
    print("cleaning API")
    files = os.listdir("C://Users/user/Documents/w2v/templates/")
    for f in files:
        if f != "form.html":
            file_loc = "C://Users/user/Documents/w2v/templates/"+f
            os.remove(file_loc)

    print("running news")
    nr.run_news()
    print("finished news")
    gp.push()
    time.sleep(3200)
    print("running again")