# -*- coding: utf-8 -*-

import sys
import os
import re
import xbmc
import xbmcgui
import xbmcplugin
import json
import xbmcvfs
import random
import time
import datetime
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode, quote_plus  # Python 2.X
else:
	from urllib.parse import urlencode, quote_plus  # Python 3.X

from .common import *


iTunesRegion = itunesCountry if itunesForceCountry and itunesCountry else region

if not xbmcvfs.exists(dataPath):
	xbmcvfs.mkdirs(dataPath)

if myTOKEN == 'AIzaSy.................................':
	xbmc.executebuiltin('addon.openSettings({0})'.format(addon_id))

if os.path.isdir(tempCAPA):
	for root, dirs, files in os.walk(tempCAPA):
		for name in files:
			filename = os.path.join(root, name).encode('utf-8').decode('utf-8')
			try:
				if os.path.exists(filename):
					if os.path.getmtime(filename) < time.time() - (60*60*cacheHours): # Check if CACHE-File exists and remove CACHE-File after defined cacheHours
						os.unlink(filename)
			except: pass


def mainMenu():
	addDir(translation(30601), artpic+'deepsearch.gif', {'mode': 'SearchDeezer'})
	addDir(translation(30602), artpic+'beatport.png', {'mode': 'beatportMain', 'url': BASE_URL_BP})
	addDir(translation(30603), artpic+'billboard.png', {'mode': 'billboardMain'})
	addDir(translation(30604), artpic+'ddp-international.png', {'mode': 'ddpMain', 'url': BASE_URL_DDP+'DDP-Charts/'})
	addDir(translation(30605), artpic+'hypem.png', {'mode': 'hypemMain'})
	addDir(translation(30606), artpic+'itunes.png', {'mode': 'itunesMain'})
	addDir(translation(30607), artpic+'official.png', {'mode': 'ocMain'})
	addDir(translation(30608), artpic+'spotify.png', {'mode': 'spotifyMain'})
	if enableADJUSTMENT:
		addDir(translation(30609), artpic+'settings.png', {'mode': 'aConfigs'}, folder=False)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def beatportMain(url):
	content = getCache(url)
	content = content[content.find('<div class="mobile-menu-body">')+1:]
	content = content[:content.find('<!-- End Mobile Touch Menu -->')]
	match = re.compile('<a href="(.*?)" class="genre-drop-list__genre" data-name=.+?">(.*?)</a>', re.S).findall(content)
	addAutoPlayDir(translation(30620), artpic+'beatport.png', {'mode': 'listBeatportVideos', 'url': BASE_URL_BP+'/top-100'})
	for genreURL, genreTITLE in match:
		topUrl = BASE_URL_BP+genreURL+'/top-100'
		title = cleaning(genreTITLE)
		addAutoPlayDir(title, artpic+'beatport.png', {'mode': 'listBeatportVideos', 'url': topUrl})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDGenres+')')

def listBeatportVideos(url, TYPE, LIMIT):
	musicVideos = []
	musicIsolated = set()
	count = 0
	PLT = cleanPlaylist() if TYPE == 'play' else None
	content = getCache(url)
	response = re.compile(r'(?s)window.Playables = (?P<json>{.+?)]};', re.S).findall(content)[0]
	DATA = json.loads(response+']}')
	for item in DATA['tracks']:
		artists = ', '.join([cleaning(artist['name']) for artist in item['artists']])
		song = cleaning(item['name'])
		if item.get('mix', '') and not 'original' in item.get('mix').lower():
			song += ' ['+cleaning(item['mix'])+']'
		plot = 'Artist:  '+artists+'[CR]'+'Song:  '+song
		firstTitle = artists+" - "+song
		try:
			released = time.strptime(item['date']['released'], '%Y-%m-%d')
			newDate = time.strftime('%d.%m.%Y', released)
			plot += '[CR]Date:  [COLOR deepskyblue]'+str(newDate)+'[/COLOR]'
			completeTitle = firstTitle+'   [COLOR deepskyblue]['+str(newDate)+'][/COLOR]'
		except: completeTitle = firstTitle
		try:
			images = list(dict.values(item['images']))
			thumb = images[0]['url']
			thumb = thumb.split('image_size')[0]+'image/'+thumb.split('/')[-1]
		except: thumb = artpic+'noimage.png'
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, completeTitle, thumb, plot])
	if TYPE == 'browse':
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			count += 1
			name = translation(30801).format(str(count), completeTitle)
			addLink(name, thumb, {'mode': 'playTITLE', 'url': fitme(firstTitle)}, plot)
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
	else:
		if int(LIMIT) > 0:
			musicVideos = musicVideos[:int(LIMIT)]
		random.shuffle(musicVideos)
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			endUrl = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playTITLE', 'url': fitme(firstTitle)}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(endUrl, listitem)
		xbmc.Player().play(PLT)

