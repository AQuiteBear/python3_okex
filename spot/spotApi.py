# coding=utf-8
# python3
# @Date    : 2019-10-20 15:40:03

import base64
import datetime
import hashlib
import hmac
import json
import urllib
import urllib.parse
import urllib.request
import requests
from .consts import *


class Client(object):
    def __init__(self, api_key, api_seceret_key):
        # API 请求地址
        self.MARKET_URL = URL_MARKET
        self.TRADE_URL = URL_TRADE
        self.ACCESS_KEY = api_key
        self.SECRET_KEY = api_seceret_key

    '''直接请求'''

    def http_get_request(self, url, params, add_to_headers=None):
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
        }
        if add_to_headers:
            headers.update(add_to_headers)
        postdata = urllib.parse.urlencode(params)
        response = requests.get(url, postdata, headers=headers, timeout=5)
        try:

            if response.status_code == 200:
                return response.json()
            else:
                return
        except BaseException as e:
            print("httpGet failed, detail is:%s,%s" % (response.text, e))
            return

    def http_post_request(self, url, params, add_to_headers=None):
        headers = {
            "Accept": "application/json",
            'Content-Type': 'application/json'
        }
        if add_to_headers:
            headers.update(add_to_headers)
        postdata = json.dumps(params)
        response = requests.post(url, postdata, headers=headers, timeout=10)
        try:

            if response.status_code == 200:
                return response.json()
            else:
                return
        except BaseException as e:
            print("httpPost failed, detail is:%s,%s" % (response.text, e))
            return

    '''需要添加公共加密参数的请求'''

    def api_key_get(self, params, request_path):
        method = 'GET'
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        params.update({'AccessKeyId': self.ACCESS_KEY,
                       'SignatureMethod': 'HmacSHA256',
                       'SignatureVersion': '2',
                       'Timestamp': timestamp})

        host_url = self.TRADE_URL
        host_name = urllib.parse.urlparse(host_url).hostname
        host_name = host_name.lower()
        params['Signature'] = self.createSign(params, method, host_name, request_path, self.SECRET_KEY)

        url = host_url + request_path
        return self.http_get_request(url, params)

    def api_key_post(self, params, request_path):
        method = 'POST'
        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
        params_to_sign = {'AccessKeyId': self.ACCESS_KEY,
                          'SignatureMethod': 'HmacSHA256',
                          'SignatureVersion': '2',
                          'Timestamp': timestamp}

        host_url = self.TRADE_URL
        host_name = urllib.parse.urlparse(host_url).hostname
        host_name = host_name.lower()
        params_to_sign['Signature'] = self.createSign(params_to_sign, method, host_name, request_path, self.SECRET_KEY)
        url = host_url + request_path + '?' + urllib.parse.urlencode(params_to_sign)
        return self.http_post_request(url, params)

    '''签名函数'''

    def createSign(self, pParams, method, host_url, request_path, secret_key):
        sorted_params = sorted(pParams.items(), key=lambda d: d[0], reverse=False)
        encode_params = urllib.parse.urlencode(sorted_params)
        payload = [method, host_url, request_path, encode_params]
        payload = '\n'.join(payload)
        payload = payload.encode(encoding='UTF8')
        secret_key = secret_key.encode(encoding='UTF8')

        digest = hmac.new(secret_key, payload, digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(digest)
        signature = signature.decode()
        return signature

    '''基础信息'''

    # 获取支持的交易对
    def get_symbols(self):
        params = {}
        url = self.MARKET_URL + URL_get_symbols
        return self.http_get_request(url, params)

    # 获取服务器时间
    def get_timestamp(self):
        params = {}
        url = self.MARKET_URL + URL_get_timestamp
        return self.http_get_request(url, params)

    # 获取支持的币种
    def get_currencys(self):
        params = {}
        url = self.MARKET_URL + URL_get_currencys
        return self.http_get_request(url, params)

    '''行情接口'''

    # 获取KLine
    def get_kline(self, symbol, period, size=150):
        """
        :param symbol:  例如: btcusdt
        :param period: 可选值：{1min, 5min, 15min, 30min, 60min, 1day, 1mon, 1week, 1year }
        :param size:   选值： [1,2000]
        :return:
        """
        params = {'symbol': symbol,
                  'period': period,
                  'size': size}

        url = self.MARKET_URL + URL_get_kline
        return self.http_get_request(url, params)

    # 获取merge ticker
    def get_ticker(self, symbol):
        """
        :param symbol:
        :return:
        """
        params = {'symbol': symbol}

        url = self.MARKET_URL + URL_get_ticker
        return self.http_get_request(url, params)

    # Tickers detail
    def get_tickers(self):
        """
        :return:
        """
        params = {}
        url = self.MARKET_URL + URL_get_tickers
        return self.http_get_request(url, params)

    # 获取盘口深度数据
    def get_depth(self, symbol, type):
        """
        :param symbol 例如： btcusdt
        :param type: 可选值：{ percent10, step0, step1, step2, step3, step4, step5 }
        :return:
        """
        params = {'symbol': symbol,
                  'type': type}

        url = self.MARKET_URL + URL_get_depth
        return self.http_get_request(url, params)

    # 获取指定货币对24小时成交量数据
    def get_detail(self, symbol):
        """
        :param symbol
        :return:
        """
        params = {'symbol': symbol}
        url = self.MARKET_URL + URL_get_detail
        return self.http_get_request(url, params)

    '''
    Trade/Account API
    '''
    # 首次运行可通过get_accounts()获取acct_id,然后直接赋值,减少重复获取。
    ACCOUNT_ID = 0

    def get_accounts(self):
        params = {}
        return self.api_key_get(params, URL_get_accounts)

    # 获取当前账户资产
    def get_balance(self, acct_id=None):
        """
        :param acct_id 账户类型 spot：现货账户， margin：逐仓杠杆账户，otc：OTC 账户，
                                point：点卡账户，super-margin：全仓杠杆账户
        """

        if not acct_id:
            accounts = self.get_accounts()
            acct_id = accounts['data'][0]['id']

        params = {"account-id": acct_id}
        return self.api_key_get(params, URL_get_balance.format(acct_id))

    # 创建并执行订单
    def send_order(self, amount, symbol, _type, source='api', price='NA'):
        """
        :param amount:
        :param source: 如果使用借贷资产交易，请在下单接口,请求参数source中填写'margin-api'
        :param symbol:  例如btcusdt
        :param _type: 可选值 {buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖}
        :param price: 默认 NA
        :return:
        """
        global ACCOUNT_ID
        try:
            accounts = self.get_accounts()
            acct_id = accounts['data'][0]['id']
        except BaseException as e:
            print('get acct_id error.%s' % e)
            acct_id = ACCOUNT_ID

        params = {"account-id": acct_id,
                  "amount": amount,
                  "symbol": symbol,
                  "type": _type,
                  "source": source,
                  'price': price}
        return self.api_key_post(params, URL_send_order)

    # 撤销订单
    def cancel_order(self, order_id):
        """
        :param order_id: 订单号
        :return:
        """
        params = {}
        return self.api_key_post(params, URL_cancel_order.format(order_id))

    # 查询某个订单
    def order_info(self, order_id):
        """
        :param order_id:
        :return:
        """
        params = {}
        return self.api_key_get(params, URL_order_info.format(order_id))

    # 查询某个订单的成交明细
    def order_matchresults(self, order_id):
        """
        :param order_id:
        :return:
        """
        params = {}
        return self.api_key_get(params, URL_order_matchresults.format(order_id))

    # 查询当前委托、历史委托
    def orders_list(self, symbol, states, types=None, start_date=None, end_date=None, _from=None, direct=None,
                    size=None):
        """
        :param symbol:
        :param states: 可选值 {pre-submitted 准备提交, submitted 已提交, partial-filled 部分成交, partial-canceled 部分成交撤销, filled 完全成交, canceled 已撤销}
        :param types: 可选值 {buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖}
        :param start_date:
        :param end_date:
        :param _from:
        :param direct: 可选值{prev 向前，next 向后}
        :param size:
        :return:
        """
        params = {'symbol': symbol,
                  'states': states}
        if types:
            params['types'] = types
        if start_date:
            params['start-date'] = start_date
        if end_date:
            params['end-date'] = end_date
        if _from:
            params['from'] = _from
        if direct:
            params['direct'] = direct
        if size:
            params['size'] = size
        return self.api_key_get(params, URL_orders_list)

    # 查询当前成交、历史成交
    def orders_matchresults(self, symbol, types=None, start_date=None, end_date=None, _from=None, direct=None,
                            size=None):
        """

        :param symbol: 例如：btcusdt
        :param types: 可选值 {buy-market：市价买, sell-market：市价卖, buy-limit：限价买, sell-limit：限价卖}
        :param start_date:
        :param end_date:
        :param _from:
        :param direct: 可选值{prev 向前，next 向后}
        :param size:
        :return:
        """
        params = {'symbol': symbol}

        if types:
            params['types'] = types
        if start_date:
            params['start-date'] = start_date
        if end_date:
            params['end-date'] = end_date
        if _from:
            params['from'] = _from
        if direct:
            params['direct'] = direct
        if size:
            params['size'] = size
        return self.api_key_get(params, URL_orders_matchresults)

    # 查询所有当前帐号下未成交订单
    def open_orders(self, account_id, symbol, side='', size=10):
        """
        :param account_id: 账户类型
        :param symbol: symbol:例如：btcusdt
        :param side: buy”或“sell”，缺省将返回所有符合条件尚未成交订单
        :param size: 0-100,默认100
        :return:
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
        if account_id:
            params['account-id'] = account_id
        if side:
            params['side'] = side
        if size:
            params['size'] = size

        return self.api_key_get(params, URL_open_orders)

    # 批量取消符合条件的订单
    def cancel_open_orders(self, account_id, symbol, side='', size=10):
        """
        :param account_id:
        :param symbol: symbol:例如：btcusdt
        :param side: buy”或“sell”，缺省将返回所有符合条件尚未成交订单
        :param size: 0-100,默认100
        :return:
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
        if account_id:
            params['account-id'] = account_id
        if side:
            params['side'] = side
        if size:
            params['size'] = size

        return self.api_key_post(params, URL_cancel_open_orders)

