import os, sys
import urllib, urllib2, cookielib

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

from BeautifulSoup import *
import mechanize

browser = mechanize.Browser()

url = 'https://www.s04tv.de/index.php/s04tv-kostenlos.html'
browser.open(url)

doc = browser.response().read()
soup = BeautifulSoup(''.join(doc))

imageTag = soup.find('div', attrs={'class' : 'field Bild'})
link = imageTag.find('a')
linkValue = link['href']

newUrl = 'https://www.s04tv.de/' +linkValue
browser.open(newUrl)

doc = browser.response().read()
soup = BeautifulSoup(''.join(doc))

videoTag = soup.find('video')
if(videoTag):
	videoUrl = videoTag['src']
	
print videoUrl