def billboardMain():
	addAutoPlayDir(translation(30630), artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/hot-100/'})
	addAutoPlayDir(translation(30631), artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/billboard-200/'})
	addAutoPlayDir(translation(30632), artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/billboard-global-200/'})
	addDir(translation(30633), artpic+'billboard.png', {'mode': 'listBillboardCharts', 'url': 'genre'})
	addDir(translation(30634), artpic+'billboard.png', {'mode': 'listBillboardCharts', 'url': 'country'})
	addDir(translation(30635), artpic+'billboard.png', {'mode': 'listBillboardCharts', 'url': 'other'})
	addDir(translation(30636), artpic+'billboard.png', {'mode': 'listBillboardCharts', 'url': 'archive'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listBillboardCharts(SELECT):
	if SELECT == 'genre':
		addAutoPlayDir('Alternative', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/alternative-airplay/'})
		addAutoPlayDir('Country', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/country-songs/'})
		addAutoPlayDir('Dance/Club', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/dance-club-play-songs/'})
		addAutoPlayDir('Dance/Electronic', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/dance-electronic-songs/'})
		addAutoPlayDir('Gospel', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/gospel-songs/'})
		addAutoPlayDir('Latin', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/latin-songs/'})
		addAutoPlayDir('Pop', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/pop-songs/'})
		addAutoPlayDir('Rap', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/rap-song/'})
		addAutoPlayDir('R&B', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/r-and-b-songs/'})
		addAutoPlayDir('R&B/Hip-Hop', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/r-b-hip-hop-songs/'})
		addAutoPlayDir('Rhythmic', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/rhythmic-40/'})
		addAutoPlayDir('Rock', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/rock-songs/'})
		addAutoPlayDir('Smooth Jazz', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/jazz-songs/'})
		addAutoPlayDir('Soundtracks', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/soundtracks/'})
		addAutoPlayDir('Tropical', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/latin-tropical-airplay/'})
	elif SELECT == 'country':
		addAutoPlayDir('Argentina Hot-100', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/billboard-argentina-hot-100/'})
		addAutoPlayDir('Canada Hot-100', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/canadian-hot-100/'})
		addAutoPlayDir('Australia - Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/australia-digital-song-sales/'})
		addAutoPlayDir('Canadian - Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/hot-canada-digital-song-sales/'})
		addAutoPlayDir('Euro - Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/euro-digital-song-sales/'})
		addAutoPlayDir('France - Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/france-digital-song-sales/'})
		addAutoPlayDir('Germany - Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/germany-songs/'})
		addAutoPlayDir('Italy - Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/italy-digital-song-sales/'})
		addAutoPlayDir('Spain - Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/spain-digital-song-sales/'})
		addAutoPlayDir('Switzerland - Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/switzerland-digital-song-sales/'})
		addAutoPlayDir('U.K. - Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/uk-digital-song-sales/'})
		addAutoPlayDir('World - Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/world-digital-song-sales/'})
	elif SELECT == 'other':
		addAutoPlayDir('Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/digital-song-sales/'})
		addAutoPlayDir('Streaming Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/streaming-songs/'})
		addAutoPlayDir('Radio Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/radio-songs/'})
		addAutoPlayDir('TOP Songs of the ’90s', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/greatest-billboards-top-songs-90s/'})
		addAutoPlayDir('TOP Songs of the ’80s', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/greatest-billboards-top-songs-80s/'})
		addAutoPlayDir('All Time Hot 100 Singles', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/greatest-hot-100-singles/'})
		addAutoPlayDir('All Time Greatest Alternative Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/greatest-alternative-songs/'})
		addAutoPlayDir('All Time Greatest Country Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/greatest-country-songs/'})
		addAutoPlayDir('All Time Greatest Latin Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/greatest-hot-latin-songs/'})
		addAutoPlayDir('All Time Greatest Pop Songs', artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': BASE_URL_BB+'/charts/greatest-of-all-time-pop-songs/'})
	elif SELECT == 'archive':
		addDir('Hot 100 Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': BASE_URL_BB+'/charts/year-end/hot-100-songs/'}) # bis 2006
		addDir('Global 200 Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': BASE_URL_BB+'/charts/year-end/billboard-global-200/'}) # bis 2021
		addDir('Streaming Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': BASE_URL_BB+'/charts/year-end/streaming-songs/'}) # bis 2013
		addDir('Radio Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': BASE_URL_BB+'/charts/year-end/radio-songs/'}) # bis 2006
		addDir('Digital Song Sales', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': BASE_URL_BB+'/charts/year-end/digital-songs/'}) # bis 2006
		addDir('Country Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': BASE_URL_BB+'/charts/year-end/hot-country-songs/'}) # bis 2002
		addDir('Dance/Electronic Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': BASE_URL_BB+'/charts/year-end/hot-dance-electronic-songs/'}) # bis 2013
		addDir('Gospel Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': BASE_URL_BB+'/charts/year-end/hot-gospel-songs/'}) # bis 2006
		addDir('Latin Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': BASE_URL_BB+'/charts/year-end/hot-latin-songs/'}) # bis 2006
		addDir('Pop Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': BASE_URL_BB+'/charts/year-end/pop-songs/'}) # bis 2008
		addDir('Rap Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': BASE_URL_BB+'/charts/year-end/hot-rap-songs/'}) # bis 2009
		addDir('R&B Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': BASE_URL_BB+'/charts/year-end/hot-r-and-and-b-songs/'}) # bis 2013
		addDir('R&B/Hip-Hop Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': BASE_URL_BB+'/charts/year-end/hot-r-and-and-b-hip-hop-songs/'}) # bis 2002
		addDir('Rhytmic Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': BASE_URL_BB+'/charts/year-end/rhythmic-songs/'}) # bis 2006
		addDir('Rock Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': BASE_URL_BB+'/charts/year-end/hot-rock-songs/'}) # bis 2009
		addDir('Smooth Jazz Songs', artpic+'billboard.png', {'mode': 'listBillboardArchive', 'url': BASE_URL_BB+'/charts/year-end/smooth-jazz-songs/'}) # bis 2006
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDGenres+')')

def listBillboardArchive(url):
	content = getCache(url)
	result = re.findall('All Year-end Charts(.*?)</ul>', content, re.S)[0]
	match = re.compile(r'href="('+BASE_URL_BB+'[^"]+).+?>([^<]+?)</a>', re.S).findall(result)
	for url2, title2 in match:
		addAutoPlayDir(title2.strip(), artpic+'billboard.png', {'mode': 'listBillboardVideos', 'url': url2})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDPlaylists+')')

