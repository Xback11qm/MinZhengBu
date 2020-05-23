"""
民政部网站 最新行政区划代码
1.假链接:向主页发请求
2.提取真链接:向假链接发请求，提取真实返回数据的url地址
3.向真链接发请求 提取最终数据
"""
import sys,re

import requests
from lxml import etree
import redis
from hashlib import md5

class MzbSpider:
    def __init__(self):
        self.url = 'http://www.mca.gov.cn/article/sj/xzqh/2020/'
        self.headers = {"User-Agent":'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'}
        #redis实现增量
        self.r = redis.Redis(host='localhost',port=6379,db=4)

    def get_html(self,url):
        html = requests.get(url=url,headers=self.headers,verify=False).text

        return html

    def xpath_func(self,html,xpath_bds):
        p = etree.HTML(html)
        r_list = p.xpath(xpath_bds)

        return r_list

    def md5_func(self,url):
        s = md5()
        s.update(url.encode())

        return s.hexdigest()

    def get_false_url(self):
        false_html = self.get_html(url=self.url)
        false_xpath_bds = '//table/tr[2]/td[2]/a/@href'
        href_list = self.xpath_func(false_html,false_xpath_bds)
        if href_list:
            false_url = 'http://www.mca.gov.cn'+href_list[0]
            finger = self.md5_func(false_url)
            if self.r.sadd('mzb:spider',finger)==1:
                # 开始进行数据抓取
                self.get_real_url(false_url)
            else:
                sys.exit('抓取完成')
        else:
            print('最新月份提取失败')
    def re_func(self,html,regex):
        pattern = re.compile(regex,re.S)
        r_list = pattern.findall(html)

        return r_list

    def get_real_url(self,false_url):
        html = self.get_html(false_url)
        regex = '<span style="float:left;width:0;height:0;">.*?<script>.*?window.location.href="(.*?)".*?</script><script type="text/javascript">'
        real_url_list = self.re_func(html,regex)
        if real_url_list:
           real_url = real_url_list[0]
           self.get_real_html(real_url)
        else:
            sys.exit('无数据')

    def get_real_html(self,real_url):
        html = self.get_html(real_url)
        xpath_bds = '//tr[@height="19"]'
        tr_list = self.xpath_func(html,xpath_bds)
        item={}
        for tr in tr_list:
            code_list = tr.xpath('./td[2]/text()|./td[2]/span/text()')
            name_list = tr.xpath('./td[3]/text()')
            item['code'] = code_list[0].strip() if code_list else None
            item['name'] = name_list[0].strip() if name_list else None
            print(item)

    def run(self):
        self.get_false_url()

if __name__ == '__main__':
    spider = MzbSpider()
    spider.run()

















