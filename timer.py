# -*- coding:utf-8 -*-
import time
import requests
import json

import datetime
from jd_logger import logger
from config import global_config


class Timer(object):
    def __init__(self, sleep_interval=0.5):
        # '2018-09-28 22:45:50.000'
        date_now = datetime.datetime.now()
        today_str = datetime.datetime.strftime(date_now,"%Y-%m-%d")
        tmp_buy_time = datetime.datetime.strptime(today_str + ' ' + global_config.getRaw('config', 'buy_time'),
                                         "%Y-%m-%d %H:%M:%S.%f")
        tmp_buy_time_ms = int(time.mktime(tmp_buy_time.timetuple()) * 1000.0 + tmp_buy_time.microsecond / 1000)
        tmp_now_ms = int(time.mktime(date_now.timetuple()) * 1000.0 + date_now.microsecond / 1000)
        if tmp_now_ms > (tmp_buy_time_ms + 2 * 60 * 1000):
            next_date = date_now + datetime.timedelta(days=1)
            next_date_str = datetime.datetime.strftime(next_date,"%Y-%m-%d")
            next_tmp_buy_time = datetime.datetime.strptime(next_date_str + ' ' + global_config.getRaw('config', 'buy_time'),
                                                  "%Y-%m-%d %H:%M:%S.%f")
            self.buy_time = next_tmp_buy_time
        else:
            self.buy_time = tmp_buy_time

        self.buy_time_ms = int(time.mktime(self.buy_time.timetuple()) * 1000.0 + self.buy_time.microsecond / 1000)
        self.sleep_interval = sleep_interval

        self.diff_time = self.local_jd_time_diff()

    def jd_time(self):
        """
        从京东服务器获取时间毫秒
        :return:
        """
        url = 'https://a.jd.com//ajax/queryServerData.html'
        ret = requests.get(url).text
        js = json.loads(ret)
        return int(js["serverTime"])

    def local_time(self):
        """
        获取本地毫秒时间
        :return:
        """
        return int(round(time.time() * 1000))

    def local_jd_time_diff(self):
        """
        计算本地与京东服务器时间差
        :return:
        """
        return self.local_time() - self.jd_time()

    def start(self):
        logger.info('正在等待到达设定时间:{}，检测本地时间与京东服务器时间误差为【{}】毫秒'.format(self.buy_time, self.diff_time))
        while True:
            # 本地时间减去与京东的时间差，能够将时间误差提升到0.1秒附近
            # 具体精度依赖获取京东服务器时间的网络时间损耗
            if self.local_time() - self.diff_time >= self.buy_time_ms:
                logger.info('时间到达，开始执行……')
                break
            else:
                time.sleep(self.sleep_interval)
