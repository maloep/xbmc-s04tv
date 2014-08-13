
# -*- coding: iso-8859-15 -*-

import os, sys, re, json
import urllib, urllib2
from urlparse import *
import xml.etree.ElementTree as ET

BASE_RESOURCE_PATH = "C:\\Users\\lom\\AppData\\Roaming\\XBMC\\addons\\plugin.video.s04tv.dev\\resources"
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib", "BeautifulSoup" ) )

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import Tag
  

BASE_URL = 'http://www.s04.tv'


def buildHomeDir(url, doc):
    
    soup = BeautifulSoup(''.join(doc))
    
    nav = soup.find('nav')
    
    for navitem in nav.contents:
        #first tag is our ul
        if(type(navitem) == Tag):
            for ulitem in navitem.contents:
                if(type(ulitem) == Tag):
                    if(ulitem.name == 'li'):
                        a = ulitem.find('a')
                        print a.text
                        print a['href']
            break
        
        
def buildSubDir(url, doc):
    
    soup = BeautifulSoup(''.join(doc))
    
    nav = soup.find('ul', attrs={'class': 'contentnav'})
    div =  nav.find('div')
    ul = div.find('ul')
    for ulitem in ul.contents:
        if(type(ulitem) == Tag):
            if(ulitem.name == 'li'):
                a = ulitem.find('a')
                print a.text
                print a['href']
                

def buildSubSubDir(url, doc):
    print 'buildSubSubDir'
    print 'url = ' +url
    soup = BeautifulSoup(''.join(doc))
    
    #get pagenumber
    indexpage = url.find('page/')
    indexpage = indexpage + len('page/')
    indexminus = url.find('-', indexpage) 
    pagenumber = url[indexpage:indexminus]
    
    #check if we have corresponding sub menus
    li = soup.find('li', attrs={'class':'dm_%s'%pagenumber})
    if(li == None):
        buildVideoLinks(url, doc)
        return
    
    div =  li.find('div')
    ul = div.find('ul')
    for ulitem in ul.contents:
        if(type(ulitem) == Tag):
            if(ulitem.name == 'li'):
                a = ulitem.find('a')
                print a.text
                print a['href']
        


def buildVideoDir(url, doc):
    
    hideexclusive = False
    hideflag = False
    hidedate = False
    
    soup = BeautifulSoup(''.join(doc))
    articles = soup.findAll('article')
    if(not articles):
        return
    
    for article in articles:
                
        div = article.find('div')
        if(not div):
            continue
        
        flag = div['class']
        
        #for some reason findNextSibling does not work here
        p = div.findAllNext('p', limit=1)
        if(not p):
            date = ''
        else:
            date = p[0].text
                
        img = div.findAllNext('img', limit=1)
        if(not img):
            continue
        imageUrl = img[0]['src']
        
        #HACK: this is only required on home page
        h2 = img[0].findAllNext('h2', limit=1)
        if(h2):
            a = h2[0].findAllNext('a', limit=1)
            if(not a):
                continue
            url = a[0]['href']
            span = a[0].find('span')
        else:
            a = img[0].findAllNext('a', limit=1)
            if(not a):
                continue
            url = a[0]['href']
            span = a[0].find('span')
        
        if(not span):
            continue
        
        title = ''
        for text in span.contents:
            if(type(text) != Tag):
                if(title != ''):
                    title = title +': '
                title = title +text
                
        #only required for homescreen
        span2 = span.nextSibling
        if(span2):
            title = title +': ' +span2.text
                
        if(not hidedate):
            title = title + ' (%s)'%date
                
        extraInfo = {}
        if(flag == 'flag_free'):
            if(not hideflag):
                title = '[FREE] ' +title
            extraInfo['IsFreeContent'] = 'True'
        elif(flag == 'flag_excl'):
            if(hideexclusive):
                #don't add exclusive videos to list
                continue
            if(not hideflag):
                title = '[EXCL] ' +title
            extraInfo['IsFreeContent'] = 'False'
                
        
        url = BASE_URL + url
        print title
        print url
        print imageUrl
        print date
        print flag        
        
        #addDir(title, url, 4, imageUrl, date, extraInfo)

        
