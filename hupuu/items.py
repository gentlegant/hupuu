# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class HupuuItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    tablename= 'tiezi'
    title=scrapy.Field()
    username=scrapy.Field()
    userid=scrapy.Field()
    time=scrapy.Field()
    huifu=scrapy.Field()
    liulan=scrapy.Field()
    url=scrapy.Field()

class HuitieItem(scrapy.Item):
    tablename='huitie'
    content=scrapy.Field()
    username=scrapy.Field()
    userid=scrapy.Field()
    datetime=scrapy.Field()
    source=scrapy.Field()
    dianzanshu=scrapy.Field()

class UserItem(scrapy.Item):
    tablename="user"
    username=scrapy.Field()
    userid=scrapy.Field()
    sex=scrapy.Field()
    shengwang=scrapy.Field()
    dengji= scrapy.Field()
    zaixianshijian=scrapy.Field()
    jiarushijian=scrapy.Field()
    fangwencishu=scrapy.Field()
    address=scrapy.Field()

class EdgeItem(scrapy.Item):
    tablename='edge'
    from_=scrapy.Field()
    from_id=scrapy.Field()
    to_=scrapy.Field()
    to_id=scrapy.Field()
    leixing=scrapy.Field()