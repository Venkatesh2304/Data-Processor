import pandas as pd
from collections import defaultdict
import json
from datetime import datetime 
from dateutil.relativedelta import relativedelta
from ikea import *
import gst
import time
header = """<ENVELOPE><HEADER><TALLYREQUEST>Import Data</TALLYREQUEST></HEADER><BODY><IMPORTDATA><REQUESTDESC><REPORTNAME>Vouchers</REPORTNAME></REQUESTDESC><REQUESTDATA>"""
footer = "</REQUESTDATA></IMPORTDATA></BODY></ENVELOPE>"
  
#cred_data = {"ikeauser" : "VEN" ,"ikeapwd" :"Ven2006@" , "dbName" : "41A392", "baseurl" : "https://leveredge102.hulcd.com"}
#session = login(cred_data)
#fromd = datetime(2022,4,29) 
#tod = datetime(2022,4,30) 
def stock_xml(self,row) : 
    #print(self.stocks,"stocks")
    #print(row,"row")
    return f"""<ALLINVENTORYENTRIES.LIST>
		        <STOCKITEMNAME>{row['stock']}</STOCKITEMNAME>
		        <AMOUNT>{row['amount']}</AMOUNT>
		        <ACTUALQTY>{row['qty']}</ACTUALQTY>
                <BATCHALLOCATIONS.LIST>
                <GODOWNNAME>Main Location</GODOWNNAME>
                </BATCHALLOCATIONS.LIST>
		        <BILLEDQTY>{row['qty']}</BILLEDQTY>
		        <ACCOUNTINGALLOCATIONS.LIST>
		        	<LEDGERNAME>{self.stock_ledger}</LEDGERNAME>
		        	<GSTOVRDNNATURE>{self.taxable_status}</GSTOVRDNNATURE>
		        	<GSTOVRDNTAXABILITY>Taxable</GSTOVRDNTAXABILITY>
		        	<AMOUNT>{row['amount']}</AMOUNT>
		        </ACCOUNTINGALLOCATIONS.LIST> 
	            </ALLINVENTORYENTRIES.LIST>
                """
def ledger_xml(self,ledger,amount,isdeemed) : 
    if amount == 0 : 
        return ""
    try : 
     return (f"""<ALLLEDGERENTRIES.LIST>{isdeemed 
                                    }
		                            <LEDGERNAME>{ledger}</LEDGERNAME>
		                            <AMOUNT>{round(amount,3)}</AMOUNT>
	                          </ALLLEDGERENTRIES.LIST>""").replace("ALLLEDGERENTRIES", 
                                  "ALLLEDGERENTRIES" if self.is_all_ledger else "LEDGERENTRIES" )
    except Exception as e :
       print(e,self.is_all_ledger)

def create_ledger(ledger,group) : 
    return f"""<TALLYMESSAGE><LEDGER NAME="{ledger}">
     <NAME.LIST>
     <NAME>{ledger}</NAME>
     </NAME.LIST>
     <PARENT>{group}</PARENT>
    </LEDGER></TALLYMESSAGE>"""
def create_stock(stock) :
    return f"""<TALLYMESSAGE><STOCKITEM Name ="{stock}" Action = "Create">
    <PARENT>HUL</PARENT>
    <BASEUNITS>nos</BASEUNITS>
    <LANGUAGENAME.LIST><NAME.LIST Type = "String"><NAME>{stock}</NAME></NAME.LIST><LANGUAGEID>1033</LANGUAGEID></LANGUAGENAME.LIST>
    </STOCKITEM></TALLYMESSAGE>
    """
def create_master(type,name,parent) : 
    return f"""<TALLYMESSAGE><{type.upper()} NAME="{name}">
     <NAME.LIST>
     <NAME>{name}</NAME>
     </NAME.LIST>
     <PARENT>{parent}</PARENT>
    </{type.upper()}></TALLYMESSAGE>"""
def create_initial_ledgers() : 
    sheets = ["group","ledger"]
    xml = ""
    for sheet in sheets : 
        df = pd.read_excel("D:\\master.xlsx",sheet_name = sheet) 
        for idx,row in df.iterrows() : 
             xml += create_master(sheet,row["NAME"],row["PARENT"])
    xml = xml.replace("&","&amp;")
    return xml 
#print(create_initial_ledgers())

