import pandas as pd 
from sales import * 
def hor_sales(invs = {}) : 
   sales = pd.read_excel("D:\\hor sales.xlsx")
   sales =  sales.rename( columns = {"Invoice Number":"Invoice No", "Customer Name" : "buyer" , "SKU Code":"stock" , "Base Quantity" : "qty" , "Taxable Amount": "amount" , 
									 "CGST Amount": "cgst" , "SGST/UGST Amount" : "sgst" })
   sales["buyer"] = "Horlics Sales Register"
   sales["Invoice Date"] = sales["Invoice Date"].apply(
           lambda dt : dt.strftime("%Y%d%m") if type(dt)!=str else dt.split("-")[2] + dt.split("-")[1] + dt.split("-")[0] )
   sales = sales.groupby(by = ["Invoice No"])
   for inum,row in sales : 
    inv = Sales()
    inv.stock_ledger = "Horlics Sales"
    inv.cgst , inv.sgst = "Horlics Sales CGST" ,"Horlics Sales SGST"
    inv.igst = "Horlics Sales IGST"
    inv.add_data(row) 
    invs[inum] = inv 
    #print(inum)
def hor_purchase(invs) : 
   pur = pd.read_excel("D:\\hor pur.xlsx")
   pur =  pur.rename( columns = {"Company Invoice Number":"Invoice No" , "Product Code":"stock" , "Salable Quantity" : "qty" , "Taxable Amount": "amount" , 
									 "CGST Amount": "cgst" , "SGST/UGST Amount" : "sgst" })
   pur["Invoice Date"] = pur["Invoice Date"].apply(
           lambda dt : dt.strftime("%Y%d%m") if type(dt)!=str else dt.split("-")[2] + dt.split("-")[1] + dt.split("-")[0] )
   pur = pur.groupby(by = ["Invoice No"])
   for inum,row in pur : 
    inv = Purchase()
    inv.stock_ledger = "Horlics Purchase"
    inv.purchase_ledger = "Horlics"
    inv.cgst , inv.sgst = "Horlics Purchase CGST" ,"Horlics Purchase SGST"
    inv.igst = "Horlics Purchase IGST"
    inv.add_data(row) 
    invs[inum] = inv 
def hor_stock_op():
   xml = ""
   stock = pd.read_excel(r"D:\hor stock op.xlsx")
   stock = stock.rename(columns = {"Product Code":"stock","Closing Stock":"qty","Total Value":"value"})
   stock = stock.groupby(by = ["stock"]).sum().reset_index()
   for idx,row in stock.iterrows() : 
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
def hor_stock_trans(invs) : 
    df = pd.read_excel(r"D:\StkGrpSum.xlsx")
    df["Invoice Date"] = "20210625"
    df["Invoice No"] = "Stock Transfer Horlics"
    inv = StockDebitNote(df,"Adjustment")
    invs["stocktr"] = inv 
def hul_stock_trans(invs) : 
    df = pd.read_excel(r"D:\hul stock entry.xlsx")
    df["Invoice Date"] = "20210625"
    df["Invoice No"] = "Stock Transfer HUL"
    #df["qty"] = -df["qty"]
    inv = StockDebitNote(df,"Adjustment")
    invs["stocktr"] = inv 
def hor_coll(invs) :
    coll = pd.read_excel(r"D:\hor coll.xlsx",skiprows =4)
    for idx,row in coll.iterrows() : 
        dt = row["Date"].strftime("%Y%m%d")
        if row["Cash"] != 0 : 
          amt ,inum  = row["Cash"] , (dt + "HORLICS CSH")
          data = { "dt" : dt  , "inum" :  inum , "ledgers" : { "Horlics Sales Register" : amt , "Cash( Horlics )" : -amt } }
          invs[inum] = Receipt(data) 
        amt= row["Cheque"] + row["Bank Transfer"]
        if amt != 0 : 
            inum  = dt + "HORLICS CHQ"
            data = { "dt" : dt  , "inum" :  inum , "ledgers" : { "Horlics Sales Register" : amt  } , "chqno" : "" }
            invs[inum] = Cheque(data)





invs = {}
hor_coll(invs) 
prepare(invs)
print("done")