def getVideoUrl(url):
    print 'getVideoUrl'
    
    doc = getUrl(url)
    soup = BeautifulSoup(''.join(doc))
    
    p = soup.find('p', attrs={'class': 'breadcrumbs'})
    a = p.find('a')
    title = a['title']
    if(title == ''):
        title = 'Play video'
    
    div = soup.find('div', attrs={'class': 'videobox'})
    script = div.find('script', attrs={'type': 'text/javascript'})
    
    scripttext = script.next
    indexbegin = scripttext.find("videoid: '")
    indexbegin = indexbegin + len("videoid: '")
    indexend = scripttext.find("'", indexbegin)
    xmlurl = scripttext[indexbegin:indexend]
    
    #load xml file
    xmlstring = getUrl(BASE_URL +xmlurl)
    root = ET.fromstring(xmlstring)
    
    urlElement = root.find('invoke/url')
    
    xmlstring = getUrl(urlElement.text)
    root = ET.fromstring(xmlstring)
    metas = root.findall('head/meta')
    vid_base_url = ''
    for meta in metas:
        if( meta.attrib.get('name') == 'httpBase'):
            vid_base_url = meta.attrib.get('content')
            break
    
    quality = 'low400'
    quality = '_%s.mp4'%quality
    videos = root.findall('body/switch/video')
    print 'quality: ' +quality 
    
    for video in videos:
        src = video.attrib.get('src')
        print 'src: ' +src
        if(src.find(quality) > 0):
            break
        
    print 'found video = ' +src
            

def login():
    
    username = 'bla'
    password = 'bla'
    print 'Logging in with username "%s"' %username
    
    loginparams = {'username_field' : username.encode('utf-8'), 'password_field' : password.encode('utf-8')}
    loginurl = 'https://ssl.s04.tv/get_content.php?lang=TV&form=login&%s' %urllib.urlencode(loginparams)    
    print loginurl
    loginresponse = getUrl(loginurl)
    print 'login response: ' +loginresponse
    
    #loginresponse should look like this: ({"StatusCode":"1","stat":"OK","UserData":{"SessionID":"...","Firstname":"...","Lastname":"...","Username":"lom","hasAbo":1,"AboExpiry":"31.07.14"},"out":"<form>...</form>"});
    #remove (); from response
    jsonstring = loginresponse[1:len(loginresponse) -2]
    jsonResult = json.loads(jsonstring)
    if(jsonResult['stat'] == "OK"):
        userdata = jsonResult['UserData']
        if(userdata['hasAbo'] == 1):
            print 'login successful'
            return True
        else:
            print 'login failed'
            return False
    else:
        print 'login failed'
        return False


def getUrl(url):
        url = url.replace('&amp;','&')
        print 'Get url: '+url
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link




#login()

"""
url = BASE_URL
doc = getUrl(url)
buildHomeDir(url, doc)
"""

"""
url = "http://www.s04.tv/de/saison/page/4--4--.html"
doc = getUrl(url)
buildSubDir(url, doc)
"""

"""
url = "http://www.s04.tv/de/saison/stimmen-zum-spiel/page/53--4--.html"
doc = getUrl(url)
buildSubSubDir(url, doc)
"""

"""
#url = "http://www.s04.tv/de/saison/highlights/saison-2013/14/testspiele/page/332--4--.html"
url = "http://www.s04.tv"
doc = getUrl(url)
buildVideoDir(url, doc)
"""

"""
url = "http://www.s04.tv/de/saison/highlights/saison-2011/12/dfb-pokal/mp4migration/110531_pokallights1_neu/page/116---262-.html"
#url = "http://www.s04.tv/de/saison/highlights/saison-2013/14/testspiele/mp4/130729_lokleipzig_schalke_s04tv/page/335---323-.html"
doc = getUrl(url)
getVideoUrl(url)
"""

import re
line = 'changeVideoPage(1, 181)'
match_res=re.compile('changeVideoPage\(0,(.+)\)', re.DOTALL).findall(line)
res = (int)(match_res[0])
print('res = ' +str(res))