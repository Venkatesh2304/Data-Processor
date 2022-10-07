import requests 
session = requests.Session()
url = "https://web3.inpartner.unilever.com/sap/bc/ui5_ui5/sap/zpmodel/index.html"
login_page = session.get(url)
xsrf = login_page.text.split("sap-login-XSRF")[1].split('"')[2][:-6] + "="
form = { "sap-system-login-oninputprocessing": "onLogin",
"sap-urlscheme": "",
"sap-system-login": "onLogin",
"sap-system-login-basic_auth":"" ,
"sap-client": 100 ,
"sap-language": "EN",
"sap-accessibility": "",
"sap-login-XSRF": xsrf,
"sap-system-login-cookie_disabled": "",
"sap-hash": "",
"sap-user": "R41A392",
"sap-password": "Mosl2121@@",
"sap-client": 100}
auth = session.post(url, data = form , headers= {"Content-Type": "application/x-www-form-urlencoded"})
d = session.post("https://web3.inpartner.unilever.com/sap/opu/odata/sap/YNWG_VARIANTS_SRV/$batch?sap-client=100")