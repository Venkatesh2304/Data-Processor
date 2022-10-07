import requests 
from io import BytesIO
from datetime import datetime, time, timedelta
import pandas as pd 
import curlify 
import json
def download_excel(session,data,dpath) :
    response = session.get(data["baseurl"] + "/rsunify/app/reportsController/downloadReport?filePath=" + dpath)
    return BytesIO(response.content)
def login(data) : 
   print("login start")
   session = requests.Session()
   date = lambda : int((datetime.now() - datetime(1970,1,1)).total_seconds() *1000) - (330*60*1000) 
   _data  = {'userId': data["ikeauser"] , 'password': data["ikeapwd"] , 'dbName': data["dbName"] , 'datetime': date() , 'diff': -330 }
   session.post( data["baseurl"] + '/rsunify/app/user/authentication.do',data=_data)
   session.post( data["baseurl"] + "/rsunify/app/user/authenSuccess.htm")
   print("login")
   return session 
def download_claims(session,data,moc) : 
    body =  { "jsonData": '[]' , 
               "jsonObjforheaders": '[{}]',
               "jsonObjfileInfi": '[{"title":"Claims Status Report,SUMMARY,HUL CLAIMS,DEPOT CLAIMS,OTHER ISSUES - 3P GIFTS,PAYMENT DETAILS,SERVICE INVOICES-PAYMENT STATUS,MANUAL ACK","reportfilename":"Claims_Status_Report","viewpage":"claims/PNCC/claimsStatusReport","viewname":"CLAIMS_STATUS_REPORT_PROC","querycount":7}]'
               , "jsonObjWhereClause": '{":val1":"'+ moc+'"}' 
               }
    res = session.post(data["baseurl"] + "/rsunify/app/reportsController/generatereport.do" , 
                 headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"} , data = body )
    return download_excel(session,data,res.text)
def download_sales(session,data,fromd,tod) : 
    body =  { "jsonData": "[]" 
             , "jsonObjforheaders": '[{"1":"Distributor :","2":"","3":"Salesman    :","4":"From Date   :","5":"Beat\t        :","6":"To Date     :","7":"Outlet      :","8":"Group By    :","9":"Division    :","10":"Report Type :","11":"Vehicle     :","12":"Bill Type   :","val1":"DEVAKI ENTERPRISES","val2":"","val3":"List of SalesMan","val4":"01/04/2022","val5":"List of Beats","val6":"30/04/2022","val7":"List of Outlets","val8":"None","val9":"List of Divisions","val10":"Bill Wise","val11":"List of Vehicles","val12":"All"}]'
             ,"jsonObjfileInfi": '[{"title":"BillWise Sales Register,SalesRegister,TaxSummary","reportfilename":"Sales_Register","viewpage":"report/salesRegister","viewname":"PR_SALES_REGISTER_SALES_REPORT","querycount":2}]'
             ,"jsonObjWhereClause": f"""{{":val1":"{fromd.strftime("%d/%m/%Y")}" ,":val2":"{tod.strftime("%d/%m/%Y")}",":val3":"Bill Wise",":val4":"Party Code",":val5":"",":val6":"",":val7":"",":val8":"",":val9":"",":val10":"",":val11":"None",":val12":"All",":val13":"1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44",":val14":19}}"""
             }
    res = session.post(data["baseurl"] + "/rsunify/app/reportsController/generatereport.do" , 
                 headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"} , data = body )
    return download_excel(session,data,res.text)
def download_gstr(session,data,fromd,tod) : 
    params = { "pramFromdate": fromd.strftime("%d/%m/%Y") , 
                "paramToDate":tod.strftime("%d/%m/%Y"),
                "gstrValue": 1  , 
                "paramId": 2}
    res = session.post(data["baseurl"] + "/rsunify/app/gstReturnsReport/gstReturnReportGenerate" , 
                 headers = {"content-type": "text"} , params = params )
    return download_excel(session,data,res.text)
def download_purchase(session,data,fromd,tod) : 
    body =  { "jsonData": '[{"viewname":"Poduct_Wise_Purchase_REPORT"}]' , 
             "jsonObjforheaders": '[{"1":"RS Name     :","2":"Supplier    :","3":"Division    :","4":"From Date   :","5":"Item Variant:","6":"To Date     :","7":"Invoice No","val1":"DEVAKI ENTERPRISES","val2":"List Of Suppliers","val3":"List Of Division","val4":"01/04/2022","val5":"List Of Item Variants","val6":"30/04/2022","val7":"List Of Invoice Number"}]' 
             ,"jsonObjfileInfi": '[{"title":"Product Wise Purchase,Product Wise Purchase,Tax Summary","reportfilename":"Product_Wise_Purchase","viewpage":"report/productwisePurchase","viewname":"Poduct_Wise_Purchase_REPORT","querycount":2}]'
             ,"jsonObjWhereClause": f"""{{":val1":"{fromd.strftime("%d/%m/%Y")}" ,":val2":"{tod.strftime("%d/%m/%Y")}",":val3":"",":val4":"",":val5":"",":val6":"''",":val7":"Units",":val8":"Detailed",":val9":"Excel"}}""" 
              }
    res = session.post(data["baseurl"] + "/rsunify/app/reportsController/generatereport" , 
                 headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"} , data = body )
   
    return download_excel(session,data,res.text)
def download_osreport(session,data,date) : 
    body =  { "jsonData": '[]' , 
             "jsonObjforheaders": '[{"1":"RS Name:","2":" ","3":"Sales Man:","4":"","5":"Beat","6":"Class:","7":"Channel:","8":"Party:","9":"Bill From Date:","10":"Coll From Date:","11":"Bill To Date:","12":"Coll To Date:","13":"Collection code","val1":"DEVAKI ENTERPRISES","val2":"","val3":"List of Salesman","val4":"","val5":"List of Beats","val6":"List of Class","val7":"List of Channel","val8":"List of Party","val9":"01/04/2018","val10":"01/04/2018","val11":"30/04/2021","val12":"30/04/2021","val13":"List of Collection Codes"}]' 
             ,"jsonObjfileInfi": '[{"title":"Outstanding Report-Beat Wise ,Outstanding Report,Outstanding Summary","reportfilename":"Outstanding Report","viewpage":"report/outstanding","viewname":"OUT_STANDING_REPORT","querycount":"2"}]'
             ,"jsonObjWhereClause": f"""{{":val1":"Beat wise",":val2":"Party Level",":val3":"",":val4":"",":val5":"",":val6":"",":val7":"",":val8":"2016-04-01",":val9":"{date.strftime('%Y-%m-%d')}",":val10":"2016-04-01",":val11":"{date.strftime('%Y-%m-%d')}",":val12":"None",":val13":"Equals",":val14":"0.00",":val15":"Both",":val16":"Excel",":val17":""}}""" 
              }
    res = session.post(data["baseurl"] + "/rsunify/app/reportsController/generatereport" , 
                 headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"} , data = body )
    return download_excel(session,data,res.text)
def download_price(session,data) : 
    body =  { "jsonData": '[]' 
              ,"jsonObjforheaders": '[{"1":"Distributor  :","2":"Brand        :","3":"ProfitCenter :","4":"Item Varient :","5":"Division     :","6":"Product Code :","7":"Category     :","8":"Supplier     :","9":"Sub-Category :","10":"Price As On  :","11":"NOTE         :","val1":"DEVAKI ENTERPRISES","val2":"List of Brands","val3":"List of Profit Center","val4":"List of Item Varients","val5":"List of Divisions","val6":"List of Product Code","val7":"List of Categories","val8":"List of Suppliers","val9":"List of Sub Categories","val10":"20/07/2022","val11":"Purchase Price and Landed Cost is calculated for source and customer state as same."}]'
              ,"jsonObjfileInfi": '[{"title":"Price Master,PriceMaster","reportfilename":"Price Master","viewpage":"report/priceMaster","viewname":"PRICE_MASTER","querycount":1}]' 
              ,"jsonObjWhereClause": f"""{{":val1":"''",":val2":"' '",":val3":"' '",":val4":"' '",":val5":"' '",":val6":"' '",":val7":"' '",":val8":"' '",":val9":"Both",":val10":"Active",":val11":"{datetime.now().strftime("%Y/%m/%d")}",":val12":"NO"}}"""
              ,"orderBy": "[Prd.Code]"
            }
    res = session.post(data["baseurl"] + "/rsunify/app/reportsController/generatereport.do" , 
                 headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"} , data = body )
    return download_excel(session,data,res.text)
def download_stock_ledger(session,data,fromd,tod) : 
    body =  { "jsonData": '[]'  
              ,"jsonObjforheaders": '[{"1":"RS Name     :","2":"","3":"Product     :","4":"","5":"From Date   :","6":"","7":"To Date     :","8":"","9":"Trans. Type :","10":"","11":"Location :","val1":"DEVAKI ENTERPRISES","val2":"","val3":"List Of Products","val4":"","val5":"01/04/2022","val6":"","val7":"02/04/2022","val8":"","val9":"List Of Divisions","val10":"","val11":"List of Locations","val12":""}]' 
              ,"jsonObjfileInfi": '[{"title":"Stock Ledger,Stock Ledger","reportfilename":"StockLedger_Report","viewpage":"/stockLedger","viewname":"STOCK_LEDGER_REPORT","querycount":1}]'
              ,"jsonObjWhereClause": f"""{{":val1":"",":val2":"",":val3":"{fromd.strftime("%d/%m/%Y")}",":val4":"{tod.strftime("%d/%m/%Y")}",":val5":"",":loggedInUserId":"1"}}""" 
            }
    res = session.post(data["baseurl"] + "/rsunify/app/reportsController/generatereport.do" , 
                 headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"} , data = body )
    return download_excel(session,data,res.text)
def download_collection(session,data,fromd,tod) : 
    body =   { "jsonData":'[]'  
                ,"jsonObjforheaders": '[{"1":"RS Name:","2":"Coll From Date:","3":"Division:","4":"Coll To Date:","5":"Beat:","6":"Bill From Date:","7":"Party:","8":"Bill To Date:","9":"Sales Man:","10":"Bill Nos:","11":"Vehicle:","12":"Collection Code:","val1":"DEVAKI ENTERPRISES","val2":"01/04/2022","val3":"List of Divisions","val4":"30/04/2022","val5":"List of Beats","val6":"","val7":"List of Outlet","val8":"","val9":"List of SalesMans","val10":"List of Bill Numbers","val11":"List of Vehicles","val12":"List of Collection Codes"}]' 
                ,"jsonObjfileInfi": '[{"title":"Collection Summary - General,Collection Summary","reportfilename":"Collection Summary","viewpage":"report/collectionSummary","viewname":"COLLECTION_SUMMARY_REPORT","querycount":1}]'
                ,"jsonObjWhereClause": f"""{{":val1":"",":val2":"",":val3":"",":val4":"",":val5":"",":val6":"",":val7":"",":val8":"",":val9":"",":val10":"{fromd.strftime("%Y/%m/%d")}",":val11":"{tod.strftime("%Y/%m/%d")}",":val12":"2018/01/01",":val13":"{tod.strftime("%Y/%m/%d")}",":val14":"",":val15":"All",":val16":"Bill Date,Bill Number,Party Name",":val17":"Ascending",":val18":"General",":val19":"Excel",":val20":1}}""" 
              }
    res = session.post(data["baseurl"] + "/rsunify/app/reportsController/generatereport.do" , 
                 headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"} , data = body )
    print(res.text)
    return download_excel(session,data,res.text)
def download_credit_note(session,data,fromd,tod) :
    def downloader(fromd,tod) : 
      body =  { "jsonData":'{"viewName":"RS_INFORMATION"}'  
                ,"jsonObjforheaders": '[{"1":"Distributor   : ","2":" ","3":"Doc Refr   : ","4":" ","5":"Accounts   : ","6":" ","7":"From Date :","8":" ","9":"To Date   :","val1":"DEVAKI ENTERPRISES","val2":"","val3":"List of Refr","val4":"","val5":"List of Account","val6":"","val7":"","val8":"","val9":""}]' 
                ,"jsonObjfileInfi": '[{"title":"Credit / Debit Note Adjustment Report,Credit Debit Note Adjustment Report","reportfilename":"CreditDebitNoteRptAdj ","viewpage":"report/creditDebitNoteRptAdj","viewname":"CREDIT_DEBIT_NOTE_ADJ_RPT_EXCEL"}]'
                ,"jsonObjWhereClause": f"""{{":val1":"Y",":val2":"Y",":val3":"Y",":val4":1,":val5":"",":val6":"",":val7":"",":val8":"",":val9":"{fromd.strftime("%d/%m/%Y")}",":val10":"{tod.strftime("%d/%m/%Y")}",":val11":"",":val12":"",":val13":"",":val14":"Excel"}}""" 
              }
      res = session.post(data["baseurl"] + "/rsunify/app/reportsController/generatereport.do" , 
                   headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"} , data = body )
      return pd.read_excel(download_excel(session,data,res.text),skiprows=9)
    """date = fromd + timedelta(days =90)
    temp = []
    while date < tod  :  
        temp.append(downloader(fromd,date))
        date += timedelta(days = 90)
    date -= timedelta(days=90)
    temp.append(downloader(date,tod))
    return pd.concat(temp) """
    return  downloader(fromd,tod)
def closingstock(session,data,date) :
    body =  { "jsonObjforheaders": '[{"1":"RS Name:","2":"","3":"Profit Center:","4":"Location:","5":"Division:","6":"Status:","7":"Category:","8":"Date:","9":"Sub-Category:","10":"","11":"Brand:","12":"","13":"Item Varient:","14":"","15":"Product:","16":"","17":"Latest Tax percentage is picked based on RS state ","val1":"DEVAKI ENTERPRISES","val2":"","val3":"List of Profit Centre","val4":"MAIN GODOWN","val5":"List of Divisions","val6":"All","val7":"List of Categories","val8":"20/07/2022","val9":"List of Sub Categories","val10":"","val11":"List of Brands","val12":"","val13":"List of Item Varients","val14":"","val15":"List of Products","val16":"","val17":""}]' 
              ,"jsonObjfileInfi": '[{"title":"Current Stock Report,CurrentStock","reportfilename":"CurrentStock","viewpage":"report/currentStockReport","viewname":"CURRENT_STOCK_REPORT_PROC","querycount":1}]'
              ,"jsonObjWhereClause": f"""{{":val1":"",":val2":"",":val3":"",":val4":"",":val5":"",":val6":"",":val7":"",":val8":"1",":val9":"Units",":val10":"Basepack+SKU7",":val11":"",":val12":"Purchase Rate * Qty",":val13":"Yes",":val14":"No",":val15":"All",":val16":"{date.strftime('%Y-%m-%d')}",":val17":"None",":val18":"Code",":reportOption":"EXCEL",":val19":"INDIA",":val20":"ALL",":loggedInUserId":"1"}}""" 
            }
    res = session.post(data["baseurl"] + "/rsunify/app/reportsController/generatereport.do" , 
                 headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"} , data = body )
    return download_excel(session,data,res.text)
    