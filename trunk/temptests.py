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

from BeautifulSoup import *


import mechanize
br = mechanize.Browser()
br.open("https://www.s04tv.de")
br.select_form(nr=0)
br.form['username'] = 'test'
br.form['password'] = 'test'
br.submit()
#print br.response().read()


url = 'https://www.s04tv.de/index.php/videos/items/lh_hjk.html'
br.open(url)
print br.response().read()

"""
URL = 'https://www.s04tv.de'


response = urllib2.urlopen(URL)
doc = response.read()
response.close()

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
	print titlePart1Value.string
	
	try:
		titlePart2 = content.find('div', attrs={'class' : 'field untertitel'})
		titlePart2Value = titlePart2.find('div', attrs={'class' : 'value'})
		print titlePart2Value.string
	except:
		pass	
	
	imageTag = content.find('div', attrs={'class' : 'field Bild'})
	link = imageTag.find('a')
	print link['href']
	imageUrl = imageTag.find('img')	
	print imageUrl['src']
		
"""





