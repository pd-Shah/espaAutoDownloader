import requests
import json
import threading
from warnings import warn

DOWNLOAD_FILE_DIR=      'Files/DownloderApp/Landsat/'
SUBMITTED_ORDER_IDS_DIR="Files/DownloderApp/system_reports/order_ids.txt"
READY_TO_DOWNLOAD_DIR=  "Files/DownloderApp/system_reports/ready_to_download.txt"


class Api(object):
    '''working with espa api
        site: https://github.com/USGS-EROS/espa-api
    '''

    def __init__(self, username, password, host):
        self.host = host
        self.username = username
        self.password = password

    def _api_request(self, endpoint, verb='get', body=None, uauth=None):
        """simple way to interact with the ESPA JSON REST API """
        auth_tup = uauth if uauth else (self.username, self.password)
        response = getattr(requests, verb)(self.host + endpoint, auth=auth_tup, json=body)
        print('{} {}'.format(response.status_code, response.reason))
        data = response.json()
        print(data)
        if isinstance(data, dict):
            messages = data.pop("messages", None)
            if messages:
                print(json.dumps(messages, indent=4))
        try:
            response.raise_for_status()
        except Exception as e:
            print(e)
            return None
        else:
            return data

    def get_user_info(self):
        ''''GET /api/v1/user'
            Basic call to get the current user's information
        '''
        resp = self._api_request('user')
        return(json.dumps(resp, indent=4))

    def available_products(self, product):
        ''''GET /api/v1/available-products
            Call to demonstrate what is returned from available-products
        '''
        avail_list={'inputs':product}
        resp = self._api_request('available-products', body=avail_list)
        return(json.dumps(resp, indent=4))

    def available_projection_parameters(self):
        '''GET /api/v1/projections
            Call to show projection parameters that are accepted
        '''
        projs = self._api_request('projections')
        return json.dumps(projs, indent=4)

    def product_builder_RT(self, start_date, end_date, path="168", row="033"):
        '''build:
        "LC08_L1TP_rowpath_startdate_enddate_01_RT"
        path="167", row="033" => moghan
        '''
        rt="LC08_L1TP_{}{}_{}_{}_01_RT".format(path, row, start_date, end_date)
        return [rt, ]

    def product_builder_T1(self, start_date, end_date, path="168", row="033"):
        '''build:
        "LC08_L1TP_rowpath_startdate_enddate_01_T1"
        path="167", row="033" => moghan
        '''
        t1="LC08_L1TP_{}{}_{}_{}_01_T1".format(path, row, start_date, end_date)
        return [t1, ]

    def product_builder_T2(self, start_date, end_date, path="168", row="033"):
        '''build:
        "LC08_L1GT_rowpath_startdate_enddate_01_T2"
        path="167", row="033" => moghan
        '''
        t2="LC08_L1GT_{}{}_{}_{}_01_T2".format(path, row, start_date, end_date)
        return [t2, ]

    def query_builder(self, order_template, inputs, products, projection, note, resampling_method, order_format):
        '''make query for order
        fill template by args
        '''
        order_template['note'] = note
        order_template['olitirs8_collection']['inputs'] =inputs
        order_template['olitirs8_collection']['products'] =products
        order_template['projection'] = projection
        order_template['format'] = order_format
        order_template['resampling_method']=resampling_method
        return order_template

    def make_new_order(self, order_template, file_name=SUBMITTED_ORDER_IDS_DIR):
        '''POST /api/v1/order'
            to Place the order into the system.
        '''
        resp = self._api_request('order', verb='post', body=order_template)
        if "status" in dict(resp):
            if dict(resp)["status"]==200 :
                with open(file_name,"a") as order_ids:
                    order_ids.write(resp['orderid'] +"\n")

        return resp

    def _check_file_size(self, file_name, file_size=1000):
        '''check order_ids.txt size
            file always has file_size members and delete others
        '''
        check=False
        with open(file_name, "r") as order_ids_file:
            order_ids=order_ids_file.readlines()
            if len(order_ids) > file_size:
                check=True
                for i in range(len(order_ids)-file_size):
                    order_ids.pop(0)
                save_list=order_ids

        if check:
            with open(file_name, "w") as order_ids:
                order_ids.writelines(save_list)

    def order_state(self, order_id):
        '''Check the status of an order
        'GET /api/v1/item-status/'
        '''
        resp = self._api_request('item-status/{0}'.format(order_id))
        return json.dumps(resp, indent=4)


    def download_manager(self, url, destination=DOWNLOAD_FILE_DIR, try_number="10", time_out="60"):
        #threading.Thread(target=self._wget_dl, args=(url, destination, try_number, time_out, log_file)).start()
        if self._wget_dl(url, destination, try_number, time_out) == 0:
            print(url+ "dowload successfully done.")
            return True
        else:
            warn(url+ " failed to dowload.")
            return False


    def _wget_dl(self,url, destination, try_number, time_out):
        import subprocess
        command=["wget", "-c", "-P", destination, "-t", try_number, "-T", time_out , url]
        try:
            download_state=subprocess.call(command)
        except Exception as e:
            print(e)
        #if download_state==0 => successfull download
        return download_state

    def get_dl_link(self, order_id):
        """if order complete then return download links
        Once the order is completed or partially completed, can get the download url's
        """
        dl_link=[]
        resp=json.loads(self.order_state(order_id))
        return resp[order_id][0]["product_dload_url"]


    def get_ready_to_download(self):
        filters = {"status": ["complete"]}  # Here, we ignore any purged orders
        resp = self._api_request('list-orders', body=filters)
        return json.dumps(resp, indent=4)

    # def set_ready_download(self):
    #     '''
    #     this making order check if order is readey to download
    #     then add it to the list.
    #     '''
    #     ready_list=[]
    #     with open(READY_TO_DOWNLOAD_DIR, mode="a") as ready_list_file:
    #         ready_list_file.write(ready_list)
    #
    # def ready_download_file_manager(self):
    #     with open(SUBMITTED_ORDER_IDS_DIR, "r") as submit_orders, open(READY_TO_DOWNLOAD_DIR, "w") as ready_ld:
    #         orders= submit_orders.readlines()
    #
    #         for order_id in orders:
    #             order=self.order_state(order_id)
    #             try:
    #                 state=[items[0]["status"] for items in order.values()][0]
    #             except:
    #                 warn(order + " order check failed.")
    #
    #             if state != "purged":
    #                 ready_ld.write(order_id)
    #
    #             else:
    #                 warn(order+" is purged.")
    #
    # def operating_download(self):


    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


