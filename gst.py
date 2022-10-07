import requests
import json
import time
import os
import pandas as pd
import zipfile
import numpy as np
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36" }

def getcaptcha() : 
    session = requests.Session()
    captcha = session.get('https://services.gst.gov.in/services/captcha?rnd=0.7395713643528166',headers = head())
    cookie = session.cookies.get("CaptchaCookie")
    print(session.cookies["CaptchaCookie"])
    with open("static\\TempCaptcha.png","wb+") as f : 
        f.write(captcha.content )
    return cookie  
def head(add_headers = {}) : 
    add_headers.update(headers)
    return add_headers 

def auth(data,cookie,captcha) :
    session = requests.Session()
    session.get('https://services.gst.gov.in/services/',headers = head()) 
    session.cookies.set("CaptchaCookie",cookie)
    data =  { "captcha": captcha , "deviceID": None ,"mFP": "{\"VERSION\":\"2.1\",\"MFP\":{\"Browser\":{\"UserAgent\":\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36\",\"Vendor\":\"Google Inc.\",\"VendorSubID\":\"\",\"BuildID\":\"20030107\",\"CookieEnabled\":true},\"IEPlugins\":{},\"NetscapePlugins\":{\"PDF Viewer\":\"\",\"Chrome PDF Viewer\":\"\",\"Chromium PDF Viewer\":\"\",\"Microsoft Edge PDF Viewer\":\"\",\"WebKit built-in PDF\":\"\"},\"Screen\":{\"FullHeight\":864,\"AvlHeight\":816,\"FullWidth\":1536,\"AvlWidth\":1536,\"ColorDepth\":24,\"PixelDepth\":24},\"System\":{\"Platform\":\"Win32\",\"systemLanguage\":\"en-US\",\"Timezone\":-330}},\"ExternalIP\":\"\",\"MESC\":{\"mesc\":\"mi=2;cd=150;id=30;mesc=739342;mesc=770243\"}}" ,
            "password": data["gstpwd"] , "type": "username" , "username": data["gstuser"] }
    authenticate = session.post("https://services.gst.gov.in/services/authenticate" ,headers  = head({'Content-type': 'application/json'}),data = json.dumps(data))
    res = json.loads(authenticate.text)
    if "errorCode" in res.keys() : 
        if res["errorCode"] == "SWEB_9000" : 
           raise Exception("Invalid Captcha")
        elif res["errorCode"] == "AUTH_9002" : 
            raise Exception("Invalid Username or Password")
        else : 
            raise Exception("Unkown Exception")
    auth =  session.get("https://services.gst.gov.in/services/auth/",headers  = head({'Referer': 'https://services.gst.gov.in/services/login'}))
    return session 
def creditinvoice(session,fromd,tod) : 
    periods = pd.date_range(fromd.strftime("%Y/%m/%d"),tod.strftime("%Y/%m/%d"), 
              freq='MS').strftime("%m%Y").tolist()
    temp = []
    for period in periods : 
        temp.append(json.loads(session.get(f"https://gstr2b.gst.gov.in/gstr2b/auth/api/gstr2b/getdata?rtnprd={period}",
                    headers = head({"Referer": "https://gstr2b.gst.gov.in/gstr2b/auth/gstr2b/summary"}) ).text))
    return temp