def listBillboardVideos(url, TYPE, LIMIT):
	musicVideos = []
	startURL = url
	count = 0
	PLT = cleanPlaylist() if TYPE == 'play' else None
	content = getCache(url)
	spl = content.split('class="o-chart-results-list-row-container">')
	for i in range(1,len(spl),1):
		entry = spl[i]
		song = re.compile('id="title-of-a-story" class="c-title.+?>([^<]+?)</', re.S).findall(entry)[0]
		song = re.sub(r'\<.*?>', '', song)
		song = cleaning(song)
		artist = re.compile('id="title-of-a-story" class="c-title.+?<span class="c-label.+?>([^<]+?)</span>', re.S).findall(entry)[0]
		artist = re.sub(r'\<.*?>', '', artist)
		artist = cleaning(artist)
		plot = 'Artist:  '+artist+'[CR]'+'Song:  '+song
		firstTitle = artist+" - "+song
		completeTitle = firstTitle
		if not 'charts/greatest' in startURL and not 'charts/year-end' in startURL:
			results = re.findall('<div class="a-chart-plus-minus-icon">(.+?)<div class="charts-result-detail', entry, re.S)
			for item in results:
				try:
					lastWeek = re.compile('<span class="c-label.+?>([^<]+?)</span>', re.S).findall(item)[0].strip()
					weeksChart = re.compile('<span class="c-label.+?>([^<]+?)</span>', re.S).findall(item)[2].strip()
					plot += '[CR]Rank:  [COLOR deepskyblue]LW = '+str(lastWeek).replace('-', '~')+'|weeksIN = '+str(weeksChart).replace('-', '~')+'[/COLOR]'
					completeTitle = firstTitle+'   [COLOR deepskyblue][LW: '+str(lastWeek).replace('-', '~')+'|weeksIN: '+str(weeksChart).replace('-', '~')+'][/COLOR]'
				except: pass
		try:
			img = re.compile(r'data-lazy-src="(https?://charts-static.billboard.com.+?(?:\.jpg|\.jpeg|\.png))', re.S).findall(entry)[0]
			thumb = re.sub(r'-[0-9]+x[0-9]+', '-480x480', img).strip() # -53x53.jpg || -87x87.jpg || -106x106.jpg || -180x180.jpg || -224x224.jpg || -344x344.jpg
		except: thumb = artpic+'noimage.png'
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, completeTitle, thumb, plot])
	if TYPE == 'browse':
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			count += 1
			name = translation(30801).format(str(count), completeTitle)
			addLink(name, thumb, {'mode': 'playTITLE', 'url': fitme(firstTitle)}, plot)
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
	else:
		if int(LIMIT) > 0:
			musicVideos = musicVideos[:int(LIMIT)]
		random.shuffle(musicVideos)
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			endUrl = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playTITLE', 'url': fitme(firstTitle)}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(endUrl, listitem)
		xbmc.Player().play(PLT)

def ddpMain(url):
	content = getCache(url)
	content = content[content.find('<div class="ddp_subnavigation_top ddp">')+1:]
	content = content[:content.find('<div class="contentbox">')]
	addDir(translation(30640), artpic+'ddp-international.png', {'mode': 'ddpMain', 'url': url})
	addAutoPlayDir(translation(30641), artpic+'ddp-international.png', {'mode': 'listDdpVideos', 'url': BASE_URL_DDP+'DDP-Videochart/'})
	match = re.compile('<li><a href="(.*?)">(.*?)</a></li>', re.S).findall(content)
	for url2, title2 in match:
		url2 = url2.split('/?')[0]
		title2 = cleaning(title2)
		if title2.lower() not in ['archiv', 'ddp', 'highscores']:
			if not 'schlager' in url2.lower():
				if title2.lower() in ['top 100','hot 50', 'neueinsteiger']:
					addAutoPlayDir('..... '+title2, artpic+'ddp-international.png', {'mode': 'listDdpVideos', 'url': url2})
				elif 'jahrescharts' in title2.lower():
					addDir('..... '+title2, artpic+'ddp-international.png', {'mode': 'listDdpYearCharts', 'url': url2})
	addDir(translation(30642), artpic+'ddp-schlager.png', {'mode': 'ddpMain', 'url': url})
	for url2, title2 in match:
		url2 = url2.split('/?')[0]
		title2 = cleaning(title2)
		if title2.lower() not in ['archiv', 'ddp', 'highscores']:
			if 'schlager' in url2.lower():
				if title2.lower() in ['top 100','hot 50', 'neueinsteiger']:
					addAutoPlayDir('..... '+title2, artpic+'ddp-schlager.png', {'mode': 'listDdpVideos', 'url': url2})
				elif 'jahrescharts' in title2.lower():
					addDir('..... '+title2, artpic+'ddp-schlager.png', {'mode': 'listDdpYearCharts', 'url': url2})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDGenres+')')

def listDdpYearCharts(url):
	musicVideos = []
	content = getCache(url)
	content = content[content.find('<div class="contentbox">')+1:]
	content = content[:content.find('</p>')]
	match = re.compile('<a href="(.*?)" alt="(.*?)">', re.S).findall(content)
	for url2, title in match:
		if 'schlager' in url.lower():
			newUrl = BASE_URL_DDP+'DDP-Schlager-Jahrescharts/?'+url2.split('/?')[1]
			thumb = artpic+'ddp-schlager.png'
		elif not 'schlager' in url.lower():
			newUrl = BASE_URL_DDP+'DDP-Jahrescharts/?'+url2.split('/?')[1]
			thumb = artpic+'ddp-international.png'
		musicVideos.append([title, newUrl, thumb])
	musicVideos = sorted(musicVideos, key=lambda d:d[0], reverse=True)
	for title, newUrl, thumb in musicVideos:
		addAutoPlayDir(cleaning(title), thumb, {'mode': 'listDdpVideos', 'url': newUrl})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDPlaylists+')')