class Voucher : 
    def __init__(self) :
        self.isdeemed = False 
        self.is_all_ledger = False 
        self.godwon = "Main Location"
        self.taxable_status = "Sales Taxable"
        self.xml = ""  
        self.headers = ""
        self.xml_ledgers = ""
        self.xml_stocks  = "" 
        self.isinvoice = "Yes" 
        self.billalloc = False 
        self.ref_type = "Agst Ref"
        self.ledgers = defaultdict(lambda : 0 )
        #self.stocks = pd.DataFrame()
        self.stocks = []
        self.stock_ledger = "Sales A/c"
    def add_ledgers(self,ledgers) : 
        for ledger , amt in ledgers.items() : 
            self.ledgers[ledger] += amt
    def add_stocks(self,stocks) : 
        self.stocks += stocks[["stock","amount","qty"]].to_dict(orient="records")
        #self.stocks = pd.concat([self.stocks,stocks])
    def add_headers(self,data) : 
           self.headers = f"""<TALLYMESSAGE><VOUCHER REMOTEID="{self.vchtype}-{data['date']}-{data['vchno']}"  ACTION ="Create">
				 <DATE>{data['date']}</DATE>
				 <VOUCHERTYPENAME>{self.vchtype}</VOUCHERTYPENAME>
				 <VOUCHERNUMBER>{data['vchno']}</VOUCHERNUMBER>
			 <ISINVOICE>{self.isinvoice}</ISINVOICE>"""
    def prepare_ledgers(self) : 
        isdeemed = lambda amt : ("\n<ISDEEMEDPOSITIVE>" + ('Yes' if amount < 0 else 'No') + "</ISDEEMEDPOSITIVE>") if self.isdeemed else ""
        for ledger , amount in self.ledgers.items() :      
          temp = ledger_xml(self,ledger,amount,isdeemed(amount))
          if self.billalloc  and self.buyer == ledger  : 
             xml = f"""<BILLALLOCATIONS.LIST>
                       <NAME>{self.bill_ref}</NAME>
                       <BILLTYPE>{self.ref_type}</BILLTYPE>
                       <AMOUNT>{amount}</AMOUNT>
                       </BILLALLOCATIONS.LIST>""" 
             temp = temp.replace("</AMOUNT>","</AMOUNT>" + xml )  
          self.xml_ledgers += temp
        self.ledger_raw = defaultdict(lambda : 0 )
    def prepare_stocks(self) : 
       #for idx,row in self.stocks.iterrows() :
        for row in self.stocks :  
         self.xml_stocks += stock_xml(self,row)
    def prepare_xml(self) : 
        self.prepare_ledgers()
        self.prepare_stocks()
        return   self.headers   +  self.xml_ledgers + self.xml_stocks +  "</VOUCHER></TALLYMESSAGE>"
class Sales(Voucher) : 
    def __init__(self,data = None) : 
        super().__init__()
        self.vchtype = "Sales"
        self.cgst , self.sgst= "Sales CGST" , "Sales SGST"
        self.igst = "Sales IGST"
        self.ref_type = "New Ref"
        self.billalloc = True 
        if type(data) != type(None) : 
          self.add_data(data)
    def add_data(self,data) : 
        headers = { "date" : data.iloc[0]["Invoice Date"] , "vchno" :data.iloc[0]["Invoice No"]  }
        self.bill_ref = headers["vchno"]
        Voucher.add_headers(self,headers)
        self.buyer = data["buyer"].iloc[0] 
        sums = data.sum()
        data["qty"] = -data["qty"]
        igst = sums["igst"] if "igst" in sums else 0 
        ledgers = { data["buyer"].iloc[0] :  -(sums["amount"] + sums['cgst'] +  sums["sgst"] + igst ) 
                   , self.cgst :  sums['cgst'] , self.sgst : sums["sgst"] , self.igst : igst }
        Voucher.add_ledgers(self,ledgers)
        Voucher.add_stocks(self,data)
        return self 
class SalesReturn(Sales) : 
    def __init__(self,data) : 
        super().__init__()
        self.vchtype = "Credit Note"
        self.stock_ledger = "Sales Return"
        self.cgst , self.sgst= "Sales Return CGST" , "Sales Return SGST"
        data["qty"] = -data["qty"]
        Sales.add_data(self,data)        
class Journal(Voucher) : 
      def __init__(self,data,vchtype = "Journal") : 
          super().__init__()
          self.isdeemed = True 
          self.is_all_ledger = True
          headers = { "date" : data["dt"] , "vchno" :data["inum"]  }
          self.vchtype = vchtype
          Voucher.add_headers(self,headers)
          Voucher.add_ledgers(self,data["ledgers"])
