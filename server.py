from flask import * 
import pandas as pd
from sales import *
import tally
import threading
import ikea
import time
user_data =  { 
 "devaki" : {"ikeauser" : "VEN" ,"ikeapwd" :"Ven2006@" , "dbName" : "41A392", "baseurl" : "https://leveredge102.hulcd.com" , "gstuser" : "DEVAKI9999" , 
             "gstpwd" : "Mosl2004@" },
 "skt" : {"ikeauser" : "SA" ,"ikeapwd" :"Sasi@1234" , "dbName" : "41A320", "baseurl" : "https://leveredge55.hulcd.com" , "gstuser" : "karthik.001" , 
             "gstpwd" : "Krish#2022" }
}
app = Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0 
@app.route("/")
def homepage() : 
    return render_template("index.html")



@app.route("/generate",methods=["post"])
def generate() : 
    invs = {}
    data = request.form 
    fromd = datetime.strptime(data['fromd'],"%Y-%m-%d")
    tod = datetime.strptime(data['tod'],"%Y-%m-%d")
    cred_data = user_data[request.cookies["user"]]
    ledger = request.files["ledger"]
    ledger = pd.read_excel(ledger)
    session =  ikea.login(cred_data)
    temp = []
    #sales(invs,session,cred_data,fromd,tod)
    temp = [stockdebitnote]
    #temp = [purchase,stockdebitnote,marketreturn] #collection
    #temp =  [marketreturn]
    closing_rate_xml = ""
    closing_rate_xml = standard_rate(session,cred_data,tod) 
    #for process in temp : 
    #    process(invs,session,cred_data,fromd,tod)
    processes = [ threading.Thread( target = process ,args = (invs,session,cred_data,fromd,tod,)) for process in temp ]
    [ process.start() for process in processes ]
    [ process.join() for process in processes ]
    claim(invs,session,cred_data,ledger,fromd,tod)
    closing_rate_xml = party_os(session,cred_data,fromd - timedelta(days=1))
    prepare(invs , closing_rate_xml)  
    return send_file("test.xml",as_attachment=True)

@app.route("/openingstock",methods = ["post"])
def getopeningstock() : 
    data = request.form   
    date = datetime.strptime(data['date'],"%Y-%m-%d")
    cred_data = user_data[request.cookies["user"]]
    print(cred_data)
    session = login(cred_data)
    openingstock(session,cred_data,date)
    return send_file("test.xml",as_attachment=True)

@app.route("/getci")
def getci() : 
    cookie  = gst.getcaptcha() 
    return render_template("getci.html",cookie=cookie)

@app.route("/ci",methods=["post"])
def ci() : 
    cred_data = user_data[request.cookies["user"]]
    data = dict(request.form)
    cookie , captcha = list(data.keys())[0] , list(data.values())[0]
    fromd = datetime.strptime(data['fromd'],"%Y-%m-%d")
    tod = datetime.strptime(data['tod'],"%Y-%m-%d")
    session = gst.auth(cred_data,cookie,captcha)
    invs = {}
    creditinvoice(invs,session,fromd,tod)
    prepare(invs)
    return send_file("test.xml",as_attachment=True)

app.run(port=1001,threaded=True)