def listDdpVideos(url, TYPE, LIMIT):
	musicVideos = []
	musicIsolated = set()
	PLT = cleanPlaylist() if TYPE == 'play' else None
	content = getCache(url)
	content = content[content.find('<div class="eintrag" id="charthead">')+1:]
	content = content[:content.find('<div id="banner_fuss">')]
	spl = content.split('<div class="eintrag">')
	for i in range(1,len(spl),1):
		entry = spl[i]
		rank = re.compile('<div class="platz">(.*?)</div>', re.S).findall(entry)[0]
		artist = re.compile('<div class="interpret">(.*?)</div>', re.S).findall(entry)[0]
		song = re.compile('<div class="titel">(.*?)</div>', re.S).findall(entry)[0]
		if song == "" or artist == "":
			continue
		artist = TitleCase(cleaning(artist))
		song = TitleCase(cleaning(song))
		plot = 'Artist:  '+artist+'[CR]'+'Song:  '+song
		firstTitle = artist+" - "+song
		if firstTitle in musicIsolated:
			continue
		musicIsolated.add(firstTitle)
		try:
			newRE = re.compile('<div class="platz">(.*?)</div>', re.S).findall(entry)[1]
			oneWeek = re.compile('<div class="platz">(.*?)</div>', re.S).findall(entry)[2]
			twoWeek = re.compile('<div class="platz">(.*?)</div>', re.S).findall(entry)[3]
			threeWeek = re.compile('<div class="platz">(.*?)</div>', re.S).findall(entry)[4]
			if newRE in ['NEU', 'RE']:
				plot += '[CR]Rank:  [COLOR deepskyblue]'+str(newRE)+'[/COLOR]'
				completeTitle = firstTitle+'   [COLOR deepskyblue]['+str(newRE)+'][/COLOR]'
			else:
				plot += '[CR]Rank:  [COLOR deepskyblue]LW = '+str(oneWeek).replace('-', '~')+'|2W = '+str(twoWeek).replace('-', '~')+'|3W = '+str(threeWeek).replace('-', '~')+'[/COLOR]'
				completeTitle = firstTitle+'   [COLOR deepskyblue][LW: '+str(oneWeek).replace('-', '~')+'|2W: '+str(twoWeek).replace('-', '~')+'|3W: '+str(threeWeek).replace('-', '~')+'][/COLOR]'
		except: completeTitle = firstTitle
		try:
			thumb = re.findall('style="background.+?//poolposition.mp3(.*?);"',entry,re.S)[0]
			thumb = 'https://poolposition.mp3'+thumb.split('&amp;width')[0]
		except: thumb = artpic+'noimage.png'
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([int(rank), firstTitle, completeTitle, thumb, plot])
	musicVideos = sorted(musicVideos, key=lambda d:d[0], reverse=False)
	if TYPE == 'browse':
		for rank, firstTitle, completeTitle, thumb, plot in musicVideos:
			name = translation(30801).format(str(rank), completeTitle)
			addLink(name, thumb, {'mode': 'playTITLE', 'url': fitme(firstTitle)}, plot)
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
	else:
		if int(LIMIT) > 0:
			musicVideos = musicVideos[:int(LIMIT)]
		random.shuffle(musicVideos)
		for rank, firstTitle, completeTitle, thumb, plot in musicVideos:
			endUrl = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playTITLE', 'url': fitme(firstTitle)}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(endUrl, listitem)
		xbmc.Player().play(PLT)

def hypemMain():
	addAutoPlayDir(translation(30650), artpic+'hypem.png', {'mode': 'listHypemVideos', 'url': BASE_URL_HM+'/popular?ax=1&sortby=shuffle'})
	addAutoPlayDir(translation(30651), artpic+'hypem.png', {'mode': 'listHypemVideos', 'url': BASE_URL_HM+'/popular/lastweek?ax=1&sortby=shuffle'})
	addDir(translation(30652), artpic+'hypem.png', {'mode': 'listHypemMachine'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listHypemMachine():
	for i in range(1, 201, 1):
		dt = datetime.date.today()
		while dt.weekday() != 0:
			dt -= datetime.timedelta(days=1)
		dt -= datetime.timedelta(weeks=i)
		months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
		month = months[int(dt.strftime('%m')) - 1]
		addAutoPlayDir(dt.strftime('%d. %b - %Y').replace('Mar', translation(30653)).replace('May', translation(30654)).replace('Oct', translation(30655)).replace('Dec', translation(30656)), artpic+'hypem.png', {'mode': 'listHypemVideos', 'url': BASE_URL_HM+'/popular/week:'+month+'-'+dt.strftime('%d-%Y')+'?ax=1&sortby=shuffle'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDPlaylists+')')

def listHypemVideos(url, TYPE, LIMIT):
	musicVideos = []
	musicIsolated = set()
	count = 0
	PLT = cleanPlaylist() if TYPE == 'play' else None
	content = getCache(url)
	response = re.compile('id="displayList-data">(.*?)</', re.S).findall(content)[0]
	DATA = json.loads(response)
	for item in DATA['tracks']:
		artist = cleaning(item['artist'])
		song = cleaning(item['song'])
		plot = 'Artist:  '+artist+'[CR]'+'Song:  '+song
		firstTitle = artist+" - "+song
		if firstTitle in musicIsolated or artist == "":
			continue
		musicIsolated.add(firstTitle)
		match = re.compile('href="/track/'+item['id']+'/.+?background:url\\((.+?)\\)', re.S).findall(content)
		thumb = match[0] if match else artpic+'noimage.png' #.replace('_320.jpg)', '_500.jpg')
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, thumb, plot])
	if TYPE == 'browse':
		for firstTitle, thumb, plot in musicVideos:
			count += 1
			name = translation(30801).format(str(count), firstTitle)
			addLink(name, thumb, {'mode': 'playTITLE', 'url': fitme(firstTitle)}, plot)
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
	else:
		if int(LIMIT) > 0:
			musicVideos = musicVideos[:int(LIMIT)]
		random.shuffle(musicVideos)
		for firstTitle, thumb, plot in musicVideos:
			endUrl = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playTITLE', 'url': fitme(firstTitle)}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(endUrl, listitem)
		xbmc.Player().play(PLT)

def itunesMain():
	content = getCache('https://itunes.apple.com/{0}/genre/music/id34'.format(iTunesRegion))
	content = content[content.find('id="genre-nav"'):]
	content = content[:content.find('</div>')]
	match = re.compile('<li><a href="https?://(?:itunes.|music.)apple.com/.+?/genre/.+?/id(.*?)"(.*?)title=".+?">(.*?)</a>', re.S).findall(content)
	addAutoPlayDir(translation(30660), artpic+'itunes.png', {'mode': 'listItunesVideos', 'url': '0'})
	for genreID, genreTYPE, genreTITLE in match:
		title = cleaning(genreTITLE)
		if 'class="top-level-genre"' in genreTYPE:
			if itunesShowSubGenres:
				title = translation(30661).format(title)
			addAutoPlayDir(title, artpic+'itunes.png', {'mode': 'listItunesVideos', 'url': genreID})
		elif itunesShowSubGenres:
			addAutoPlayDir('..... '+title, artpic+'itunes.png', {'mode': 'listItunesVideos', 'url': genreID})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDGenres+')')