if __name__ == '__main__':
    from USGSInfo import AccountInfo, GeoInfo
    start_date="2015-04-01"
    end_date="2015-05-01",
    geo=GeoInfo(start_date, end_date)

    username='hamidsalehi'
    password='88421038h'
    email="hamidsalehi2007@gmail.com"
    info=AccountInfo(username, email, password)

    with Api(info.username, info.password, geo.host) as api:
        #user info
        res=api.get_user_info()
        print(res)

        # #build product
        # products_list=api.product_builder_RT("20170425", "20170425")
        # print(products_list)
        #
        #
        # #available products
        # res=api.available_products(products_list)
        # print(res)
        #
        # #projection parameters that are accepted
        # res=api.available_projection_parameters()
        # print(res)
        #
        # products= [
        #     "source_metadata",
        #     "l1",
        #     "toa",
        #     "bt",
        #     "cloud",
        #     "sr",
        #     "sr_ndvi",
        #     "sr_evi",
        #     "sr_savi",
        #     "sr_msavi",
        #     "sr_ndmi",
        #     "sr_nbr",
        #     "sr_nbr2",
        #     "stats"
        # ]
        # #make an order
        # projection =   {
        #                     "lonlat":None
        #                 }
        #
        # #build a query
        # query=api.query_builder(geo.order_template, products_list, products, projection, "this is note", 'nn', 'gtiff')
        # print(json.dumps(query, indent=4))
        #
        # #make order
        # order=api.make_new_order(query)
        # print(order)
        #
        #
        # #state of orders:
        # print(api.order_state("hamidsalehi2007@gmail.com-05012017-010655-351"))
        #
        # #download links
        # dl_list=(api.get_dl_link("hamidsalehi2007@gmail.com-05012017-010655-351"))
        # print(dl_list)
        #
        # #download
        # for link in dl_list:
        #     api.download_manager(link)
        #
        # print("during dl")
