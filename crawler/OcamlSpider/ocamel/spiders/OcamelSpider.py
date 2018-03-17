# -*- coding:utf-8 -*-
import requests,time,random

import scrapy

import json
import urllib


from ocamel.items import OcamelItem
from ocamel.items import OcamlVersionItem




class OcamelSpider(scrapy.Spider):
    name = 'OcamelSpider'
    # custom_settings = {'DOWNLOAD_DELAY': 1, 'DOWNLOAD_TIMEOUT':30000}
    # start_urls = ['http://go-search.org/search']
    # host_prefix = "http://go-search.org"

    def __init__(self, **kwargs):
        self.start_urls = ['http://opam.ocaml.org/packages/']
        self.package_prefix = 'http://opam.ocaml.org/packages/'

        super(OcamelSpider, self).__init__(self, **kwargs)



    def __str__(self):
        return "OcamelSpider"

    def start_requests(self):
        for unit in self.start_urls:
            print unit
            yield scrapy.Request(url = unit, callback = self.parseAllLinks)



    # parse all the ocaml package's urls
    def parseAllLinks(self, response):
        trs = response.xpath("//table[@id='packages']/tbody/tr")
        prefix = 'http://opam.ocaml.org/packages/'
        print len(trs), ' len'
        for tr in trs:
            packageNames = tr.xpath('./td[1]/a/text()').extract()
            latestVersions = tr.xpath('./td[2]/text()').extract()
            descs = tr.xpath('./td[3]/text()').extract()
            if len(packageNames) == len(latestVersions) and len(packageNames) == len(descs) and len(packageNames) == 1:
                nts = prefix + packageNames[0].strip()
                yield  scrapy.Request(url = nts,callback = self.parseFirstDetails, meta = {'name':packageNames[0].strip(),'desc':descs[0].strip(), 'latest_v':latestVersions[0].strip()})

    # parse the ocaml package detail page
    def parseFirstDetails(self, response):
        nextLinkMap = {}  #store other versions' url (version name is the key, url for the value)
        tts = {}
        vinfo = {}
        projectUrl = response.url
        tts['project_url'] =  projectUrl
        tts['project_name'] = response.meta['name']
        tts['project_desc'] = response.meta['desc']
        tts['latest_version'] = response.meta['latest_v']
        tts['authors'] = ''
        tts['official_license'] = ''
        tts['homepage'] = ''
        tts['issue_tracker'] = ''
        tts['maintainer'] = ''
        tts['versions'] = []
        tts['other_urls'] = []

        trs = response.xpath('//table[@class="table"]/tbody/tr')
        vname = ''




        ntlinks = response.xpath('//ul[@class="nav nav-pills"]/li/a')
        for ntlink in ntlinks:
            linkUrls= ntlink.xpath('./@href').extract()
            linkNames = ntlink.xpath('./text()').extract()
            if len(linkUrls) == len(linkNames) and len(linkUrls) == 1:
                linkUrl = linkUrls[0].strip().replace('../','')

                linkName = linkNames[0].strip()
                print 'linkName ', linkName
                if linkUrl != '#':
                    linkUrl = self.package_prefix + linkUrl
                    nextLinkMap[linkName] = linkUrl

                else:
                    vname = linkName.replace('version', '').strip()

        tts['latest_version'] = vname
        vinfo['name'] = vname

        vinfo['available'] = ''
        vinfo['published_date'] = ''
        vinfo['source_url'] = ''
        vinfo['edit_url'] = ''
        vinfo['statistics'] = 0
        vinfo['depends'] = {}
        vinfo['optional_depends'] = {}

        print len(trs), '  ~~~~~~'
        for tr in trs:
            titles = tr.xpath('./th/text()').extract()
            if len(titles) > 0:
                ttsp = titles[0].strip()
                if ttsp == 'Author':
                    contents = tr.xpath('./td/text()').extract()
                    if len(contents) > 0:
                        tts['authors'] = contents[0].strip()
                elif ttsp == 'License':
                    contents = tr.xpath('./td/text()').extract()
                    if len(contents) > 0:
                        tts['official_license'] = contents[0].strip()
                elif ttsp == 'Homepage':
                    contents = tr.xpath('./td/a/text()').extract()
                    if len(contents) > 0:
                        tts['homepage'] = contents[0].strip()
                elif ttsp == 'Issue Tracker':
                    contents = tr.xpath('./td/a/text()').extract()
                    if len(contents) > 0:
                        tts['issue_tracker'] = contents[0].strip()
                        tts['other_urls'] = [contents[0].strip().replace('/issues', '')]
                elif ttsp == 'Maintainer':
                    contents = tr.xpath('./td/text()').extract()
                    if len(contents) > 0:
                        tts['maintainer'] = contents[0].strip()
                elif ttsp == 'Available':
                    contents = tr.xpath('./td/text()').extract()
                    if len(contents) > 0:
                        vinfo['available'] = contents[0].strip()
                elif ttsp == 'Published':
                    contents = tr.xpath('./td/text()').extract()
                    if len(contents) > 0:
                        vinfo['published_date'] = contents[0].strip()
                elif ttsp == 'Source [http]':
                    contents = tr.xpath('./td/a/text()').extract()
                    if len(contents) > 0:
                        vinfo['source_url'] = contents[0].strip()
                elif ttsp == 'Statistics':
                    contents = tr.xpath('./td/strong/text()').extract()
                    if len(contents) > 0:
                        gh = contents[0].strip().replace(',', '')
                        if gh == 'once':
                            vinfo['statistics'] = 1
                        else:
                            vinfo['statistics'] = int(gh)


                elif ttsp == 'Edit':
                    contents = tr.xpath('./td/a/text()').extract()
                    if len(contents) > 0:
                        vinfo['edit_url'] = contents[0].strip()
                elif ttsp == 'Optional dependencies':
                    outTable = tr.xpath('./td/table')
                    dependObj = {}
                    dependsList = []
                    if len(outTable) > 0:
                        cot = 0
                        innerTrs = outTable[0].xpath('./tr/td/table/tr')
                        for itr in innerTrs:
                            if cot == 0:
                                nss = itr.xpath('./th/text()').extract()
                                dependObj['operator'] = ''
                                if len(nss) > 0:
                                    dependObj['operator'] = nss[0].strip()
                            else:
                                artin = itr.xpath('./td[1]/a/text()').extract()
                                rangeN = itr.xpath('./td[2]/text()').extract()
                                artivm = itr.xpath('./td[2]/a/text()').extract()
                                if len(artin) == len(rangeN) and len(artin) == len(artivm) and len(artin) == 1:
                                    newdict = {}
                                    newdict['name'] = artin[0].strip()
                                    newdict['range'] = rangeN[0].strip()
                                    newdict['version'] = artivm[0].strip()
                                    dependsList.append(newdict)

                            cot = cot + 1
                        dependObj['depends_list'] = dependsList

                    vinfo['optional_depends'] = dependObj


                elif ttsp == 'Dependencies':
                    outTable = tr.xpath('./td/table')
                    dependObj = {}
                    dependsList = []
                    if len(outTable) > 0:
                        cot = 0
                        innerTrs = outTable[0].xpath('./tr/td/table/tr')
                        for itr in innerTrs:
                            if cot == 0:
                                nss = itr.xpath('./th/text()').extract()
                                dependObj['operator'] = ''
                                if len(nss) > 0:
                                    dependObj['operator'] = nss[0].strip()
                            else:
                                artin = itr.xpath('./td[1]/a/text()').extract()
                                rangeN = itr.xpath('./td[2]/text()').extract()
                                artivm =itr.xpath('./td[2]/a/text()').extract()
                                if len(artin) == len(rangeN) and len(artin) == len(artivm) and len(artin) == 1:
                                    newdict = {}
                                    newdict['name'] = artin[0].strip()
                                    newdict['range'] = rangeN[0].strip()
                                    newdict['version'] = artivm[0].strip()
                                    dependsList.append(newdict)


                            cot = cot + 1
                        dependObj['depends_list'] = dependsList

                    vinfo['depends'] = dependObj

        tts['versions'] = [vinfo]

        item = OcamelItem()
        item['data'] = tts
        yield item
        print len(nextLinkMap.keys()), ' nextLinkMap'
        for ky in nextLinkMap.keys():
            ky = ky.strip()
            lk = nextLinkMap.get(ky)
            yield scrapy.Request(url = lk, callback = self.parseVersionDetails, meta = {'vname':ky.strip(), "prev_url":tts['project_url']})







    def parseVersionDetails(self, response):
        trs = response.xpath('//table[@class="table"]/tr')
        vinfo = {}


        vinfo['available'] = ''
        vinfo['published_date'] = ''
        vinfo['source_url'] = ''
        vinfo['edit_url'] = ''
        vinfo['statistics'] = 0
        vinfo['depends'] = {}
        vinfo['optional_depends'] = {}
        vinfo['name'] = response.meta['vname']
        vinfo['project_url'] = response.meta['prev_url']




        trs = response.xpath('//table[@class="table"]/tbody/tr')
        for tr in trs:
            titles = tr.xpath('./th/text()').extract()
            if len(titles) > 0:
                ttsp = titles[0].strip()
                if ttsp == 'Available':
                    contents = tr.xpath('./td/text()').extract()
                    if len(contents) > 0:
                        vinfo['available'] = contents[0].strip()
                elif ttsp == 'Published':
                    contents = tr.xpath('./td/text()').extract()
                    if len(contents) > 0:
                        vinfo['published_date'] = contents[0].strip()
                elif ttsp == 'Source [http]':
                    contents = tr.xpath('./td/a/text()').extract()
                    if len(contents) > 0:
                        vinfo['source_url'] = contents[0].strip()
                elif ttsp == 'Statistics':
                    contents = tr.xpath('./td/strong/text()').extract()
                    if len(contents) > 0:
                        gh = contents[0].strip().replace(',','')
                        if gh == 'once':
                            vinfo['statistics'] = 1
                        else:
                            vinfo['statistics'] = int(gh)
                elif ttsp == 'Edit':
                    contents = tr.xpath('./td/a/text()').extract()
                    if len(contents) > 0:
                        vinfo['edit_url'] = contents[0].strip()
                elif ttsp == 'Optional dependencies':
                    outTable = tr.xpath('./td/table')
                    dependObj = {}
                    dependsList = []
                    if len(outTable) > 0:
                        cot = 0
                        innerTrs = outTable[0].xpath('./tr/td/table/tr')
                        for itr in innerTrs:
                            if cot == 0:
                                nss = itr.xpath('./th/text()').extract()
                                dependObj['operator'] = ''
                                if len(nss) > 0:
                                    dependObj['operator'] = nss[0].strip()
                            else:
                                artin = itr.xpath('./td[1]/a/text()').extract()
                                rangeN = itr.xpath('./td[2]/text()').extract()
                                artivm = itr.xpath('./td[2]/a/text()').extract()
                                if len(artin) == len(rangeN) and len(artin) == len(artivm) and len(artin) == 1:
                                    newdict = {}
                                    newdict['name'] = artin[0].strip()
                                    newdict['range'] = rangeN[0].strip()
                                    newdict['version'] = artivm[0].strip()
                                    dependsList.append(newdict)

                            cot = cot + 1
                        dependObj['depends_list'] = dependsList

                    vinfo['optional_depends'] = dependObj


                elif ttsp == 'Dependencies':
                    outTable = tr.xpath('./td/table')
                    dependObj = {}
                    dependsList = []
                    if len(outTable) > 0:
                        cot = 0
                        innerTrs = outTable[0].xpath('./tr/td/table/tr')
                        for itr in innerTrs:
                            if cot == 0:
                                nss = itr.xpath('./th/text()').extract()
                                dependObj['operator'] = ''
                                if len(nss) > 0:
                                    dependObj['operator'] = nss[0].strip()
                            else:
                                artin = itr.xpath('./td[1]/a/text()').extract()
                                rangeN = itr.xpath('./td[2]/text()').extract()
                                artivm =itr.xpath('./td[2]/a/text()').extract()
                                if len(artin) == len(rangeN) and len(artin) == len(artivm) and len(artin) == 1:
                                    newdict = {}
                                    newdict['name'] = artin[0].strip()
                                    newdict['range'] = rangeN[0].strip()
                                    newdict['version'] = artivm[0].strip()
                                    dependsList.append(newdict)


                            cot = cot + 1
                        dependObj['depends_list'] = dependsList

                    vinfo['depends'] = dependObj

        versionDetailItem = OcamlVersionItem()
        versionDetailItem['data'] = vinfo
        yield versionDetailItem









