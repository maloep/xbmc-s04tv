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

url = 'https://www.s04tv.de/?page=2'
browser.open(url)

doc = browser.response().read()
soup = BeautifulSoup(''.join(doc))

previousTag = soup.find('a', attrs={'class' : 'previous'})
print previousTag['href']

nextTag = soup.find('a', attrs={'class' : 'next'})
print nextTag['href']