def listItunesVideos(genreID, TYPE, LIMIT):
	musicVideos = []
	musicIsolated = set()
	count = 0
	PLT = cleanPlaylist() if TYPE == 'play' else None
	url = 'https://itunes.apple.com/{0}/rss/topsongs/limit=100'.format(iTunesRegion)
	if genreID != '0':
		url += '/genre='+genreID
	url += '/explicit=true/json'
	content = getCache(url)
	response = json.loads(content)
	for item in response['feed']['entry']:
		artist = cleaning(item['im:artist']['label'])
		song = cleaning(item['im:name']['label'])
		plot = 'Artist:  '+artist+'[CR]'+'Song:  '+song
		firstTitle = artist+" - "+song
		if firstTitle in musicIsolated:
			continue
		musicIsolated.add(firstTitle)
		try: thumb = item['im:image'][2]['label'].replace('/170x170bb.png', '/512x512bb.jpg').replace('/170x170bb.jpg', '/512x512bb.jpg')
		except: thumb = artpic+'noimage.png'
		try:
			newDate = item['im:releaseDate']['attributes']['label']
			plot += '[CR]Date:  [COLOR deepskyblue]'+str(newDate)+'[/COLOR]'
			completeTitle = firstTitle+'   [COLOR deepskyblue]['+str(newDate)+'][/COLOR]'
		except: completeTitle = firstTitle
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, completeTitle, thumb, plot])
	if TYPE == 'browse':
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			count += 1
			name = translation(30801).format(str(count), completeTitle)
			addLink(name, thumb, {'mode': 'playTITLE', 'url': fitme(firstTitle)}, plot)
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
	else:
		if int(LIMIT) > 0:
			musicVideos = musicVideos[:int(LIMIT)]
		random.shuffle(musicVideos)
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			endUrl = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playTITLE', 'url': fitme(firstTitle)}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(endUrl, listitem)
		xbmc.Player().play(PLT)

