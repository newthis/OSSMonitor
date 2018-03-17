# -*- coding:utf-8 -*-
import requests,time,random

import scrapy

import json
import urllib


from lua.items import LuaItem




class LuaSpider(scrapy.Spider):
    name = 'LuaSpider'
    custom_settings = {'DOWNLOAD_DELAY': 1, 'DOWNLOAD_TIMEOUT':30000}
    # start_urls = ['http://go-search.org/search']
    # host_prefix = "http://go-search.org"

    def __init__(self, **kwargs):
        self.start_urls = 'https://luarocks.org/m/root'
        self.host_prefix = 'https://luarocks.org'

        super(LuaSpider, self).__init__(self, **kwargs)




    def __str__(self):
        return "LuaSpider"

    def start_requests(self):



        yield scrapy.Request(url = self.start_urls, callback = self.parseLuaLinks)





    def parseLuaLinks(self, response):
        unitLinks = response.xpath('/html/body/div[1]/div[2]/div/div[3]/div/div[1]/a/@href').extract()
        for unit in unitLinks:
            unitUrl = self.host_prefix + unit.strip()
            yield scrapy.Request(url = unitUrl, callback = self.parseLuaDetails)


        pageIndi = response.xpath("//div[@class='pager']/span/text()").extract()
        if len(pageIndi) > 0:
            text = pageIndi[0].strip()
            splits = text.replace('Page','').strip().split('of')
            curPage = int(splits[0].strip())
            wholePage = int(splits[1].strip())
            if curPage < wholePage:
                curPage = curPage + 1
                urlNext = 'https://luarocks.org/m/root?page='+str(curPage)
                yield scrapy.Request(url = urlNext, callback = self.parseLuaLinks)

    def parseLuaDetails(self, response):
        basicInfo = {}
        stripedUrl = response.url.strip()
        indi = stripedUrl.rfind('/')
        pname = stripedUrl[indi+1:]
        pname = pname.strip()
        basicInfo['official_license'] = ''
        basicInfo['project_name'] = pname
        basicInfo['official_license'] = ''
        basicInfo['project_desc'] = ''
        basicInfo['homepage'] = ''
        basicInfo['total_downloads'] = 0
        basicInfo['project_url'] = response.url.strip()
        basicInfo['uploader'] = response.url.replace(pname,'').strip()
        basicInfo['labels'] = []
        basicInfo['depends'] = []
        basicInfo['versions'] = []
        basicInfo['other_urls'] = []

        licenseTexts = response.xpath('/html/body/div[1]/div[2]/div[1]/div[2]/div/div[2]/text()').extract()
        descs = response.xpath('/html/body/div[1]/div[2]/div[3]/div[1]/p/text()').extract()
        homepages = response.xpath('/html/body/div[1]/div[2]/div[1]/div[2]/div/div[3]/a/@href').extract()
        downloads = response.xpath('/html/body/div[1]/div[2]/div[1]/div[2]/div/div[4]/text()').extract()
        if len(downloads) > 0:
            basicInfo['total_downloads'] = int(downloads[0].replace(',','').strip())


        if len(homepages) > 0:
            basicInfo['homepage'] = homepages[0].strip()
        if len(descs) > 0:
            basicInfo['project_desc'] = descs[0].strip()
        if len(licenseTexts) > 0:
            basicInfo['official_license'] = licenseTexts[0].strip()

        labels = response.xpath('//div[@class="label_row"]/a/text()').extract()
        lableList = []
        for ll in labels:
            lableList.append(ll.strip())
        basicInfo['labels'] = lableList

        depends = response.xpath('//div[@class="dependency_row"]')
        dependsList = []
        for dep in depends:
            textss = dep.xpath('./text()').extract()
            range = dep.xpath('./span/text()').extract()
            if len(textss) == len(range) and len(textss) == 1:
                dd = {}
                dd['name'] = textss[0]
                dd['version_range'] = range[0].strip()
                dependsList.append(dd)
        basicInfo['depends'] = dependsList

        vvs = response.xpath('//div[@class="version_row"]')
        vlist = []
        for vv in vvs:
            names = vv.xpath('./a/text()').extract()
            forSpanLength = len(vv.xpath('./span').extract())
            if forSpanLength == 2:
                days_ago = vv.xpath('./span[1]/text()').extract()
                downloads_num = vv.xpath('./span[2]/text()').extract()
            else:
                days_ago = vv.xpath('./span[2]/text()').extract()
                downloads_num = vv.xpath('./span[3]/text()').extract()
            if len(names) == len(days_ago) and len(downloads_num) == len(days_ago) and len(days_ago) == 1:
                ddcs = {}

                ddcs['name'] = names[0].strip()
                print downloads_num[0].strip()
                ddcs['downloads'] = int(downloads_num[0].replace(',','').replace('downloads','').replace('download','').strip())
                ddcs['time_ago'] = days_ago[0].replace(',', '').strip()

                ddcs['rockspec_url'] = response.url.replace('modules','manifest')+'/'+ddcs['name']+'-'+'.rockspec'
                vlist.append(ddcs)


        if len(basicInfo['homepage']) > 0:
            basicInfo['other_urls'] = [basicInfo['homepage'].strip()]
        basicInfo['versions'] = vlist



        item = LuaItem()
        item['data'] = basicInfo
        yield item


















