import requests 
import time
header = """<ENVELOPE><HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER><BODY><IMPORTDATA><REQUESTDESC><REPORTNAME>Vouchers</REPORTNAME></REQUESTDESC><REQUESTDATA>"""
footer = "</REQUESTDATA></IMPORTDATA></BODY></ENVELOPE>"

def upload(body) :
   res = requests.post("http://localhost:9000",data=body)
   return res.text

def upload_many(body) : 
    body = ["<TALLYMESSAGE>" + i for i in 
              "</TALLYMESSAGE>".join(body.split("</TALLYMESSAGE>")[:-1]).split("<TALLYMESSAGE>")[1:]]
    n = 100
    body = [ "".join(i) for i in [body[i:i+n] for i in range(0, len(body), n)]]
    count = 0 
    start = time.time()
    for body in body :
        count += n
        res = upload(header + body + footer)
        if count % 100 == 0 : 
          print(count)
          print(res)
          #print(res)
          print(time.time() - start)
          start = time.time()
#with open("C:\\Users\\Venkatesh\\Downloads\\test.xml") as f :
#   print(upload(f.read()))