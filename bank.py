from datetime import datetime , timedelta
import pandas as pd 
from itertools import combinations
import pickle
from itertools import chain, combinations
def powerset(df,amt):
    df = df.reset_index()
    lens = len(df.index)
    for i in range(0,lens) : 
        for j in range(i+1,lens+1) : 
            temp = df[i:j]["amt"].sum()
            if abs(temp - amt) < 2 : 
                #print(df[i:j]) 
                return df[i:j] 
    return False 

def multi_chq_merger(chqs,coll) :
    count = 0
    not_found = []
    chqs = chqs.groupby(by=["Value Date"])
    c1 , c2 = [] , []
    for dt,chqs in chqs : 
      chqs = chqs.to_dict(orient="records")
      iters = chain.from_iterable(combinations(chqs, r) for r in range(1,len(chqs)+1))
      for comb in iters :  
        #if len([1 for ele in comb if ele in c1]) > 0 : 
        #    continue 
        comb = pd.DataFrame(comb) 
        amt = comb["Credit"].sum()
        df = coll[coll["dt"] >= dt - timedelta(days = 1) ][coll["dt"] - timedelta(days = 5) <= dt ]
        df = df.groupby(by=["party"])
        x = False 
        anss = []
        for party , data in df : 
               #print(desc,data)
               ans = powerset(data,amt) 
               if type(ans) != bool :
                   tmp = ans.to_dict(orient="records")
                   #if len([1 for ele in tmp if ele in c2]) > 0 : 
                   #   continue 
                   comb["bank"] = comb["Description"].apply(lambda x : x.split(":")[-1].split("-")[0]) 
                   if not (comb['bank'] == comb['bank'][0]).all() : 
                       continue 
                   print("Combination : ",comb[["Description","Credit"]] )
                   print(ans)    
                   c1 += comb.to_dict(orient="records")
                   c2 += tmp
                   x = True 
                   break 
        if x : 
            count += len(comb.index) 
    return count                

bank = pd.read_excel(r"D:\kvb bank filter hor.xlsx")
bank = bank.dropna(subset=["Value Date"])
coll = pd.read_pickle(r"coll.pkl")
#bank = bank[4500:]
"""
coll = pd.read_excel(r"D:\\collection.xlsx" , skiprows = 12 )

import pickle
coll = coll[coll["Status"].apply(lambda x : x in ["CHQ","NEFT"])]
coll = coll.rename(columns = {"Bill No" : "inum" ,"Collection Date" : "dt" , "Coll. Amt" : "amt"})
coll["party"] = coll["Party Name"].apply(lambda name : name.split("-")[0])
coll = coll[["dt","inum","party","amt"]] 
with open("coll.pkl","wb+") as f : 
    pickle.dump(coll,f)
dsfdsf

"""
def find(dt,coll,day_bank,leave = False) :
    found = False 
    coll_amt  =  coll["amt"].sum()
    df = day_bank[day_bank["Value Date"] <= dt + timedelta(days = 1)  ][day_bank["Value Date"] + timedelta(days = 5 if leave else 15) >= dt ] #[coll["inum"].apply(lambda x: x not in cor)]       
    df = df.reset_index()
    lens = len(df.index)
    iters = chain.from_iterable(combinations(coll.to_dict(orient="records"), r) for r in range(1,len(coll.index)+1))
    for i in range(0,lens) : 
        for j in range(i+1,lens+1) : 
            bank_amt = df[i:j]["Credit"].sum()
            if leave : 
               for comb in iters : 
                print(pd.DataFrame(comb), abs(bank_amt - pd.DataFrame(comb)["amt"].sum()))
                if abs(bank_amt - pd.DataFrame(comb)["amt"].sum()) < 5 : 
                   print(dt,pd.DataFrame(comb)["amt"].sum(),bank_amt,df[i:j][["Value Date","Credit"]])
                   found = True 
            else :   
               if abs(bank_amt - coll_amt) < 5 : 
                print(dt,coll_amt,bank_amt,df[i:j][["Value Date","Credit"]])
                found = True 
    return found 



#bank = bank[:]
"""
coll_all = coll.sort_values(by = "dt")
bank = bank[bank["Description"].apply(lambda desc :  desc[:6] == "BY CLG" or desc[:7] == "FT - CR" or desc[:7] == "NEFT CR" or desc[:4] == "IMPS" or desc[:3] == "UPI")]

day_bank = bank.groupby( by = ["Value Date"]).sum().reset_index().sort_values(by = ["Value Date"])
day_coll = coll_all.groupby( by = ["dt"])
for dt , coll in day_coll :    
   if not  find(dt,coll,day_bank,False) : 
       if  find(dt,coll,day_bank,True) : 
          print(dt , "round 2")
          continue 
       print(dt , "Not found")
   else : 
       print(dt , "round 1")
print(1)
"""
bank = bank[bank["Description"].apply(lambda desc :  desc[:6] == "BY CLG")]

miss = [] 
cor = []
corr = 0 
wrong = 0
bank = bank[bank["Value Date"] >= datetime(2021,4,1)][bank["Value Date"] <= datetime(2021,4,20)]
#multi_chq_merger(bank,coll)

coll["Collection Refr"] = coll["inum"] + coll["dt"].apply(lambda x : x.strftime("%d%m%Y"))
count = 0
not_found_bank , found_bills = [],[]
for idx,row in bank.iterrows() :
      desc = row["Description"] 
      dt = row["Value Date"]
      err =  1
      name = desc.split(":")[1]
      amt = row["Credit"]
      df = coll[coll["dt"] >= dt - timedelta(days = 1) ][coll["dt"] - timedelta(days = 15) <= dt ] #[coll["inum"].apply(lambda x: x not in cor)] 
      df = df.groupby(by=["party"])
      found = False
      
      for party , data in df : 
               ans = powerset(data,amt)
               if type(ans) != bool :
                   tmp = list(ans["Collection Refr"])
                   found_bills += tmp
                   #print(ans)
                   found = True
                   count += 1 
                   break
      if not found : 
         print(desc,amt,found)
         print( "wrong : " , len(not_found_bank)) 
         print( "correct  : ", count)
         not_found_bank.append(row) 

tmp = pd.DataFrame(found_bills , columns = ["coll ref"])
tmp["is_na"] = 1 
tmp = coll.merge(tmp , left_on = "Collection Refr", right_on = "coll ref" , how = "left")
filtered_coll = tmp[ tmp["is_na"].isna() ]
not_found_bank= pd.DataFrame(not_found_bank)
print("Merger :")
print(len(not_found_bank.index))
count += multi_chq_merger(not_found_bank,coll)
print(count , len(bank.index) - count )                
                
                   
                 