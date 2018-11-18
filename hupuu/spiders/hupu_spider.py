# -*- coding: utf-8 -*-
import datetime
import functools
from functools import reduce

import pymongo
import scrapy
import re

from hupuu import settings
from hupuu.items import *


class HupuSpiderSpider(scrapy.Spider):
    name = 'hupu_spider'
    allowed_domains = ['hupu.com']
  
    start_urls = ['https://bbs.hupu.com/lol','https://bbs.hupu.com/kog','https://bbs.hupu.com/hs',
    'https://bbs.hupu.com/pubg','https://bbs.hupu.com/game','https://bbs.hupu.com/ow','https://bbs.hupu.com/dota2']
   

    depth=2
    qianzhui='https://bbs.hupu.com'
    processed=set()
    userqianzhui='https://my.hupu.com/'

    def __init__(self):
        super()
        client=pymongo.MongoClient()
        cursor=client.hupu.user.find({},{"userid":1})
        #再mongodb 上依旧做了 index 处理，不会有重复的user，但为了效率，这还是先把user加入
        for i in cursor:
            id=i["userid"]
            self.processed.add(id)

        
    def parse(self, response):
        #所有帖子
        #print("head ------------------------------------------")
        #print(response.url)
        item=HupuuItem()
        lis=response.xpath('//ul[@class="for-list"]/li') #type:scrapy.selector.unified.Selector
        kk=0
        for i in lis:
            print("下一个帖子"+str(kk))
            kk+=1
            url=i.xpath('div/a[@class="truetit"]/@href').extract_first()
            ids=i.xpath('div/a[@class="aulink"]/@href').re(r'(?<=/)\d+(?=$)')
            if(len(ids)==0):
                continue
            userid=int(ids[0])
            #yield scrapy.Request(self.qianzhui+url,callback=self.parse_content)
            #  在本 实验中 不处理帖子回复了
            if(userid not in  self.processed):#一切都要再当前id没有处理的情况下进行
                self.processed.add(userid)
                item["title"]=i.xpath('div/a[@class="truetit"]/text()').extract_first()
            
                url=i.xpath('div/a[@class="truetit"]/@href').extract_first()
                item['url']=url 

                username=i.xpath('div/a[@class="aulink"]/text()').extract_first()
                item["username"]=username
                req= scrapy.Request(self.userqianzhui+'/'+str(userid),callback=functools.partial(self.parse_user,deep=0))  #一个小技巧，在回调函数前设置参数
                req.meta['userid'] = userid
                req.meta['username'] = username               
                yield req 
                #处理帖子
                item["userid"]=userid
                strtime=i.xpath('div/a[@style="color:#808080;cursor: initial; "]/text()').extract_first()
                dtime=datetime.datetime.strptime(strtime,"%Y-%m-%d")
                item["time"]=dtime
                str_= i.xpath('span[@class="ansour box"]/text()').extract_first().split('\xa0/\xa0') #95/113395 as  '95\xa0/\xa0113395'
                item["huifu"]=int(str_[0])
                item["liulan"]=int(str_[1])
                yield item
            
        #处理翻页逻辑
        url_num=response.url.split('-')
 
        if(len(url_num)==1):
            yield scrapy.Request(url_num[0]+'-2')
        else:
            yield scrapy.Request(url_num[0] +'-'+str(int(url_num[1])+1))
           
    def parse_content(self, response):
        item=HuitieItem()
        #print("content-----------------------------------------")
        #print(response.url)
        lis=response.xpath('//div[@class="floor_box"]')
        for i in lis:
            ids=i.xpath('.//a[@class="u"]/@href').re(r'(?<=/)\d+(?=$)')
            if(len(ids)==0):
                continue
            item['userid']=int(ids[0])
            time_dianzan=i.xpath('.//span[@class="stime"]/text()').extract()
            item['datetime']=datetime.datetime.strptime(time_dianzan[0],'%Y-%m-%d %H:%M')
            item['dianzanshu']=time_dianzan[1] if(len(time_dianzan)>1) else None
            contents=i.xpath('.//table[@class="case"]//td/text()').extract()
            item['content']=reduce(lambda x,y:x+y,contents)
            item['username']=i.xpath('.//a[@class="u"]/text()').extract_first()
            
            item['source']=i.xpath('.//a[@style="color:#999"]/text()').extract_first()
            
            yield item
        #处理完了翻页
        url_num=response.url.split('-')
        if(len(url_num)==1):
            
            yield scrapy.Request(response.url[0:-5]+'-2'+response.url[-5:],callback=self.parse_content)
        else:
            yield scrapy.Request(url_num[0] +'-'+str(int(url_num[1][0])+1)+url_num[1][1:],callback=self.parse_content)

    def visits(self,lis,name_,id_,deep):
        liss=lis.xpath('.//a[@class="u"]')

    
        for temp in liss:           
            ids=temp.xpath("./@href").re(r'(?<=/)\d+(?=$)')


            if(len(ids)!=0 and ids[0] not in self.processed):
                id=ids[0]
                self.processed.add(id)
                item=EdgeItem()
                #关注和访问刚好是反过来得
                name=temp.xpath('./text()').extract_first()
                item['from_']=name
                item['from_id']=int(id)
                item['to_']=name_
                item['to_id']=id_
                item["leixing"]="visit"
                yield item
                if(deep!=self.depth):
                    req= scrapy.Request(self.userqianzhui+'/'+id,callback= functools.partial(self.parse_user,deep=deep+1))  #一个小技巧，在回调函数前设置参数
                    req.meta['userid'] = int(id)
                    req.meta['username'] = name          
                    yield req     
            

    def parse_user(self,response,deep):
        #牺牲一下效率，拿到response 之后再 判断。。
        #实在不想重构代码了，┭┮﹏┭┮
        if(deep==self.depth):
            return

        item=UserItem() 
        username=response.meta['username']
        item["username"]=username
        userid= response.meta['userid']
        item["userid"]=int(userid)
        item['sex']= response.xpath('//span[ @itemprop="gender"]/text()').extract_first()
        yield item 
         #处理完当前了，继续处理粉丝和访客
        # follow=response.xpath('//div[@id="following"]')
        visit=response.xpath('//div[@id="visitor"]')
        # for i in self.myfunc(follow,username,userid,'follow'):
        #     yield i
        #处理访问他的人
        for i in self.visits(visit,username,userid,deep):
            yield i  
        #处理关注的人
      
        req=scrapy.Request(response.url+"/following",callback=functools.partial(self.parse_follow,dir=True,deep=deep))  #另一个小技巧，用偏函数来做
        req.meta['userid'] = userid
        req.meta['username'] = username          
        yield req
        req=scrapy.Request(response.url+"/follower",callback=functools.partial(self.parse_follow,dir=False,deep=deep)) 
        req.meta['userid'] = userid
        req.meta['username'] = username          
        yield req
    def parse_follow(self,response,dir,deep):
        #如果dir为true，说明当前关注他人  ，反之 被关注
        temp=response.xpath('//div[@class="search_user_list index_bbs"]/ul')
        username=response.meta["username"]
        userid=response.meta["userid"]
      
        lis=temp.xpath('./li')
        for user in lis:
            ids=user.xpath('.//a[@class="u"]/@href').re(r'(?<=/)\d+(?=$)')
            if(len(ids)==0):#有些人的id不是数字
                continue
            id=int(ids[0])
            if(id not in self.processed):# 先看处理过没有
              
                self.processed.add(id)
                item=EdgeItem()
                name=user.xpath('.//a[@class="u"]/text()').extract_first()
               
                if(dir):
                    item["from_id"]=userid
                    item["from_"]=username
                    item["to_id"]=id
                    item["to_"]=name
                else:
                    item["from_id"]=id
                    item["from_"]=name
                    item["to_id"]=userid
                    item["to_"]=username
                item["leixing"]="follow"
                
                yield item
                if(deep!=self.depth):
                    req= scrapy.Request(self.userqianzhui+'/'+str(id),callback=functools.partial(self.parse_user,deep=deep+1))
                    req.meta['userid'] =id  
                    req.meta['username'] = name              
                    yield  req
