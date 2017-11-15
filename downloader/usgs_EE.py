import json
import requests
from USGSInfo import AccountInfo

class LoginError(Exception):
    pass


class EarthExplorer():
    def __init__(self, username, password):
        self.username=username
        self.password=password
        self._login()

    def _login(self):
        try:
            # url="""https://earthexplorer.usgs.gov/inventory/json/v/1.4.0/login?jsonRequest=%7B"username"%3A"{0}"%2C"password"%3A"{1}"%2C"catalogId"%3A"EE"%7D"""
            # url.format(username,password)
            # res=requests.get(url)
            res=requests.get("""https://earthexplorer.usgs.gov/inventory/json/v/1.4.0/login?jsonRequest=%7B"username"%3A"{0}"%2C"password"%3A"{1}"%2C"catalogId"%3A"EE"%7D""".format(self.username, self.password))

            if str(res.status_code) == "200":
                print(res.json())
                self.key=res.json()["data"]
        except Exception:
            raise LoginError("loging failed!")

    def search():
        https://earthexplorer.usgs.gov/inventory/json/v/1.4.0/search?jsonRequest={"apiKey":"5b9ae7cc23bb4297b3a42184db0cbc70","datasetName":"LANDSAT_8_C1","months":[3],"includeUnknownCloudCover":true,"sortOrder":"ASC"}
        
if __name__ =="__main__":
    username='hamidsalehi'
    password='88421038h'
    email="hamidsalehi2007@gmail.com"
    ee=EarthExplorer(username, password)
    print(ee.key)
