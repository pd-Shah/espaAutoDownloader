from USGSInfo import AccountInfo, GeoInfo
from espa_order_download import Api
import json

import schedule
import time
import datetime

# def job():
#     print("I'm working...")
#
# schedule.every(1).seconds.do(job)
#
# while True:
#     schedule.run_pending()
#     time.sleep(10)

def automatic_dl():
    info=AccountInfo(username, email, password)
    with Api(info.username, info.password, geo.host) as api:
        order_list=json.loads(api.get_ready_to_download())
        for order in order_list:
            api.download_manager(api.get_dl_link(order))

automatic_dl()