def ocMain():
	addAutoPlayDir(translation(30670), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/singles-chart/'})
	addAutoPlayDir(translation(30671), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/uk-top-40-singles-chart/'})
	addAutoPlayDir(translation(30672), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/singles-chart-update/'})
	addAutoPlayDir(translation(30673), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/singles-downloads-chart/'})
	addAutoPlayDir(translation(30674), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/singles-sales-chart/'})
	addAutoPlayDir(translation(30675), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/audio-streaming-chart/'})
	addAutoPlayDir(translation(30676), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/dance-singles-chart/'})
	addAutoPlayDir(translation(30677), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/classical-singles-chart/'})
	addAutoPlayDir(translation(30678), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/r-and-b-singles-chart/'})
	addAutoPlayDir(translation(30679), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/rock-and-metal-singles-chart/'})
	addAutoPlayDir(translation(30680), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/irish-singles-chart/'})
	addAutoPlayDir(translation(30681), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/scottish-singles-chart/'})
	addAutoPlayDir(translation(30682), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/end-of-year-singles-chart/'})
	addAutoPlayDir(translation(30683), artpic+'official.png', {'mode': 'listOcVideos', 'url': BASE_URL_OC+'/charts/physical-singles-chart/'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDGenres+')')

def listOcVideos(url, TYPE, LIMIT):
	musicVideos = []
	musicIsolated = set()
	count = 0
	PLT = cleanPlaylist() if TYPE == 'play' else None
	content = getCache(url)
	match = re.findall(r'<div class=["\']track["\']>(.*?)<div class=["\']actions["\']>', content, re.S)
	for video in match:
		photo = re.compile(r'<img src=["\'](.*?)["\']', re.S).findall(video)[0]
		if 'amazon.com' in photo or 'coverartarchive.org' in photo:
			thumb = photo.split('img/small?url=')[1].replace('http://ecx.images-amazon.com', 'https://m.media-amazon.com').replace('L._SL75_', 'L')
		elif '/img/small?url=/images/artwork/' in photo:
			thumb = photo.replace('/img/small?url=', '')
		else:
			thumb = artpic+'noimage.png'
		song = re.compile(r'<a href=["\'].+?["\']>(.*?)</a>', re.S).findall(video)[0]
		artist = re.compile(r'<a href=["\'].+?["\']>(.*?)</a>', re.S).findall(video)[1]
		artist = artist.split('/')[0] if '/' in artist else artist
		song = TitleCase(cleaning(song))
		artist = TitleCase(cleaning(artist))
		plot = 'Artist:  '+artist+'[CR]'+'Song:  '+song
		firstTitle = artist+" - "+song
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, thumb, plot])
	if TYPE == 'browse':
		for firstTitle, thumb, plot in musicVideos:
			count += 1
			name = translation(30801).format(str(count), firstTitle)
			addLink(name, thumb, {'mode': 'playTITLE', 'url': fitme(firstTitle)}, plot)
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
	else:
		if int(LIMIT) > 0:
			musicVideos = musicVideos[:int(LIMIT)]
		random.shuffle(musicVideos)
		for firstTitle, thumb, plot in musicVideos:
			endUrl = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playTITLE', 'url': fitme(firstTitle)}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(endUrl, listitem)
		xbmc.Player().play(PLT)

def spotifyMain():
	addDir(translation(30690), artpic+'spotify.png', {'mode': 'listSpotifyCC_Countries', 'url': BASE_URL_SCC+'viral/{}/daily/latest'})
	addDir(translation(30691), artpic+'spotify.png', {'mode': 'listSpotifyCC_Countries', 'url': BASE_URL_SCC+'viral/{}/weekly/latest'})
	addDir(translation(30692), artpic+'spotify.png', {'mode': 'listSpotifyCC_Countries', 'url': BASE_URL_SCC+'regional/{}/daily/latest'})
	addDir(translation(30693), artpic+'spotify.png', {'mode': 'listSpotifyCC_Countries', 'url': BASE_URL_SCC+'regional/{}/weekly/latest'})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listSpotifyCC_Countries(url):
	xbmcplugin.addSortMethod(ADDON_HANDLE, xbmcplugin.SORT_METHOD_LABEL)
	musicIsolated = set()
	UN_Supported = ['andorra', 'bulgaria', 'cyprus', 'hong kong', 'israel', 'japan', 'monaco', 'malta', 'nicaragua', 'singapore', 'thailand', 'taiwan'] # these lists are empty or signs are not readable
	content = getCache(BASE_URL_SCC+'regional')
	content = content[content.find('<div class="responsive-select" data-type="country">')+1:]
	content = content[:content.find('<div class="responsive-select" data-type="recurrence">')]
	match = re.compile('<li data-value="(.*?)" class=.+?>(.*?)</li>', re.S).findall(content)
	for url2, toptitle in match:
		if any(x in toptitle.strip().lower() for x in UN_Supported):
			continue
		if toptitle.strip() in musicIsolated:
			continue
		musicIsolated.add(toptitle)
		addAutoPlayDir(cleaning(toptitle), artpic+'spotify.png', {'mode': 'listSpotifyCC_Videos', 'url': url.format(url2)})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDGenres+')')

def listSpotifyCC_Videos(url, TYPE, LIMIT):
	musicVideos = []
	musicIsolated = set()
	count = 0
	PLT = cleanPlaylist() if TYPE == 'play' else None
	content = getCache(url)
	content = content[content.find('<tbody>')+1:]
	content = content[:content.find('</tbody>')]
	spl = content.split('<tr>')
	for i in range(1,len(spl),1):
		entry = spl[i]
		song = re.compile('<strong>(.*?)</strong>', re.S).findall(entry)[0]
		song = cleaning(song)
		artist = re.compile('<span>(.*?)</span>', re.S).findall(entry)[0]
		artist = cleaning(artist)
		if '(remix)' in song.lower():
			song = song.lower().replace('(remix)', '')
		if ' - ' in song:
			firstSong = song[:song.rfind(' - ')]
			secondSong = song[song.rfind(' - ')+3:]
			song = firstSong+' ['+secondSong+']'
		if artist.lower().startswith('by', 0, 2):
			artist = artist.lower().split('by ')[1]
		if artist.islower():
			artist = TitleCase(artist)
		plot = 'Artist:  '+artist+'[CR]'+'Song:  '+song
		firstTitle = artist+" - "+song
		if firstTitle in musicIsolated or artist == "":
			continue
		musicIsolated.add(firstTitle)
		try:
			thumb = re.compile('<img src="(.*?)">', re.S).findall(entry)[0].replace('ab67616d00004851', 'ab67616d0000b273')
			thumb = 'https://i.scdn.co/image/'+thumb if thumb[:4] != 'http' else thumb
			#thumb = 'https://u.scdn.co/images/pl/default/'+thumb
		except: thumb = artpic+'noimage.png'
		try:
			numbers = re.compile('<td class="chart-table-streams">(.*?)</td>', re.S).findall(entry)[0]
			plot += '[CR]Loads:  [COLOR deepskyblue]'+str(numbers).replace(',', '.')+'[/COLOR]'
			completeTitle = firstTitle+'   [COLOR deepskyblue][DL: '+str(numbers).replace(',', '.')+'][/COLOR]'
		except: completeTitle = firstTitle
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, completeTitle, thumb, plot])
	if TYPE == 'browse':
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			count += 1
			name = translation(30801).format(str(count), completeTitle)
			addLink(name, thumb, {'mode': 'playTITLE', 'url': fitme(firstTitle)}, plot)
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
	else:
		if int(LIMIT) > 0:
			musicVideos = musicVideos[:int(LIMIT)]
		random.shuffle(musicVideos)
		for firstTitle, completeTitle, thumb, plot in musicVideos:
			endUrl = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playTITLE', 'url': fitme(firstTitle)}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': thumb, 'poster': thumb})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(endUrl, listitem)
		xbmc.Player().play(PLT)

def SearchDeezer():
	keyword = None
	someReceived = False
	keyword = dialog.input(translation(30770), type=xbmcgui.INPUT_ALPHANUM, autoclose=10000)
	if keyword: keyword = quote_plus(keyword, safe='')
	else: return
	FOUNDATION = [
		{'action': 'artistSEARCH', 'conv': 'strukturARTIST', 'name': translation(30771), 'slug': 'artist', 'turn': 'listDeezerSelection'},
		{'action': 'trackSEARCH', 'conv': 'strukturTRACK', 'name': translation(30772), 'slug': 'track', 'turn': 'listDeezerVideos'},
		{'action': 'albumSEARCH', 'conv': 'strukturALBUM', 'name': translation(30773), 'slug': 'album', 'turn': 'listDeezerSelection'},
		{'action': 'playlistSEARCH', 'conv': 'strukturPLAYLIST', 'name': translation(30774), 'slug': 'playlist', 'turn': 'listDeezerSelection'},
		{'action': 'userlistSEARCH', 'conv': 'strukturUSERLIST', 'name': translation(30775), 'slug': 'user', 'turn': 'listDeezerSelection'}]
	for elem in FOUNDATION:
		elem['action'] = getCache('{0}/{1}?q={2}&limit={3}&strict=on&output=json&index=0'.format(BASE_URL_DZ, elem['slug'], keyword, deezerSearchDisplay))
		elem['conv'] = json.loads(elem['action'])
		if elem['slug'] == 'track' and elem['conv']['total'] != 0:
			addAutoPlayDir(elem['name'], artpic+elem['slug']+'.png', {'mode': elem['turn'], 'url': keyword, 'extras': elem['slug'], 'transmit': icon})
			someReceived = True
		elif elem['slug'] in ['artist', 'album', 'playlist', 'user'] and elem['conv']['total'] != 0:
			addDir(elem['name'], artpic+elem['slug']+'.png', {'mode': elem['turn'], 'url': keyword, 'extras': elem['slug']})
			someReceived = True
	if not someReceived:
		addDir(translation(30776), artpic+'noresults.png', {'mode': 'root', 'url': keyword})
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listDeezerSelection(url, EXTRA):
	musicVideos = []
	musicIsolated = set()
	if url.startswith(BASE_URL_DZ):
		newURL = getCache(url)
	else:
		newURL = getCache('{0}/{1}?q={2}&limit={3}&strict=on&output=json&index=0'.format(BASE_URL_DZ, EXTRA, url, deezerSearchDisplay))
	response = json.loads(newURL)
	for item in response['data']:
		artist = cleaning(item['artist']['name']) if EXTRA == 'album' else cleaning(item['name']) if EXTRA == 'artist' else TitleCase(cleaning(item['title'])) if EXTRA == 'playlist' else None
		album = cleaning(item['title']) if EXTRA == 'album' else None
		user = TitleCase(cleaning(item['user']['name'])) if EXTRA == 'playlist' else TitleCase(cleaning(item['name'])) if EXTRA == 'user' else None
		numbers = str(item['nb_tracks']) if EXTRA in ['album', 'playlist'] else str(item['nb_fan']) if EXTRA == 'artist' else None
		version = cleaning(item['record_type']).title() if EXTRA == 'album' else None
		try:
			thumb = item['picture_big'] if EXTRA in ['artist', 'playlist', 'user'] else item['cover_big']
			if EXTRA in ['artist', 'user'] and thumb.endswith(EXTRA+'//500x500-000000-80-0-0.jpg'):
				thumb = artpic+'noavatar.gif'
		except:
			thumb = artpic+'noavatar.gif' if EXTRA in ['artist', 'user'] else artpic+'noimage.png'
		tracksUrl = item['tracklist'].split('top?limit=')[0]+'top?limit={0}&index=0'.format(deezerVideosDisplay) if EXTRA == 'artist' else item['tracklist']+'?limit={0}&index=0'.format(deezerVideosDisplay)
		special = artist+" - "+album if EXTRA == 'album' else artist.strip().lower() if EXTRA == 'artist' else artist+" - "+user if EXTRA == 'playlist' else user
		if special in musicIsolated:
			continue
		musicIsolated.add(special)
		musicVideos.append([numbers, artist, album, user, version, tracksUrl, special, thumb])
	musicVideos = sorted(musicVideos, key=lambda d:int(d[0]), reverse=True) if EXTRA == 'artist' else musicVideos
	for numbers, artist, album, user, version, tracksUrl, special, thumb in musicVideos:
		if EXTRA == 'artist':
			name = translation(30777).format(artist, numbers)
			plot = 'Artist:  '+artist+'[CR]Fans:  [COLOR FFFFA500]'+numbers+'[/COLOR]'
		elif EXTRA == 'album':
			name = translation(30778).format(special, version, numbers)
			plot = 'Artist:  '+artist+'[CR]Album:  '+album+'[CR]Version:  [COLOR deepskyblue]'+version+'[/COLOR][CR]Tracks:  [COLOR FFFFA500]'+numbers+'[/COLOR]'
		elif EXTRA == 'playlist':
			name = translation(30779).format(artist, user, numbers)
			plot = 'Artist:  '+artist+'[CR]User:  [COLOR deepskyblue]'+user+'[/COLOR][CR]Tracks:  [COLOR FFFFA500]'+numbers+'[/COLOR]'
		elif EXTRA == 'user':
			name = user
			plot = 'User:  [COLOR deepskyblue]'+user+'[/COLOR]'
		addAutoPlayDir(name, thumb, {'mode': 'listDeezerVideos', 'url': tracksUrl, 'extras': EXTRA, 'transmit': thumb}, plot)
	try:
		nextPage = response['next']
		if BASE_URL_DZ in nextPage:
			addDir(translation(30802), artpic+'nextpage.png', {'mode': 'listDeezerSelection', 'url': nextPage, 'extras': EXTRA})
	except: pass
	xbmcplugin.endOfDirectory(ADDON_HANDLE)
	if forceView:
		xbmc.executebuiltin('Container.SetViewMode('+viewIDPlaylists+')')

def listDeezerVideos(url, TYPE, LIMIT, EXTRA, PHOTO):
	musicVideos = []
	musicIsolated = set()
	count = 0
	PLT = cleanPlaylist() if TYPE == 'play' else None
	if EXTRA == 'track' and not 'index=' in url:
		newURL = getCache('{0}/{1}?q={2}&limit={3}&strict=on&output=json&index=0'.format(BASE_URL_DZ, EXTRA, url, deezerVideosDisplay))
	else:
		newURL = getCache(url)
	response = json.loads(newURL)
	for item in response['data']:
		artist = cleaning(item['artist']['name'])
		song = cleaning(item['title'])
		if song.isupper() or song.islower():
			song = TitleCase(song)
		plot = 'Artist:  '+artist+'[CR]'+'Song:  '+song
		firstTitle = artist+" - "+song
		if firstTitle in musicIsolated or artist == "":
			continue
		musicIsolated.add(firstTitle)
		album = cleaning(item['album']['title']) if EXTRA == 'track' else ""
		if album != "": plot += '[CR]'+'Album:  '+album
		if EXTRA == 'track':
			try: PHOTO = item['album']['cover_big']
			except: PHOTO = artpic+'noimage.png'
		for snippet in blackList:
			if snippet.strip().lower() and snippet.strip().lower() in firstTitle.lower():
				continue
		musicVideos.append([firstTitle, album, PHOTO, plot])
	if TYPE == 'browse':
		for firstTitle, album, PHOTO, plot in musicVideos:
			count += 1
			name = translation(30780).format(firstTitle, album) if EXTRA == 'track' else translation(30801).format(str(count), firstTitle)
			addLink(name, PHOTO, {'mode': 'playTITLE', 'url': fitme(firstTitle)}, plot)
		try:
			nextPage = response['next']
			if 'https://api.deezer.com/' in nextPage:
				addAutoPlayDir(translation(30802), artpic+'nextpage.png', {'mode': 'listDeezerVideos', 'url': nextPage, 'extras': EXTRA, 'transmit': PHOTO})
		except: pass
		xbmcplugin.endOfDirectory(ADDON_HANDLE)
		if forceView:
			xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
	else:
		if int(LIMIT) > 0:
			musicVideos = musicVideos[:int(LIMIT)]
		random.shuffle(musicVideos)
		for firstTitle, album, PHOTO, plot in musicVideos:
			endUrl = '{0}?{1}'.format(HOST_AND_PATH, urlencode({'mode': 'playTITLE', 'url': fitme(firstTitle)}))
			listitem = xbmcgui.ListItem(firstTitle)
			listitem.setArt({'icon': icon, 'thumb': PHOTO, 'poster': PHOTO})
			listitem.setProperty('IsPlayable', 'true')
			PLT.add(endUrl, listitem)
		xbmc.Player().play(PLT)

def playTITLE(SUFFIX):
	query = 'official+'+quote_plus(SUFFIX.lower()).replace('%5B', '').replace('%5D', '').replace('%28', '').replace('%29', '').replace('%2F', '')
	COMBI_VIDEO = []
	content = getUrl('https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults=5&order=relevance&q={0}&key={1}'.format(query, myTOKEN))
	response = json.loads(content)
	for item in response.get('items', []):
		if item.get('id', {}).get('kind', '') == 'youtube#video':
			title = cleaning(item['snippet']['title'])
			IDD = str(item['id']['videoId'])
			COMBI_VIDEO.append([title, IDD])
	if COMBI_VIDEO:
		parts = COMBI_VIDEO[:]
		matching = [s for s in parts if not 'audio' in s[0].lower() and not 'hörprobe' in s[0].lower()]
		youtubeID = matching[0][1] if matching else parts[0][1]
		finalURL = '{0}?video_id={1}'.format('plugin://plugin.video.youtube/play/', str(youtubeID))
		log("(navigator.playTITLE) StreamURL : {0}".format(finalURL))
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, xbmcgui.ListItem(path=finalURL))
		xbmc.sleep(1000)
		if enableINFOS: infoMessage()
	else:
		return dialog.notification(translation(30521).format('VIDEO'), translation(30525).format(SUFFIX), icon, 10000)

def infoMessage():
	count = 0
	while not xbmc.Player().isPlaying():
		xbmc.sleep(200)
		if count == 50:
			break
		count += 1
	xbmc.sleep(infoDelay*1000)
	if xbmc.Player().isPlaying() and infoType == '0':
		xbmc.sleep(1500)
		xbmc.executebuiltin('ActivateWindow(12901)')
		xbmc.sleep(infoDuration*1000)
		xbmc.executebuiltin('ActivateWindow(12005)')
		xbmc.sleep(500)
		xbmc.executebuiltin('Action(Back)')
	elif xbmc.Player().isPlaying() and infoType == '1':
		xbmc.getInfoLabel('Player.Title')
		xbmc.getInfoLabel('Player.Duration')
		xbmc.getInfoLabel('Player.Art(thumb)')
		xbmc.sleep(500)
		TITLE = py2_enc(xbmc.getInfoLabel('Player.Title'))
		if TITLE.isupper() or TITLE.islower():
			TITLE = TitleCase(TITLE)
		RUNTIME = xbmc.getInfoLabel('Player.Duration')
		PHOTO = xbmc.getInfoLabel('Player.Art(thumb)')
		xbmc.sleep(1000)
		dialog.notification(translation(30803), TITLE+'[COLOR blue]  * '+RUNTIME+' *[/COLOR]', PHOTO, infoDuration*1000)
	else: pass

def AddToQueue():
	return xbmc.executebuiltin('Action(Queue)')

def addDir(name, image, params={}, plot=None, folder=True):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image})
	if useThumbAsFanart:
		liz.setArt({'fanart': defaultFanart})
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=folder)

def addAutoPlayDir(name, image, params={}, plot=None):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Mediatype': 'musicvideo'})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image})
	if useThumbAsFanart:
		liz.setArt({'fanart': defaultFanart})
	entries = []
	entries.append([translation(30831), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': params.get('mode'), 'url': params.get('url'), 'type': 'play', 'extras': params.get('extras', ''), 'transmit': params.get('transmit', '')}))])
	entries.append([translation(30832), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': params.get('mode'), 'url': params.get('url'), 'type': 'play', 'limit': '10', 'extras': params.get('extras', ''), 'transmit': params.get('transmit', '')}))])
	entries.append([translation(30833), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': params.get('mode'), 'url': params.get('url'), 'type': 'play', 'limit': '20', 'extras': params.get('extras', ''), 'transmit': params.get('transmit', '')}))])
	entries.append([translation(30834), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': params.get('mode'), 'url': params.get('url'), 'type': 'play', 'limit': '30', 'extras': params.get('extras', ''), 'transmit': params.get('transmit', '')}))])
	entries.append([translation(30835), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': params.get('mode'), 'url': params.get('url'), 'type': 'play', 'limit': '40', 'extras': params.get('extras', ''), 'transmit': params.get('transmit', '')}))])
	entries.append([translation(30836), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, urlencode({'mode': params.get('mode'), 'url': params.get('url'), 'type': 'play', 'limit': '50', 'extras': params.get('extras', ''), 'transmit': params.get('transmit', '')}))])
	liz.addContextMenuItems(entries)
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz, isFolder=True)

def addLink(name, image, params={}, plot=None):
	u = '{0}?{1}'.format(HOST_AND_PATH, urlencode(params))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Mediatype': 'musicvideo'})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image})
	if useThumbAsFanart:
		liz.setArt({'fanart': defaultFanart})
	liz.setProperty('IsPlayable', 'true')
	liz.addContextMenuItems([(translation(30804), 'RunPlugin({0}?{1})'.format(HOST_AND_PATH, 'mode=AddToQueue'))])
	return xbmcplugin.addDirectoryItem(handle=ADDON_HANDLE, url=u, listitem=liz)
