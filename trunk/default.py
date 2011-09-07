
import xbmcplugin
import xbmcgui
import xbmcaddon
import os, sys, re
import urllib, urllib2

PLUGINNAME = 'S04tv'
PLUGINID = 'plugin.video.s04tv'
BASE_URL = 'https://www.s04tv.de/'

# Shared resources
addonPath = ''

import xbmcaddon
__addon__ = xbmcaddon.Addon(id='plugin.video.s04tv')
addonPath = __addon__.getAddonInfo('path')
		
BASE_RESOURCE_PATH = os.path.join(addonPath, "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib", "BeautifulSoup" ) )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib", "mechanize" ) )

from BeautifulSoup import BeautifulSoup
import mechanize

__language__ = __addon__.getLocalizedString
thisPlugin = int(sys.argv[1])

browser = mechanize.Browser()


def buildVideoList(doc):
	xbmc.log('buildVideoList')
	
	#parse complete document
	soup = BeautifulSoup(''.join(doc))
	
	container = soup.findAll('div', attrs={'class' : 'layout_full'})
	
	#iterate content
	for content in container[0].contents:
		#ignore NavigableStrings
		if(type(content).__name__ == 'NavigableString'):		
			continue
				
		titlePart1 = content.find('div', attrs={'class' : 'field Headline'})
		titlePart1Value = titlePart1.find('div', attrs={'class' : 'value'})
		itemTitle = titlePart1Value.string
		
		try:
			titlePart2 = content.find('div', attrs={'class' : 'field untertitel'})
			titlePart2Value = titlePart2.find('div', attrs={'class' : 'value'})
			itemTitle = itemTitle +': ' +titlePart2Value.string
		except:
			pass		
		
		imageTag = content.find('div', attrs={'class' : 'field Bild'})
		link = imageTag.find('a')
		linkValue = link['href']
		imageUrl = imageTag.find('img')	
		imageUrlValue = BASE_URL +imageUrl['src']
			
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


def buildVideoLinks(doc, name):
	xbmc.log('buildVideoLinks')

	#parse complete document
	soup = BeautifulSoup(''.join(doc))
	videoTag = soup.find('video')
	
	if(videoTag):
		videoUrl = videoTag['src']
		xbmc.log('start playing video: ' +videoUrl)
		addLink(name, videoUrl, '')
	else:
		xbmc.log('Error while loading video from page. Maybe you are not logged in or site structure has changed.')
		

def provideTestvideo():
	
	url = 'https://www.s04tv.de/index.php/s04tv-kostenlos.html'
	browser.open(url)	
	doc = browser.response().read()
	soup = BeautifulSoup(''.join(doc))
	
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
	browser.open(newUrl)
	
	doc = browser.response().read()
	soup = BeautifulSoup(''.join(doc))
	
	videoTag = soup.find('video')
	if(not videoTag):
		xbmc.log('Error while loading test video. "video" tag not found.')
	videoUrl = videoTag['src']
	
	addLink(__language__(30004), videoUrl, imageUrlValue)


def addDir(name,url,mode,iconimage):
    u = sys.argv[0] +"?url=" +url +"&mode=" +str(mode)+"&name=" +name
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok
   

def addLink(name,url,iconimage):
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={ "Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz)
    return ok


def get_params():
    ''' Convert parameters encoded in a URL to a dict. '''
    parameters = sys.argv[2]
    
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
            #HACK: support urls like ?page=2
            elif (len(paramSplits)) == 3:
                paramDict[paramSplits[0]] = paramSplits[1] +'=' +paramSplits[2] 
    return paramDict


def login(cookieFile):
	
	username = __addon__.getSetting('username')
	xbmc.log('username: ' +username) 
	password = __addon__.getSetting('password')
	
	cj = mechanize.LWPCookieJar()
	
	try:
		xbmc.log('load cookie file')
		#ignore_discard=True loads session cookies too
		cj.load(cookieFile, ignore_discard=True)
		browser.set_cookiejar(cj)
		
		xbmc.log('cookies loaded, checking if they are still valid...')
		browser.open("https://www.s04tv.de")
		doc = browser.response().read()
		
		loginStatus = checkLogin(doc, username)
		if(loginStatus == 0):
			return True
	#if cookie file does not exist we just keep going...
	except IOError:
		xbmc.log('Error loading cookie file. Trying to log in again.')
		pass
	
	xbmc.log('Logging in')	
		
	browser.open("https://www.s04tv.de")
	#HACK: find out how to address form by name
	browser.select_form(nr=0)
	browser.form['username'] = username
	browser.form['password'] = password
	browser.submit()
	
	cj.save(cookieFile, ignore_discard=True)
	
	doc = browser.response().read()
	loginStatus = checkLogin(doc, username)			
	return loginStatus == 0
	

def checkLogin(doc, username):
	
	matchLoginSuccessful = re.search('Sie sind angemeldet als', doc, re.IGNORECASE)
	if(matchLoginSuccessful):
		xbmc.log('login successful')
		return 0
	
	matchLoginFailed = re.search('Anmeldung fehlgeschlagen', doc, re.IGNORECASE)
	if(matchLoginFailed):
		xbmcgui.Dialog().ok(PLUGINNAME, __language__(30100) %username, __language__(30101))
		return 1
	
	matchLoginFailed = re.search('Bitte geben Sie Benutzername und Passwort ein', doc, re.IGNORECASE)
	if(matchLoginFailed):
		xbmcgui.Dialog().ok(PLUGINNAME, __language__(30102), __language__(30103))
		return 1
	
	#not logged in but we don't know the reason
	xbmc.log('You are not logged in.')
	#Guess we are logged in
	return 1
	


def runPlugin(doc):
	
	if mode==None or doc==None or len(doc)<1:
		buildVideoList(doc)
       
	elif mode==1:
		buildVideoList(doc)
	        
	elif mode==2:
		buildVideoLinks(doc,name)


print 'start'

params=get_params()
url=None
name=None
mode=None

try:
	url=params["url"]
except:
	pass
try:
	name=params["name"]
except:
	pass
try:
	mode=int(params["mode"])
except:
	pass

print "Mode: "+str(mode)
print "URL: "+str(url)
print "Name: "+str(name)

if(url == None):
	url = BASE_URL

path = xbmc.translatePath('special://profile/addon_data/%s' %(PLUGINID))
success = login(os.path.join(path, 'cookies.txt'))

if(success):
	browser.open(url)
	doc = browser.response().read()
	runPlugin(doc)
else:
	#provide testvideo
	provideTestvideo()
	
xbmcplugin.endOfDirectory(thisPlugin)
	
	

