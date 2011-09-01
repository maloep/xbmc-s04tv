
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


def buildVideoList(url):
	
	browser.open(url)
	doc = browser.response().read()	

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


def buildVideoLinks(url, name):
	
	browser.open(url)
	doc = browser.response().read()

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


def login():
		
	xbmc.log('begin login')
	username = settings.getSetting('username')
	xbmc.log('username: ' +username) 
	password = settings.getSetting('password')
		
	cookies = mechanize.CookieJar()
	opener = mechanize.build_opener(mechanize.HTTPCookieProcessor(cookies))
		
	browser.open("https://www.s04tv.de")
	#HACK: find out how to address form by name
	browser.select_form(nr=0)
	browser.form['username'] = username
	browser.form['password'] = password
	browser.submit()
	
	doc = browser.response().read()
	
	matchLoginSuccessful = re.search('Sie sind angemeldet als', doc, re.IGNORECASE)
	if(matchLoginSuccessful):
		xbmc.log('login successful')
		return True
	
	matchLoginFailed = re.search('Anmeldung fehlgeschlagen', doc, re.IGNORECASE)
	if(matchLoginFailed):
		 xbmcgui.Dialog().ok(PLUGINNAME, 'Login failed for user "%s". Please validate your credentials.' %username)
		 return False
	else:		
		xbmc.log('Login status could not be determined. Maybe the code of the site has changed.')
		#Guess we are logged in
		return True


def runPlugin():
	
	print 'runPlugin' 
	
	if mode==None or url==None or len(url)<1:
		print "mode 0"
		buildVideoList(BASE_URL)
       
	elif mode==1:
		print "mode 1"
		buildVideoList(url)
	        
	elif mode==2:
		print "mode 2"	
		buildVideoLinks(url,name)
	
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

loggedIn = login()
if(loggedIn):
	runPlugin()



