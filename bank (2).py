#with open("D:\\Master.xml","r") as f : 
#    xml = f.read()
#    xml = [  ele for ele in xml.split("<TALLYMESSAGE") if "Sundry Debtor" not in ele "<STOCKITEM" not in ele ]
#    print(len(xml))
#    xml = "<TALLYMESSAGE".join(xml)
#with open("D:\\Primary Master.xml","w+") as f : 
#      f.write(xml)
#print(1)

with open("E:\\downloads\\test (1).xml") as f : 
    xml = f.read().split("<TALLYMESSAGE")  
    xml = [xml[0]] + [ e for e in xml if "SCHEME" in e ]
    xml = "<TALLYMESSAGE".join(xml)
with open("E:\\downloads\\test (2).xml","w+") as f : 
      f.write(xml)
print(1)
    