class ClaimService(Voucher) : 
      def __init__(self,data) : 
          super().__init__()
          self.cgst , self.sgst= "Claim Service CGST" , "Claim Service SGST"
          self.isdeemed = True 
          self.is_all_ledger = True
          headers = { "date" : data.iloc[0]["Invoice Date"] , "vchno" :data.iloc[0]["Invoice No"]  }
          self.vchtype = "Claim Service"
          Voucher.add_headers(self,headers)
          self.buyer = data["buyer"].iloc[0] 
          txval , cgst ,sgst  = data.sum()["amount"] , data.sum()['cgst'] , data.sum()['sgst']
          if "Other services" in data.iloc[0]["HSN Description"] :
              ledgers = { "CDT Service" : txval,  "CDT Service Receivable": -(txval+cgst+sgst) + (txval*0.02) ,  
                          "TDS" :  -txval*0.02 , "Outward CGST" :  cgst , "Outward SGST" : sgst  }    
          else : 
                ledgers = { "Sponsership & Promotion " : txval ,  "Sponsership & Promotion - Trade": -txval, "TDS" : -txval*0.02 ,
                      "Service Invoice (Duties & Taxes)" :(txval*0.02) - (cgst+sgst) , "Outward CGST" :  cgst , "Outward SGST" : sgst }
          Voucher.add_ledgers(self,ledgers)
class Purchase(Voucher) :
    def __init__(self,data = None) : 
        super().__init__()
        self.stock_ledger = "Purchase A/c"
        self.vchtype = "Purchase"
        self.purchase_ledger = "HUL Purchase"
        self.taxable_status = "Purchase Taxable"
        self.cgst , self.sgst= "Purchase CGST" , "Purchase SGST"
        self.igst = "Purchase IGST"
        if type(data) != type(None) : 
          self.add_data(data)
    def add_data(self,data) : 
        headers = { "date" : data.iloc[0]["Invoice Date"] , "vchno" :data.iloc[0]["Invoice No"]  }
        Voucher.add_headers(self,headers)
        sums = data.sum()
        igst = sums["igst"] if "igst" in sums else 0
        ledgers = {  self.purchase_ledger : sums['amount'] + sums['cgst'] + sums['sgst'] + igst , 
                    self.cgst :  -sums['cgst'] , self.sgst : -sums["sgst"] , self.igst : -igst }
        #ledgers = {  "HUL Purchase" : data.sum()['amount'] }
        Voucher.add_ledgers(self,ledgers)
        data[["amount", "qty"]] = -data[["amount", "qty"]]
        Voucher.add_stocks(self,data)
        return self 

def getprice(price,stock) : 
   query = price[price["stock"] == stock]
   if len(query.index) > 0 : 
      return round(float(query.iloc[0]["pur rate"]),3)
   else : 
       return 0 
class StockDebitNote(Voucher) : 
    def __init__(self,data,types) : 
      super().__init__()
      self.types = types 
      if types in ["Dse","Nmsm"] : 
          self.debit_ledger = "Purchase Return Receivable"
          self.stock_ledger =   "Pending Purchase Return"
      else : 
        self.debit_ledger = types + " Receivable"
        self.stock_ledger = types 
      self.godwon = types + " Location"
      self.isdeemed = True 
      self.is_all_ledger = True
      headers = { "date" : data["Invoice Date"].iloc[0] , "vchno" :data["Invoice No"].iloc[0]  }
      self.vchtype = "Journal"
      Voucher.add_headers(self,headers) 
      if data["Godown"].iloc[0] == "MAIN GODOWN" : 
        data["qty"] = -data["qty"]
      data["amount"] = round(data["rate"] * data["qty"],3)
      ledgers = { self.debit_ledger : -data["amount"].sum() }
      Voucher.add_stocks(self,data)
      Voucher.add_ledgers(self,ledgers)
    def prepare_stocks(self):
        stocks = pd.DataFrame(self.stocks)
        self.xml_stocks += f"""
		 <ALLLEDGERENTRIES.LIST>
		        	<LEDGERNAME>{self.stock_ledger}</LEDGERNAME>
		        	<GSTOVRDNNATURE>{self.taxable_status}</GSTOVRDNNATURE>
		        	<GSTOVRDNTAXABILITY>Taxable</GSTOVRDNTAXABILITY>
		        	<AMOUNT>{stocks['amount'].sum()}</AMOUNT>
                    <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>"""
        for row in self.stocks : 
                 self.xml_stocks += f"""<INVENTORYALLOCATIONS.LIST>
		            <STOCKITEMNAME>{row['stock']}</STOCKITEMNAME>
		            <AMOUNT>{row['amount']}</AMOUNT>
		            <ACTUALQTY>{row['qty']}</ACTUALQTY>
		            <BILLEDQTY>{row['qty']}</BILLEDQTY> 
                     <GODOWNNAME>{self.godwon}</GODOWNNAME>
	            </INVENTORYALLOCATIONS.LIST>"""
        self.xml_stocks += "</ALLLEDGERENTRIES.LIST>"
                
