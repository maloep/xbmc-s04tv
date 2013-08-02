# Copyright (C) 2012 Malte Loepmann (maloep@googlemail.com)
#
# This program is free software; you can redistribute it and/or modify it under the terms 
# of the GNU General Public License as published by the Free Software Foundation; 
# either version 2 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; 
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program; 
# if not, see <http://www.gnu.org/licenses/>.

import xbmc, xbmcplugin, xbmcgui, xbmcaddon
import os, sys, re, json, string
import urllib, urllib2
from urlparse import *
import xml.etree.ElementTree as ET


PLUGINNAME = 'S04tv'
PLUGINID = 'plugin.video.s04tv'
BASE_URL = 'http://www.s04.tv'

# Shared resources
addonPath = ''
__addon__ = xbmcaddon.Addon(id='plugin.video.s04tv')
addonPath = __addon__.getAddonInfo('path')
        
BASE_RESOURCE_PATH = os.path.join(addonPath, "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib", "BeautifulSoup" ) )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib", "mechanize" ) )

from BeautifulSoup import BeautifulSoup
from BeautifulSoup import Tag


__language__ = __addon__.getLocalizedString
thisPlugin = int(sys.argv[1])



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
                        url = BASE_URL + a['href']
                        print 'url = ' +url
                        #HACK: don't add Home menu as all videos are available in other categories
                        if(a.text != 'Home'):
                            addDir(a.text, url, 2, '')
            break
        

def buildSubDir(url, doc):
    print 'url = ' +url
    soup = BeautifulSoup(''.join(doc))
    
    nav = soup.find('ul', attrs={'class': 'contentnav'})
    if(nav):
        div =  nav.find('div')
        if(div):
            ul = div.find('ul')
            for ulitem in ul.contents:
                if(type(ulitem) == Tag):
                    if(ulitem.name == 'li'):
                        a = ulitem.find('a')
                        url = BASE_URL + a['href']
                        print 'url = ' +url
                        addDir(a.text, url, 3, '')
        else:
            buildVideoLinks(url, doc)
    else:
        buildVideoLinks(url, doc)
        
    buildVideoLinks(url, doc)
        
        
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
                url = BASE_URL + a['href']
                print 'url = ' +url
                addDir(a.text, url, 3, '')


def buildVideoLinks(url, doc):
    print 'buildVideoLinks'
    print 'url = ' +url
    
    soup = BeautifulSoup(''.join(doc))
    articles = soup.findAll('article', attrs={'class': 'video_gallery'})
    for article in articles:
        div = article.find('div')
        flag = div['class']
        #for some reason findNextSibling does not work here
        img = div.findAllNext('img', limit=1)
        imageUrl = img[0]['src']
        a = img[0].findAllNext('a', limit=1)
        url = a[0]['href']
        span = a[0].find('span')
        title = ''
        for text in span.contents:
            if(type(text) != Tag):
                if(title != ''):
                    title = title +': '
                title = title +text
        if(flag == 'flag_free'):
            title = '[FREE] ' +title
        elif(flag == 'flag_excl'):
            title = '[EXCL] ' +title
                
        url = getVideoUrl(BASE_URL + url)
        addLink(title, url, imageUrl)


def getVideoUrl(url):
    print 'getVideoUrl'
    
    doc = getUrl(url)
    soup = BeautifulSoup(''.join(doc))
    
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
    
    videos = root.findall('body/switch/video')
    hdvideo = videos[len(videos)-1]
    src = hdvideo.attrib.get('src')
    videourl = vid_base_url +src +'&v=&fp=&r=&g='
    return videourl
    
    
    
    """
    for video in videos:
        src = video.attrib.get('src')
        print vid_base_url +src
    """



"""
def buildVideoList(doc):
    xbmc.log('buildVideoList')
    
    #parse complete document
    soup = BeautifulSoup(''.join(doc))
    
    container = soup.findAll('div', attrs={'class' : 'layout_full'})
    if(not container):
        xbmc.log('Error while building video list. class "layout_full" not found.')
        return
    
    #iterate content
    for content in container[0].contents:
        #ignore NavigableStrings
        if(type(content).__name__ == 'NavigableString'):        
            continue
                        
        itemTitle = findTitle(content, 'div', {'class' : 'field Headline'})        
        if(itemTitle == ''):
            xbmc.log('Error while building video list. class "field Headline" not found.')
            continue
        
        titlePart2 = findTitle(content, 'div', {'class' : 'field untertitel'})        
        if(titlePart2 == ''):
            titlePart2 = findTitle(content, 'div', {'class' : 'field Beitragsart'})
        
        if(titlePart2 != ''):
            itemTitle = itemTitle +': ' +titlePart2
        
        linkValue = ''
        imageUrlValue = ''
        imageTag = content.find('div', attrs={'class' : 'field Bild'})
        if(imageTag):
            link = imageTag.find('a')
            linkValue = link['href']
            imageUrl = imageTag.find('img')    
            imageUrlValue = BASE_URL +imageUrl['src']
        else:
            xbmc.log('Error while building video list. class "field Bild" not found.')
            continue
            
        url = BASE_URL + linkValue
        addDir(itemTitle, url, 2, imageUrlValue)
    
    #previous page
    previousTag = soup.find('a', attrs={'class' : 'previous'})
    if(previousTag):
        pageLink = previousTag['href']
        itemTitle = __language__(30002)
        url = BASE_URL + pageLink
        addDir(itemTitle, url, 1, '')
    
    #next page
    nextTag = soup.find('a', attrs={'class' : 'next'})
    if(nextTag):
        pageLink = nextTag['href']
        itemTitle = __language__(30003)
        url = BASE_URL + pageLink
        addDir(itemTitle, url, 1, '')
"""

