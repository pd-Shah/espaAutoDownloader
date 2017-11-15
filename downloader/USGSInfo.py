import json


class AccountInfo:
    def __init__(self, username, email, password):
        self.email=email
        self.username=username
        self.password=password
        self.save=True

class GeoInfo:
    def __init__(self, start_date, end_date, dataset="LANDSAT_8", node="EE"):
        self.start_date=start_date
        self.end_date=end_date
        self.dataset=dataset
        self.node=node
        self.host='https://espa.cr.usgs.gov/api/v1/'
        self.order_template=json.loads(
                        '''{
                            "note": "",
                            "olitirs8_collection": {
                                                    "inputs": [],
                                                    "products": []
                                                    },
                            "projection": {},
                            "resampling_method": "nn",
                            "format": "gtiff"
                            }''')