class Cheque(Voucher) : 
      def __init__(self,data) :
          super().__init__()
          #self.billalloc = True 
          #self.coll_party =  party
          self.is_all_ledger = True
          self.chqno =  data['chqno']
          self.isdeemed = True
          self.bank = "KVB"
          self.vchtype = "Payment"
          self.amt =  -sum(data["ledgers"].values())
          data["ledgers"].update({ self.bank : self.amt  })   
          Voucher.add_headers(self,{ "date" : data["dt"] , "vchno" :data["inum"]  })
          Voucher.add_ledgers(self,data["ledgers"])
      def prepare_ledgers(self):
          super().prepare_ledgers()
          chq_data = f"""
               <BANKALLOCATIONS.LIST>
                <TRANSACTIONTYPE>Cheque</TRANSACTIONTYPE>
                <INSTRUMENTNUMBER>{self.chqno}</INSTRUMENTNUMBER>
                <AMOUNT>{self.amt}</AMOUNT>
               </BANKALLOCATIONS.LIST>
          """
          self.xml_ledgers = self.xml_ledgers.replace(f"<LEDGERNAME>{self.bank}" , chq_data +  f"<LEDGERNAME>{self.bank}")
class Receipt(Journal) : 
       def __init__(self,data,party,bill_ref) : 
           super().__init__(data,vchtype="Receipt")
           self.billalloc = True 
           self.coll_party =  party
           self.bill_ref = bill_ref

def GetVoucherType(data) :
  row = data.iloc[0]
  if  row["type"] == "Pur" and row["Out"] > 0  and row["Godown"] == "MAIN GODOWN" : 
      return "Dse"
  if row["type"] == "LocTran" :
     if row["Godown"] == "SHORTAGE GODOWN" : 
        return "Shortage"
     if row["Godown"] in  ["EXPIRY GODOWN","DAMAGE GODOWN","FROZEN GODOWN"]  :
        return "Damage"
  if row["type"] == "RSTrans" and row["Godown"] == "MAIN GODOWN" : 
     return "Nmsm"
  if row["type"] == "Adj" and row["Godown"] == "MAIN GODOWN" :
      return "Adjustment"
  return False 
def find_moc(fromd,tod) :
    months = pd.date_range(fromd.strftime("%Y-%m-%d"),tod.strftime("%Y-%m-%d"), 
              freq='MS').strftime("%m/%Y").tolist()
    if int(tod.strftime("%d")) > 20 : 
        months.append( (tod + relativedelta(days = 28)).strftime("%m/%Y") )
    return months 

def parse_gstr2_b2bothers(invs,data) : 
    data = data["data"]["docdata"]
    if "b2b" in data.keys() : 
        for b2bs in data["b2b"] : 
            if b2bs["trdnm"] != "HINDUSTAN UNILEVER LIMITED" :
              for b2b in b2bs["inv"] :
                dt = datetime.strptime(b2b["dt"],"%d-%m-%Y")
                b2b_sum = pd.DataFrame(b2b["items"]).sum()
                ledgers = { b2bs["trdnm"] : b2b_sum["txval"]
                          , "HUL Purchase Return" : -(b2b_sum["txval"] + b2b_sum["cgst"] + b2b_sum['sgst'])
                        , "Purchase Return CGST" : b2b_sum["cgst"] , "Purchase Return SGST" : b2b_sum["sgst"] , 
                           "Pending Purchase Return" : -b2b_sum["txval"] , "Purchase Return Receivable" : b2b_sum["txval"] }
                date = b2b["dt"].split("-")[2] + b2b["dt"].split("-")[1] + b2b["dt"].split("-")[0] 
                invs[b2b["ntnum"]] = Journal({"dt":date, "inum" : b2b["ntnum"] ,  "ledgers" : ledgers }, 
                                               "Credit Invoice")
 

