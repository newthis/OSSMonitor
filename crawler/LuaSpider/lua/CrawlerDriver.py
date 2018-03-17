# -*- coding:utf-8 -*-
import scrapy
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from scrapy import cmdline

if __name__ == '__main__':
    cmdline.execute("scrapy crawl LuaSpider".split())
    #cmdline.execute("scrapy runspider ./spiders/GolangSpider.py".split())