"""
def buildVideoLinks(doc, name):
    xbmc.log('buildVideoLinks')

    #parse complete document
    soup = BeautifulSoup(''.join(doc))
    videoTag = soup.find('video')
    
    if(videoTag):
        sourceTag = videoTag.find('source')
        if(sourceTag):
            videoUrl = sourceTag['src']
            xbmc.log('start playing video: ' +videoUrl)
            addLink(name, videoUrl, os.path.join(addonPath, 'icon.png'))
        else:
            xbmc.log('Error while loading video from page. Maybe you are not logged in or site structure has changed.')
    else:
        xbmc.log('Error while loading video from page. Maybe you are not logged in or site structure has changed.')
"""  

"""
def provideTestvideoDir():

    xbmc.log('provideTestvideo')
    
    url = 'https://www.s04tv.de/index.php/s04tv-kostenlos.html'
    browser.open(url)
    doc = browser.response().read()
    soup = BeautifulSoup(''.join(doc))
    
    xbmc.log('site loaded')
    
    imageTag = soup.find('div', attrs={'class' : 'field Bild'})
    if(not imageTag):
        xbmc.log('Error while loading test video. div "field Bild" not found.')
        return
    
    link = imageTag.find('a')
    if(not link):
        xbmc.log('Error while loading test video. "a href" not found.')
    linkValue = link['href']
    imageUrl = imageTag.find('img')    
    imageUrlValue = BASE_URL +imageUrl['src']
    
    newUrl = BASE_URL +linkValue
    
    xbmc.log('new url: ' +newUrl)
    browser.open(newUrl)
    
    doc = browser.response().read()
    soup = BeautifulSoup(''.join(doc))
    
    videoTag = soup.find('video')
    if(not videoTag):
        xbmc.log('Error while loading test video. "video" tag not found.')
        return
    sourceTag = videoTag.find('source')
    if(not sourceTag):
        xbmc.log('Error while loading test video. "video" tag not found.')
        return
    
    videoUrl = sourceTag['src']
    addLink(__language__(30004), videoUrl, imageUrlValue)
"""


def addDir(name,url,mode,iconimage):
    parameters = {'url' : url.encode('utf-8'), 'mode' : str(mode), 'name' : __language__(30005)}
    u = sys.argv[0] +'?' +urllib.urlencode(parameters)
    xbmc.log('addDir url = ' +str(u))
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok
   

def addLink(name,url,iconimage):
    xbmc.log('addLink url = ' +str(url))
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={ "Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz)
    return ok


def login():
    username = __addon__.getSetting('username')
    xbmc.log('username: ' +username) 
    password = __addon__.getSetting('password')
    
    xbmc.log('Logging in with username "%s"' %username)
    loginparams = {'username_field' : username, 'password_field' : password}
    loginurl = 'https://ssl.s04.tv/get_content.php?lang=TV&form=login&%s' %urllib.urlencode(loginparams)
    loginresponse = getUrl(loginurl)
    xbmc.log('login response: ' +loginresponse)
    
    #loginresponse should look like this: ({"StatusCode":"1","stat":"OK","UserData":{"SessionID":"...","Firstname":"...","Lastname":"...","Username":"lom","hasAbo":1,"AboExpiry":"31.07.14"},"out":"<form>...</form>"});
    #remove (); from response
    jsonstring = loginresponse[1:len(loginresponse) -2]
    jsonResult = json.loads(jsonstring)
    if(jsonResult['stat'] == "OK"):
        userdata = jsonResult['UserData']
        if(userdata['hasAbo'] == 1):
            xbmc.log('login successful')
            return True
        else:
            print 'login failed'
            return False
    else:
        xbmc.log('login failed')
        return False
    

def getUrl(url):
        url = url.replace('&amp;','&')
        xbmc.log('Get url: '+url)
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link
    

def num_gen(size=1, chars=string.digits):
        return ''.join(random.choice(chars) for x in range(size))


def runPlugin(url, doc):
    
    if mode==None or doc==None or len(doc)<1:
        buildHomeDir(url, doc)
       
    elif mode==1:
        buildHomeDir(url, doc)
            
    elif mode==2:
        buildSubDir(url, doc)
        
    elif mode==3:
        buildSubSubDir(url, doc)


xbmc.log('S04TV: start addon')

params = parse_qs(urlparse(sys.argv[2]).query)
url=None
name=None
mode=None

try:
    url=params["url"][0]
except:
    pass
try:
    name=params["name"][0]
except:
    pass
try:
    mode=int(params["mode"][0])
except:
    pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if(url == None):
    url = BASE_URL


doc = getUrl(url)
runPlugin(url, doc)
xbmcplugin.endOfDirectory(thisPlugin)
    