def parse_gstr2_cdnr(invs,data) : 
    data = data["data"]["docdata"]
    if "cdnr" in data.keys() : 
        for cdnrs in data["cdnr"] : 
            if cdnrs["trdnm"] == "HINDUSTAN UNILEVER LIMITED" :
              for cdnr in cdnrs["nt"] :
                dt = datetime.strptime(cdnr["dt"],"%d-%m-%Y")
                cdnr_sum = pd.DataFrame(cdnr["items"]).sum()
                ledgers = { "Purchase Return" : cdnr_sum["txval"] , "HUL Purchase Return" : -(cdnr_sum["txval"] + cdnr_sum["cgst"] + cdnr_sum['sgst'])
                        , "Purchase Return CGST" : cdnr_sum["cgst"] , "Purchase Return SGST" : cdnr_sum["sgst"] , 
                           "Pending Purchase Return" : -cdnr_sum["txval"] , "Purchase Return Receivable" : cdnr_sum["txval"] }
                date = cdnr["dt"].split("-")[2] + cdnr["dt"].split("-")[1] + cdnr["dt"].split("-")[0] 
                invs[cdnr["ntnum"]] = Journal({"dt":date, "inum" : cdnr["ntnum"] ,  "ledgers" : ledgers }, 
                                               "Credit Invoice")
 
#invs = {}
def standard_rate(session,cred_data,date) : 
    stock = pd.read_excel(closingstock(session,cred_data,date),skiprows=17)
    stock = stock.rename( columns = {"SKU7":"stock" , "Cur.Stk Value":"value" ,"Units":"qty"}) 
    stock = stock.astype({"value" : float , "qty" : int })
    stock = stock.groupby(by=["stock"]).sum().reset_index()
    stock["rt"] = stock["value"] / stock["qty"]
    xml = ""
    for idx,row in stock.iterrows()  : 
       temp = create_stock(row["stock"])
       opening = f"""
          <STANDARDCOSTLIST.LIST>
          <DATE>{date.strftime("%Y%m%d")}</DATE>
          <RATE>{row['rt']}/nos</RATE>
          </STANDARDCOSTLIST.LIST>
       """
       xml += temp.replace("<PARENT>",opening + "<PARENT>") 
    return xml
def openingstock(session,cred_data,date) : 
    stock = pd.read_excel(closingstock(session,cred_data,date),skiprows=17)
    stock = stock.rename( columns = {"SKU7":"stock" , "Cur.Stk Value":"value" ,"Units":"qty"}) 
    stock = stock.astype({"value" : float , "qty" : int })
    stock = stock.groupby(by=["stock"]).sum().reset_index()
    stock["rt"] = stock["value"] / stock["qty"]
    xml = ""
    for idx,row in stock.iterrows()  : 
       temp = create_stock(row["stock"])
       opening = f"""<OPENINGBALANCE> {row['qty']} nos</OPENINGBALANCE>
       <OPENINGVALUE>-{row['value']}</OPENINGVALUE>
       <BATCHALLOCATIONS.LIST>
         <GODOWNNAME>Main Location</GODOWNNAME>
         <BATCHNAME>Primary Batch</BATCHNAME>
         <OPENINGBALANCE> {row['qty']} nos</OPENINGBALANCE>
         <OPENINGVALUE>-{row['value']}</OPENINGVALUE>
       </BATCHALLOCATIONS.LIST>"""
       xml += temp.replace("<PARENT>",opening + "<PARENT>") 
    with open("test.xml","w+") as f : 
        f.write(header + xml + footer) 
def collection(invs,session,cred_data,fromd,tod) :
  print("coll")
  coll = pd.read_excel(download_collection(session,cred_data,fromd,tod),skiprows=12)
  #coll = pd.read_excel(r"D:\collection.xlsx",skiprows=12)
  print("coll downloaded")
  coll = coll[coll["Status"] != "CAN"]
  coll = coll.dropna(subset=["Collection Date"])
  coll["Date"] = coll["Collection Date"].apply(lambda dt : dt.strftime("%Y%m%d") )
  for idx,row in coll.iterrows() :
      amt , shop , inum   =   float(row["Coll. Amt"]) , row["Party Name"] , row["Collection Refr"]
      ledgers = { shop : amt } 
      if row["Status"] == "CSH" : 
         ledgers["Cash"] =  -amt 
      else : 
          ledgers["KVB"] = -amt
      invs[inum] =  Receipt({"dt" : row["Date"] , "inum" : inum , "ledgers" : ledgers  }, shop , row["Bill No"] )
      invs[inum].buyer = shop
  print("Collection finished")
