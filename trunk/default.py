
import xbmcplugin
import xbmcgui
import xbmcaddon
import os, sys, re
import urllib, urllib2


# Shared resources
addonPath = ''
try:
	import xbmcaddon
	addon = xbmcaddon.Addon(id='plugin.video.s04tv')
	addonPath = addon.getAddonInfo('path')
except:
	addonPath = os.getcwd()
		
BASE_RESOURCE_PATH = os.path.join(addonPath, "resources" )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib" ) )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib", "BeautifulSoup" ) )
sys.path.append( os.path.join( BASE_RESOURCE_PATH, "lib", "mechanize" ) )

from BeautifulSoup import BeautifulSoup
import mechanize

thisPlugin = int(sys.argv[1])

PLUGINNAME = 'S04tv'
PLUGINID = 'plugin.video.s04tv'
BASE_URL = 'https://www.s04tv.de/'
	
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
	
		#url = sys.argv[0] + '?' + urllib.urlencode(parameters)
		url = BASE_URL + linkValue
		
		addDir(itemTitle, url, 2, imageUrlValue)
		
		#listItem = xbmcgui.ListItem(itemTitle, iconImage=imageUrlValue)
		#xbmcplugin.addDirectoryItem(thisPlugin, listitem=listItem, url='', isFolder=True)


def buildVideoLinks(doc, name):
	xbmc.log('buildVideoLinks')

	#parse complete document
	soup = BeautifulSoup(''.join(doc))
	videoTag = soup.find('video')	
	videoUrl = videoTag['src']
	
	print 'start playing video: ' +videoUrl
	addLink(name, videoUrl, '')


def addDir(name,url,mode,iconimage):
    u=sys.argv[0]+"?url="+url+"&mode="+str(mode)+"&name="+name
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
    return ok
   

def addLink(name,url,iconimage):
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
    return ok


def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
            params=sys.argv[2]
            cleanedparams=params.replace('?','')
            if (params[len(params)-1]=='/'):
                    params=params[0:len(params)-2]
            pairsofparams=cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                    splitparams={}
                    splitparams=pairsofparams[i].split('=')
                    if (len(splitparams))==2:
                            param[splitparams[0]]=splitparams[1]
                            
    return param


def login(cookieFile):
	
	cj = mechanize.LWPCookieJar()
	
	try:
		xbmc.log('load cookie file')
		#ignore_discard=True loads session cookies too
		cj.load(cookieFile, ignore_discard=True)
		browser.set_cookiejar(cj)
		
		xbmc.log('cookies loaded, checking if they are still valid...')
		browser.open("https://www.s04tv.de")
		doc = browser.response().read()
		
		loginStatus = checkLogin(doc)
		if(loginStatus == 0):
			return True
	#if cookie file does not exist we just keep going...
	except IOError:
		xbmc.log('Error loading cookie file. Trying to log in again.')
		pass
	
	xbmc.log('Logging in')
	username = settings.getSetting('username')
	xbmc.log('username: ' +username) 
	password = settings.getSetting('password')
		
	browser.open("https://www.s04tv.de")
	#HACK: find out how to address form by name
	browser.select_form(nr=0)
	browser.form['username'] = username
	browser.form['password'] = password
	browser.submit()
	
	cj.save(cookieFile, ignore_discard=True)
	
	doc = browser.response().read()
	loginStatus = checkLogin(doc)			
	return loginStatus == 0
	

def checkLogin(doc):
	
	matchLoginSuccessful = re.search('Sie sind angemeldet als', doc, re.IGNORECASE)
	if(matchLoginSuccessful):
		xbmc.log('login successful')
		return 0
	
	matchLoginFailed = re.search('Anmeldung fehlgeschlagen', doc, re.IGNORECASE)
	if(matchLoginFailed):
		 xbmcgui.Dialog().ok(PLUGINNAME, 'Login failed for user "%s". Please validate your credentials.' %username)
		 return 1
	else:
		xbmc.log('You are not logged in')
		#Guess we are logged in
		return 2


def runPlugin(doc):
	
	print 'runPlugin' 
	
	if mode==None or doc==None or len(doc)<1:
		print "mode 0"
		buildVideoList(doc)
       
	elif mode==1:
		print "mode 1"
		buildVideoList(doc)
	        
	elif mode==2:
		print "mode 2"	
		buildVideoLinks(doc,name)
	
	xbmcplugin.endOfDirectory(thisPlugin)


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

settings = xbmcaddon.Addon(id='%s' %PLUGINID)

if(url == None):
	url = BASE_URL
	
success = login('C:\\Users\\malte\\AppData\\Roaming\\XBMC\\addons\\plugin.video.s04tv\\cookies.txt')

if(success):
	browser.open(url)
	doc = browser.response().read()
	runPlugin(doc)