def sales(invs,session,cred_data,fromd,tod) :  
  print("sales")
  gst  =  pd.read_csv(download_gstr(session,cred_data,fromd,tod)) 
  #gst = pd.read_csv(r"D:\sales.csv")
  print("gst summary donwloaded")
  gst  = gst.rename( columns = { "Amount - Central Tax" : "cgst" , "Amount - State/UT Tax" : "sgst" , "Outlet Name" : "buyer"  ,
                                 "Total Quantity" : "qty" , "Taxable" : "amount" ,"Base Value" : "rate" , "UQC" :"stock"})
  gst["Invoice Date"] = gst["Invoice Date"].apply(lambda dt : dt.split("/")[2] + dt.split("/")[1]  + dt.split("/")[0]  )
  gst = gst.groupby(by = "Invoice No") 
  count = 0
  for inum , data in gst :
      if count%100 == 0 : 
          print(count) 
      count+=1 
      row = data.iloc[0]
      if row["Transactions"] == "SECONDARY BILLING" : 
         inv = Sales(data)
      elif row["Transactions"] == "SALES RETURN" :
        data[["qty","amount","cgst","sgst"]] = -data[["qty","amount","cgst","sgst"]]  
        inv = SalesReturn(data)
        #inum = row["Original Invoice No"] #this is not srt but dev or tks 
      elif row["Transactions"] == "CLAIMS SERVICE" : 
         inv = ClaimService(data) 
      else : 
          continue 
      invs[inum] = inv
  print("invs generated for gstr summary") 
  sales_reg = pd.read_excel(download_sales(session,cred_data,fromd,tod),skiprows =12)
  #sales_reg = pd.read_excel(r"D:\salesreg.xlsx",skiprows =12)
  print("sales summary donwloaded")
  sales_day_book = sales_reg.groupby(by = "BillDate/Sales Return Date") 
  sales_reg = sales_reg.groupby(by = "BillRefNo") 
  
  for inum , data in sales_reg :
    if inum in invs.keys()  :
      buyer = data["Party Name"].iloc[0]
      is_return = (data.iloc[0]["Sal Ret"] != 0 )
      data = dict(data.sum()) 
      inv = invs[inum]
      inv_data = {  buyer : data["BTPR SchDisc"]  - data["TCS Amt"] + data["Adjustments"] + data["Ushop Redemption"] 
                                       + data["OutPyt Adj"] , "BTPR" : -data["BTPR SchDisc"] , "TCS" :data["TCS Amt"] ,
                                     "Outlet Payout" :-data["OutPyt Adj"] , "Ushop" : -data["Ushop Redemption"] , "Adjustments" : -data["Adjustments"] }
      inv_data = { shop : amt for shop,amt in inv_data.items()  if amt!=0  } #filter
      if not is_return : 
          inv.add_ledgers(inv_data) 
      else : 
          inv.add_ledgers({ key: -value for key,value in inv_data.items() }) 
  
  for dt , data in sales_day_book : 
     date = data.iloc[0]["BillDate/Sales Return Date"].strftime("%Y%m%d")
     invs["SCHEME" + date] = Journal({"dt" : date , "inum" : "SCHEME" + date   ,
                               "ledgers" : {"Scheme Discount" : data.sum()["SchDisc"] ,  "Scheme Discount Receivable" : -data.sum()["SchDisc"] }})    
def purchase(invs,session,cred_data,fromd,tod) : 
  #purchase  
  pur = pd.read_excel(download_purchase(session,cred_data,fromd,tod),skiprows = 7)
  pur = pur.dropna(subset=["Invoice Date"])
  pur = pur.rename( columns = {"Item Code" :"stock" , "Purchase Qty Units" :"qty" ,"NetAmt" : "amount" ,
                               "Supplier Invoice No": "Invoice No","CGST Amt" :"cgst","SGST Amt":"sgst" , "IGST Amt":"igst"})
  pur["Invoice Date"] = pur["Invoice Date"].apply(lambda dt : dt.strftime("%Y%m%d") )
  pur['amount'] = (pur['amount'] - pur['cgst'] - pur['sgst'] - pur["igst"]).round(3)
  pur['Invoice No'] = pur['Invoice No'].apply(lambda inum : str(inum).split(".")[0] )
  pur = pur[pur["Invoice Type"] == "EGIR"]
  pur = pur.groupby(by = "Invoice No") 
  for inum , data in pur : 
          invs[inum] = Purchase(data)
def stockdebitnote(invs,session,cred_data,fromd,tod) : 
  price = pd.read_excel( download_price(session,cred_data),skiprows=11,usecols= "B,I,J")
  #price = pd.read_excel("D:\\price.xlsx",skiprows=11,usecols= "B,I,J")
  print("price downloaded")
  price = price.rename(columns = {"Prd.Code" : "stock","Landed Cost/Unit":"rate"})
  price = price.drop_duplicates(subset=["stock"],keep="last")
  trans = pd.read_excel( download_stock_ledger(session,cred_data,fromd,tod),skiprows=11)
  #trans = pd.read_excel(r"D:\stockledger.xlsx",skiprows = 11 ,usecols = "B,E,F,G,H,I,K")
  print("stock ledger downloaded")
  trans = trans.rename(columns ={"PRODUCT CODE" : "stock","Trans. Type":"type","Trans. No.":"Invoice No" })
  trans = trans[trans.apply(lambda row :  (row["type"]!="Sales")  and not ((row["type"]=="Pur") & (row["Out"] == 0)), axis=1) ]
  print(trans[trans["type"] == "Pur"])
  trans["Invoice Date"] = trans["Tran Date"].apply(lambda dt: dt.strftime("%Y%m%d"))
  trans["qty"] = trans.apply( lambda row : row["In"] - row["Out"]  , axis=1)
  inv_main = list(set(trans[trans["Godown"] == "MAIN GODOWN"]["Invoice No"]))
  print("getprice")
  #trans["rate"] = trans["stock"].apply(lambda stock : getprice(price,stock)) 
  price = price[["stock","rate"]]
  trans = trans.merge(price,left_on ="stock", right_on="stock", how="left" ).fillna(value = {"rate" : 0})
  print("getprice finished")
  trans = trans.groupby(by=["Invoice No","Godown"])
  for idx,row in trans : 
       rows = row.iloc[0]
       vchtype = GetVoucherType(row)
       inum = row.iloc[0]["Invoice No"]
       if vchtype != False and inum in inv_main   :
           invs[inum] = StockDebitNote(row,vchtype)

def marketreturn(invs,session,cred_data,fromd,tod) :
  market = download_credit_note(session,cred_data,fromd,tod) 
  market = market[market["Date"].apply(lambda dt : (dt>=fromd) and (dt<=tod) )]
  market["Date"]  = market["Date"].apply(lambda dt : dt.strftime("%Y%m%d"))
  market = market.groupby(by=["Doc Ref NO","Date"])
  for idx,data in market : 
      row = data.iloc[0]
      inum = row["Doc Ref NO"]
      shop , amt =  row["Account"], data.sum()["Adj. Amt"]
      ledger_map = { "From Shortages" : "Shortage Receivable" , "From Market Return" : "Damage Receivable"}
      if row["Narration"]  in  ledger_map.keys() : 
          invs[inum + row["Date"]] = Journal({"dt" : row["Date"], "inum" : inum , "ledgers" : { ledger_map[row['Narration']] : -amt , shop : amt }})
          invs[inum + row["Date"]].buyer = shop 
def claim(invs,session,cred_data,hul,fromd,tod) :
  claim = []
  print("claim start")
  for moc in find_moc(fromd - relativedelta(months = 6) ,tod) : 
   temp = download_claims( session ,cred_data , moc )
   claim.append(pd.read_excel(temp,sheet_name="HUL CLAIMS"))
  claim = pd.concat(claim) 
  #claim.to_excel("claim.xlsx")
  print("claim downloaded")
  claim = claim[claim["CREDIT DATE"].apply(lambda dt : (tod>=dt) and (dt>=fromd)) ]
  claims = {}
  for idx,row in claim.iterrows() :
      for dbnote in row["ADJUSTMENT REFR NO"].split(",") : 
          claims[dbnote] =  {"type" : row["CLAIM TYPE DESCRIPTION"] ,"details" : row["ACTIVITY DESCRIPTION"]}
  
  #service invoice from hul amount . 
  si = claim[claim["ADJUSTMENT REFR NO"].apply(lambda inum : "SI"  ==  inum[:2] )]
  si = si.groupby(by=["ADJUSTMENT REFR NO"])
  for inum,data in si :
       ledger_map = {"Outlet_Pay" : "Outlet Payout" , "Ushop" : "Ushop" , "OTHERS-CLAIM" : "CDT Service Receivable"}
       for types,data in data.groupby(by=["CLAIM TYPE DESCRIPTION"]) : 
           row = data.sum()
           cr_ledger = ledger_map[types] 
           amt = row["CLAIM AMOUNT"]*1.16 #1.18 txval + tax - 0.02 tds
           ledgers = { cr_ledger : amt , "HUL Service Invoice" : -amt }
           dt  = data.iloc[0]["CREDIT DATE"].strftime("%Y%m%d")
           inum = types+"-"+inum
           invs[inum] = Journal({"dt" : dt , "inum" : inum , "ledgers": ledgers} , "Service Invoice")
  
  #hul = pd.read_excel(r"D:\ledger.xlsx")
  hul = hul[hul["Date"].apply(lambda dt : (tod>=dt) and (dt>=fromd)) ]
  hul = hul.rename( columns = {"Document Details":"type"})
  hul = hul[hul["Adj. Amt. (Rs.)"] == 0]
  hul["amt"] = hul["Credit (Rs)"] - hul["Debit (Rs)."]
  hul["Date"] = hul["Date"].apply(lambda dt : dt.strftime("%Y%m%d"))
  hul = hul.dropna(subset=["Doc. No"])
  for idx,row in hul.iterrows() :
      inum  = str(int(row["Doc. No"]))
      amt = row["amt"]
      already = ["Credit Invoice","G/L account document","HUL New Manual Bill","Invoice"]
      if row["type"] == "Rcpt doc - Cheques" : 
          invs[inum] = Cheque({"dt" :row["Date"] , "chqno" : str(row["Reference"]) , "inum" : inum , "ledgers" : {"HUL Cheque" :  -amt }}) 
      elif row["type"] == "Post-tax claim"  : 
          cr_ledger = "Misc Claims"
          dbnote , amt =  str(int(row["Doc. No"])) , row["amt"] 
          if dbnote in claims.keys() : 
              data = claims[dbnote]
              types = data["type"]
              ledger_map = { "STPR" : "Scheme Discount Receivable" , "BTPR" : "BTPR" , "Outlet_Pay" : "Outlet Payout", 
                "Ushop"  : "Ushop" , "OTHERS-CLAIM" : "Other Claims" , "DAMAGE" : "Shortage Receivable", "VENDOR" : "Adjustments" } 
              if types in ledger_map.keys() : 
                 cr_ledger = ledger_map[types]  
          invs[dbnote] = Journal({"dt" :row["Date"] , "inum" : dbnote, "ledgers" : {"HUL Claims" :  -amt , cr_ledger : amt }},"Claim")
      elif row["type"] == "GT Rtn Bill No Tax" : 
          invs[inum] = Journal({"dt" :row["Date"] , "inum" : inum , "ledgers" : {"HUL Claims" :  -amt , "Damage Receivable" : amt }},"Claim")
      elif row["type"] == "AR TDS Receivable" :
         invs[inum] = Journal({"dt" :row["Date"] , "inum" : inum , "ledgers" : {"HUL TDS" :  -amt , "TDS" : amt }})
      else : 
          continue 
          #if row["type"] not in already :       
  print("claim finished")
def party_os(session,cred_data,date) : 
    party = pd.read_excel(download_osreport(session,cred_data,date),skiprows=13)
    party = party.rename( columns = {"O/S Amount":"amount" , "Party Name":"party" })[["party","amount"]]
    party = party.groupby(by =["party"]).sum()
    xml = ""
    for party , data in party.iterrows() :
         if party == "AMMAN STORE-D" : 
             print(data)
         temp = create_master("ledger",party,"Sundry Debtors")
         opening = f"""<OPENINGBALANCE> {-data['amount']} </OPENINGBALANCE>"""
         xml += temp.replace("<PARENT>",opening + "<PARENT>") 
    with open("test.xml","w+") as f : 
        f.write(header + xml + footer) 
    return xml.replace("&" ,"&amp;") 

def creditinvoice(invs,session,fromd,tod) : 
    datas = gst.creditinvoice(session,fromd,tod)
    for data in datas : 
       parse_gstr2_cdnr(invs,data)
def prepare(invs,additional="") : 
  master = ""
  buyers , stocks = [], []
  for inv in invs.values()  :
      if "buyer" in inv.__dict__.keys() : 
          buyers.append(inv.buyer)
      if len(inv.stocks) !=0 : 
           stocks +=  inv.stocks         
  for buyer in list(set(buyers)) :    
          master += create_ledger(buyer,"Sundry Debtors")
  if len(stocks) != 0 : 
   stocks = pd.DataFrame(stocks)
   stocks = stocks.drop_duplicates(subset=["stock"])
   if "stock" in stocks.columns : 
        for stock in list(set(stocks["stock"])) : 
                  master += create_stock(stock)
  xml = master  + "".join([ inv.prepare_xml() for inv in invs.values() ])
  xml = xml.replace("&" ,"&amp;")
  xml = header  + xml + additional + footer
  with open("test.xml","w+") as f : 
      f.write(xml)
  return xml
invs = {}
