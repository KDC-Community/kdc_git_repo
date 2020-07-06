#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import re
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3
if PY2:
	reload(sys)
	sys.setdefaultencoding('utf-8')
	from urllib import quote, unquote, quote_plus, unquote_plus, urlencode  # Python 2.X
	from urllib2 import build_opener, Request, urlopen  # Python 2.X
	from urlparse import urljoin, urlparse, urlunparse  # Python 2.X
elif PY3:
	from urllib.parse import quote, unquote, quote_plus, unquote_plus, urlencode, urljoin, urlparse, urlunparse  # Python 3+
	from urllib.request import build_opener, Request, urlopen  # Python 3+
import requests
try: import StorageServer
except: from . import storageserverdummy as StorageServer
import json
import xbmcvfs
import shutil
import socket
import time
from datetime import datetime, timedelta
import io
import gzip
import ssl
import base64
from collections import OrderedDict
from inputstreamhelper import Helper


global debuging
pluginhandle = int(sys.argv[1])
addon = xbmcaddon.Addon()
socket.setdefaulttimeout(40)
addonPath = xbmc.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath    = xbmc.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
defaultFanart = os.path.join(addonPath, 'fanart.jpg') or os.path.join(addonPath, 'resources', 'fanart.jpg')
icon = os.path.join(addonPath, 'icon.png') or os.path.join(addonPath, 'resources', 'icon.png')
artpic = os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
WORKFILE = os.path.join(dataPath, 'episode_data.txt')
channelFavsFile = os.path.join(dataPath, 'my_TVNOW_favourites.txt').encode('utf-8').decode('utf-8')
cachePERIOD = int(addon.getSetting('cacherhythm'))
cache = StorageServer.StorageServer(addon.getAddonInfo('id'), cachePERIOD) # (Your plugin name, Cache time in hours)
freeonly = addon.getSetting('freeonly')
forceBEST = addon.getSetting('force_best')
selectionHD = addon.getSetting('high_definition') == 'true'
markMOVIES = addon.getSetting('mark_movies') == 'true'
showDATE = addon.getSetting('show_date') == 'true'
enableAdjustment = addon.getSetting('show_settings') == 'true'
DEB_LEVEL = (xbmc.LOGNOTICE if addon.getSetting('enableDebug') == 'true' else xbmc.LOGDEBUG)
enableLibrary = addon.getSetting('tvnow_library') == 'true'
mediaPath = addon.getSetting('mediapath')
updatestd = addon.getSetting('updatestd')
KODI_17 = int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) == 17
KODI_18 = int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) >= 18
KODI_vs18 = int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) == 18
KODI_vs19 = int(xbmc.getInfoLabel('System.BuildVersion')[0:2]) >= 19
baseURL = 'https://api.tvnow.de/v3/'

if KODI_vs19:
	addon.setSetting('Notify_Select', '1')
elif KODI_vs18:
	addon.setSetting('Notify_Select', '2')
elif KODI_17:
	addon.setSetting('Notify_Select', '3')
else:
	addon.setSetting('Notify_Select', '4')

xbmcplugin.setContent(int(sys.argv[1]), 'movies')

if not xbmcvfs.exists(dataPath):
	xbmcvfs.mkdirs(dataPath)

def py2_enc(s, encoding='utf-8'):
	if PY2:
		if not isinstance(s, basestring):
			s = str(s)
		s = s.encode(encoding) if isinstance(s, unicode) else s
	return s

def py2_uni(s, encoding='utf-8'):
	if PY2 and isinstance(s, str):
		s = unicode(s, encoding)
	return s

def py3_dec(d, encoding='utf-8'):
	if PY3 and isinstance(d, bytes):
		d = d.decode(encoding)
	return d

def get_sec(time_str):
	h, m, s = time_str.split(':')
	return int(h)*3600+int(m)*60+int(s)

def get_min(time_str):
	h, m, s = time_str.split(':')
	SECS = 0
	if int(s) >= 30: SECS = 1
	return int(h)*60+int(m)+SECS

def translation(id):
	return py2_enc(addon.getLocalizedString(id))

def failing(content):
	log(content, xbmc.LOGERROR)

def debug_MS(content):
	log(content, DEB_LEVEL)

def log(msg, level=xbmc.LOGNOTICE):
	xbmc.log('[{0} v.{1}]{2}'.format(addon.getAddonInfo('id'), addon.getAddonInfo('version'), py2_enc(msg)), level)

if addon.getSetting('checkwidevine') == 'true':
	pos = 0
	if pos < 1:
		pos += 1
		debug_MS("(checkwidevine_ON) XXX Widevineüberprüfung ist eingeschaltet !!! XXX")
	is_helper = Helper('mpd', drm='widevine')
	if not is_helper.check_inputstream():
		failing("(check_inputstream) ERROR - ERROR - ERROR :\n##### !!! Widevine ist NICHT installiert !!! #####")
		xbmcgui.Dialog().notification(translation(30521).format('Widevine'), translation(30527), icon, 12000)

if addon.getSetting('cert') == 'false':
	pos = 0
	if pos < 1:
		pos += 1
		debug_MS("(cert_OFF) XXX Web-Zertifikatüberprüfung ist abgeschaltet !!! XXX")
	try: _create_unverified_https_context = ssl._create_unverified_context
	except AttributeError: pass
	else: ssl._create_default_https_context = _create_unverified_https_context

def makeREQUEST(url):
	return cache.cacheFunction(getUrl, url)

def getUrl(url, header=None, referer=None, agent='Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0'):
	opener = build_opener()
	opener.addheaders = [('User-Agent', agent), ('Accept-Encoding', 'gzip, deflate')]
	try:
		if header: opener.addheaders = header
		if referer: opener.addheaders = [('Referer', referer)]
		response = opener.open(url, timeout=30)
		if response.info().get('Content-Encoding') == 'gzip':
			content = py3_dec(gzip.GzipFile(fileobj=io.BytesIO(response.read())).read())
		else:
			content = py3_dec(response.read())
	except Exception as e:
		failure = str(e)
		failing("(getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
		#xbmcgui.Dialog().notification(translation(30521).format('URL'), "ERROR = [COLOR red]{0}[/COLOR]".format(failure), icon, 15000)
		content = ""
		return sys.exit(0)
	opener.close()
	return content

def ADDON_operate(IDD):
	js_query = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.GetAddonDetails", "params": {"addonid":"'+IDD+'", "properties": ["enabled"]}, "id":1}')
	if '"enabled":false' in js_query:
		try:
			xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "Addons.SetAddonEnabled", "params": {"addonid":"'+IDD+'", "enabled":true}, "id":1}')
			failing("(ADDON_operate) ERROR - ERROR - ERROR :\n##### Das benötigte Addon : *{0}* ist NICHT aktiviert !!! #####\n##### Es wird jetzt versucht die Aktivierung durchzuführen !!! #####".format(IDD))
		except: pass
	if '"error":' in js_query:
		xbmcgui.Dialog().ok(addon.getAddonInfo('id'), translation(30501).format(IDD))
		failing("(ADDON_operate) ERROR - ERROR - ERROR :\n##### Das benötigte Addon : *{0}* ist NICHT installiert !!! #####".format(IDD))
		return False
	if '"enabled":true' in js_query:
		return True

def clearCache():
	debug_MS("(clearCache) -------------------------------------------------- START = clearCache --------------------------------------------------")
	debug_MS("(clearCache) ========== Lösche jetzt den Addon-Cache ==========")
	cache.delete('%')
	xbmc.sleep(1000)
	xbmcgui.Dialog().ok(addon.getAddonInfo('id'), translation(30502))

def index():
	STATUS,TOKEN = LOGIN()
	addDir(translation(30601), "", 'listShowsFavs', icon)
	addDir(translation(30602), "", 'listStations', icon)
	addDir(translation(30603) , "rtl", 'listThemes', icon)
	addDir(translation(30604) , "", 'listTopics', icon)
	addDir(translation(30605), "", 'listGenres', icon)
	addDir(translation(30606), "", 'newShows', icon)
	addDir(translation(30607), "0", 'getSearch', icon, nosub=1)
	if STATUS==3 and KODI_18: addDir(translation(30608), "", 'liveTV', icon)
	addDir(translation(30609).format(str(cachePERIOD)), "", 'clearCache', icon)
	if enableAdjustment:
		addDir(translation(30610), "", 'aSettings', icon)
		if ADDON_operate('inputstream.adaptive'):
			addDir(translation(30611), "", 'iSettings', icon)
	xbmcplugin.endOfDirectory(pluginhandle)

def listSeries(url):
	debug_MS("(listSeries) -------------------------------------------------- START = listSeries --------------------------------------------------")
	xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
	debug_MS("(listSeries) ### startURL : {0} ###".format(url))
	pageNUMBER = 0  
	if 'maxPerPage' in url:
		pageNUMBER = 1
	position = 1
	total = 1
	while (total > 0):  
		if pageNUMBER > 0:
			newURL = url+'&page='+str(pageNUMBER)
		else: newURL = url
		debug_MS("(listSeries) ### newURL : {0} ###".format(newURL))
		content = makeREQUEST(newURL)
		DATA = json.loads(content, object_pairs_hook=OrderedDict)
		if 'movies' in DATA and 'items' in str(DATA['movies']):
			elements = DATA['movies']['items']
		else: elements = DATA['items']
		for seriesITEM in elements:
			debug_MS("(listSeries) ##### seriesITEM : {0} #####".format(str(seriesITEM)))
			seriesID = str(seriesITEM['id'])
			name = py2_enc(seriesITEM['title']).strip()
			station = seriesITEM['station'].upper()
			seoUrl = py2_enc(seriesITEM['seoUrl'])
			try: seriesITEM = seriesITEM['format']
			except: pass
			logo = ""
			if 'formatimageArtwork' in seriesITEM and seriesITEM['formatimageArtwork'] != "" and seriesITEM['formatimageArtwork'] != None:
				logo = cleanPhoto(seriesITEM['formatimageArtwork'])
			if logo == "" and 'defaultImage169Logo' in seriesITEM and seriesITEM['defaultImage169Logo'] != "" and seriesITEM['defaultImage169Logo'] != None:
				logo = cleanPhoto(seriesITEM['defaultImage169Logo'])
			if logo == "": logo = 'https://aistvnow-a.akamaihd.net/tvnow/format/'+seriesID+'_02logo/image.jpg'
			genre = py2_enc(seriesITEM['genre1']).strip()
			category = seriesITEM['categoryId']
			plot = ""
			if 'infoTextLong' in seriesITEM and seriesITEM['infoTextLong'] != "" and seriesITEM['infoTextLong'] != None:
				plot = py2_enc(seriesITEM['infoTextLong']).strip()
			if plot == "" and 'infoText' in seriesITEM and seriesITEM['infoText'] != "" and seriesITEM['infoText'] != None:
				plot = py2_enc(seriesITEM['infoText']).strip()
			freeEP = seriesITEM['hasFreeEpisodes']
			addType=1
			if os.path.exists(channelFavsFile):
				with open(channelFavsFile, 'r') as output:
					lines = output.readlines()
					for line in lines:
						if line.startswith('###START'):
							part = line.split('###')
							if seriesID == part[2]: addType=2
			if category == 'film':
				addType=3
				if markMOVIES: name = '[I]'+name+'[/I]'
			debug_MS("(listSeries) ### TITLE = {0} || IDD = {1} || PHOTO = {2} || addType = {3} ###".format(name, seriesID, logo, str(addType)))
			addDir(name, seriesID, 'listSeasons', logo, plot, origSERIE=name, genre=genre, studio=station, addType=addType)
			position += 1
		debug_MS("(listSeries) Anzahl-in-Liste : {0}".format(str(int(position)-1)))
		try:
			debug_MS("(listSeries) Anzahl-auf-Webseite : {0}".format(str(DATA['total'])))
			total = DATA['total'] - position
		except: total = 0
		pageNUMBER += 1
	xbmcplugin.endOfDirectory(pluginhandle)

def listSeasons(Xidd, Xbild):
	debug_MS("(listSeasons) -------------------------------------------------- START = listSeasons --------------------------------------------------")
	COMBI_SEASON = []
	#http://api.tvnow.de/v3/formats/seo?fields=*,.*,formatTabs.*,formatTabs.headline&name=chicago-fire
	url = 'http://api.tvnow.de/v3/formats/'+str(Xidd)+'?fields='+quote_plus('*,.*,formatTabs.*,formatTabs.headline,annualNavigation.*')
	try:
		content = makeREQUEST(url)
		debug_MS("(listSeasons) ##### CONTENT : {0} #####".format(str(content)))
		DATA = json.loads(content, object_pairs_hook=OrderedDict)
		seriesname = py2_enc(DATA['title']).strip()
	except: return xbmcgui.Dialog().notification(translation(30522).format(str(Xidd)), translation(30523), icon, 12000)
	seasonID = str(DATA['id'])
	Xbild = cleanPhoto(Xbild)
	if DATA['annualNavigation']['total'] == 1:
		debug_MS("(listSeasons) no.1 ### SERIE = {0} || seasonID = {1} || PHOTO = {2} ###".format(seriesname, seasonID, str(Xbild)))
		listEpisodes('##'+seasonID+'##')
	else:
		for each in DATA['annualNavigation']['items']:
			year = str(each['year'])
			debug_MS("(listSeasons) no.2 ### SERIE = {0} || seasonID = {1} || PHOTO = {2} || YEAR = {3} ###".format(seriesname, seasonID, str(Xbild), year))
			COMBI_SEASON.append([seasonID, year, Xbild, seriesname])
	if COMBI_SEASON:
		for seasonID, year, Xbild, seriesname in sorted(COMBI_SEASON, key=lambda num:num[1], reverse=True):
			addDir(translation(30620).format(year), seasonID+'@@'+year+'@@', 'listEpisodes', Xbild, origSERIE=seriesname, addType=2)
	xbmcplugin.endOfDirectory(pluginhandle)

def listEpisodes(Xidd):
	debug_MS("(listEpisodes) -------------------------------------------------- START = listEpisodes --------------------------------------------------")
	xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_UNSORTED)
	xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
	STATUS,TOKEN = LOGIN()
	COMBI_EPISODE = []
	uno_LIST = []
	if '@@' in Xidd:
		elem_IDD = Xidd.split('@@')[0]
		elem_YEAR = Xidd.split('@@')[1]
		startURL = 'https://api.tvnow.de/v3/movies?fields=*,format,paymentPaytypes,pictures,trailers&filter={%22BroadcastStartDate%22:{%22between%22:{%22start%22:%22'+elem_YEAR+'-01-01%2000:00:00%22,%22end%22:%20%22'+elem_YEAR+'-12-31%2023:59:59%22}},%20%22FormatId%22%20:%20'+elem_IDD+'}&maxPerPage=500&order=BroadcastStartDate%20asc'
	elif '##' in Xidd:
		startURL = 'https://api.tvnow.de/v3/movies?fields=*,format,paymentPaytypes,pictures,trailers&filter={%20%22FormatId%22%20:%20'+Xidd.replace('##', '')+'}&maxPerPage=500&order=BroadcastStartDate%20asc'
	else:
		startURL = Xidd
	debug_MS("(listEpisodes) ### startURL : {0} ###".format(startURL))
	content = makeREQUEST(startURL)
	DATA = json.loads(content, object_pairs_hook=OrderedDict)    
	if 'formatTabPages' in DATA and 'items' in str(DATA['formatTabPages']):
		for each in DATA['formatTabPages']['items']:
			elements = each['container']['movies']['items']
	elif not 'formatTabPages' in DATA and 'movies' in DATA and 'items' in str(DATA['movies']):
		elements = DATA['movies']['items']
	else: elements = DATA['items']
	for folge in elements:
		debug_MS("(listEpisodes) ##### FOLGE : {0} #####".format(str(folge)))
		try: debug_MS(str(folge['isDrm']))
		except: continue
		spezTIMES = None
		normTIMES = None
		begins = None
		try:
			broadcast = datetime(*(time.strptime(folge['broadcastStartDate'][:19], '%Y{0}%m{0}%d %H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2019-06-02 11:40:00
			spezTIMES = broadcast.strftime('%a{0} %d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':').replace('Mon', translation(30621)).replace('Tue', translation(30622)).replace('Wed', translation(30623)).replace('Thu', translation(30624)).replace('Fri', translation(30625)).replace('Sat', translation(30626)).replace('Sun', translation(30627))
			normTIMES = broadcast.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
			begins =  broadcast.strftime('%d{0}%m{0}%Y').format('.')
		except: pass
		episID = str(folge['id'])
		title = py2_enc(folge['title']).strip()
		try: seriesname = py2_enc(folge['format']['title']).strip()
		except: 
			try: seriesname = py2_enc(folge['format']['seoUrl']).replace('-', ' ').title().strip()
			except: continue
		season = '0'
		if 'season' in folge and folge['season'] != "" and str(folge['season']) != "0" and folge['season'] != None:
			season = str(folge['season'])
		episode = '0'
		if 'episode' in folge and folge['episode'] != "" and str(folge['episode']) != "0" and folge['episode'] != None:
			episode = str(folge['episode'])
		duration = '0'
		if 'duration' in folge and folge['duration'] !="" and folge['duration'] != None:
			duration = get_sec(folge['duration'])
		tagline = None
		if 'teaserText' in folge and folge['teaserText'] !="" and folge['teaserText'] != None:
			tagline = py2_enc(folge['teaserText']).strip()
		plot = ""
		if 'articleLong' in folge and folge['articleLong'] !="" and folge['articleLong'] != None:
			plot = py2_enc(folge['articleLong']).strip()
		if plot == "" and 'articleShort' in folge and folge['articleShort'] !="" and folge['articleShort'] != None:
			plot = py2_enc(folge['articleShort']).strip()
		Note_1 =""
		Note_2 =""
		Note_3 =""
		Note_4 =""
		Note_5 =""
		Note_6 =""
		if seriesname !="": Note_1 = seriesname
		if season != '0' and episode != '0': Note_3 = translation(30628).format(season, episode)
		if spezTIMES: Note_4 = translation(30629).format(str(spezTIMES))
		mpaa =""
		if 'fsk' in folge and folge['fsk'] != "" and str(folge['fsk']) != '0' and folge['fsk'] != None:
			mpaa = translation(30630).format(str(folge['fsk']))
		year =""
		if 'productionYear' in folge and folge['productionYear'] != "" and str(folge['productionYear']) != '0' and folge['productionYear'] != None:
			year = folge['productionYear']
		if showDATE and normTIMES:
			Note_5 = translation(30631).format(str(normTIMES))
		PayType = True
		if 'payed' in folge and str(folge['payed']) !="" and folge['payed'] != None: PayType = folge['payed']
		videoURL = '0'
		if STATUS == 3:
			if 'manifest' in folge and 'dashhd' in folge['manifest'] and folge['manifest']['dashhd'] != "" and freeonly=='false' and selectionHD: # HD-Play with Pay-Account
				videoURL = folge['manifest']['dashhd'].split('.mpd')[0]+'.mpd'
			elif 'manifest' in folge and 'dash' in folge['manifest'] and folge['manifest']['dash'] != "" and freeonly=='false': # Normal-Play with Pay-Account
				videoURL = folge['manifest']['dash'].split('.mpd')[0]+'.mpd'
		elif STATUS < 3 and 'manifest' in folge and 'dash' in folge['manifest'] and folge['manifest']['dash'] != "" :
			if PayType == True: # Normal-Play without Pay-Account
				videoURL = folge['manifest']['dash'].split('.mpd')[0]+'.mpd'
		try: deeplink = 'https://www.tvnow.de/'+folge['format']['formatType'].replace('show', 'shows').replace('serie', 'serien').replace('film', 'filme')+'/'+py2_enc(folge['format']['seoUrl'])+'-'+str(folge['format']['id'])
		except: deeplink =""
		# BILD_1 = https://aistvnow-a.akamaihd.net/tvnow/movie/1454577/960x0/image.jpg
		# BILD_2 = https://ais.tvnow.de/tvnow/movie/1454577/960x0/image.jpg
		image = 'https://aistvnow-a.akamaihd.net/tvnow/movie/'+episID+'/1200x0/image.jpg'
		if freeonly == 'true' and PayType == False and STATUS < 3: episID = '0'
		station =""
		if 'format' in folge and 'station' in folge['format'] and folge['format']['station'] != "" and folge['format']['station'] != None:
			station = folge['format']['station'].upper()
		genre =""
		genreList=[]
		if 'format' in folge and 'genres' in folge['format'] and folge['format']['genres'] != "" and folge['format']['genres'] != None:
			for item in folge['format']['genres']:
				gNames = py2_enc(item)
				genreList.append(gNames)
			genre =' / '.join(genreList)
		if genre =="" and 'format' in folge and 'genre1' in folge['format'] and folge['format']['genre1'] != "" and folge['format']['genre1'] != None:
			genre = py2_enc(folge['format']['genre1']).strip()
		try: ttype = folge['format']['categoryId']
		except: ttype =""
		ftype = 'episode'
		if ttype == 'film': ftype = 'movie'
		if (not KODI_18 and folge['isDrm'] == True and PayType == False):
			Note_2 = '   [COLOR skyblue](premium|[/COLOR][COLOR orangered]DRM)[/COLOR]'
			Note_6 = '     [COLOR deepskyblue](premium|[/COLOR][COLOR orangered]DRM)[/COLOR]'
		elif (not KODI_18 and folge['isDrm'] == True and PayType == True):
			Note_2 = '   [COLOR orangered](DRM)[/COLOR]'
			Note_6 = '     [COLOR orangered](DRM)[/COLOR]'
		elif (KODI_17 or KODI_18) and PayType == False and STATUS < 3:
			Note_2 = '   [COLOR skyblue](premium)[/COLOR]'
			Note_6 = '     [COLOR deepskyblue](premium)[/COLOR]'
		plot = Note_1+Note_2+'[CR]'+Note_3+Note_4+'[CR][CR]'+plot
		title1 = title
		title2 = title+Note_5+Note_6
		if freeonly == 'true' and PayType == False and STATUS < 3: nosub = str(deeplink)+'@@'+str(folge['isDrm'])+'@@C3'+str(TOKEN)+'A5@@'+str(PayType)
		else: nosub = str(deeplink)+'@@'+str(folge['isDrm'])+'@@'+str(TOKEN)+'@@'+str(PayType)
		COMBI_EPISODE.append([episID, videoURL, image, title1, title2, plot, tagline, duration, seriesname, season, episode, genre, mpaa, year, begins, station, ftype, nosub])
	if COMBI_EPISODE:
		for episID, videoURL, image, title1, title2, plot, tagline, duration, seriesname, season, episode, genre, mpaa, year, begins, station, ftype, nosub in COMBI_EPISODE:
			EP_entry = py2_enc(episID+'@@'+str(videoURL)+'@@'+str(seriesname)+'@@'+str(title2)+'@@'+str(image)+'@@'+str(duration)+'@@'+str(season)+'@@'+str(episode)+'@@'+str(nosub)+'@@')
			if EP_entry not in uno_LIST:
				uno_LIST.append(EP_entry)
			listitem = xbmcgui.ListItem(path=sys.argv[0]+'?IDENTiTY='+episID+'&mode=playCODE')
			ilabels = {}
			ilabels['Season'] = season
			if episode != '0':
				ilabels['Episode'] = episode
				xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_EPISODE)
			ilabels['Tvshowtitle'] = seriesname
			ilabels['Title'] = title2
			ilabels['Tagline'] = tagline
			ilabels['Plot'] = plot
			ilabels['Duration'] = duration
			if begins != None:
				ilabels['Date'] = begins
				xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_DATE)
			ilabels['Year'] = year
			ilabels['Genre'] = genre
			ilabels['Director'] = None
			ilabels['Writer'] = None
			ilabels['Studio'] = station
			ilabels['Mpaa'] = mpaa
			ilabels['Mediatype'] = ftype
			listitem.setInfo(type='Video', infoLabels=ilabels)
			listitem.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
			if image != icon and not artpic in image:
				listitem.setArt({'fanart': image})
			listitem.addStreamInfo('Video', {'Duration':duration})
			listitem.setProperty('IsPlayable', 'true')
			playInfos = '###START###{0}?IDENTiTY={1}&mode=playCODE###{2}###{3}###END###'.format(sys.argv[0], episID, title2, image)
			listitem.addContextMenuItems([(translation(30654), 'RunPlugin('+sys.argv[0]+'?mode=addQueue&url='+quote_plus(playInfos)+')')])
			xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys.argv[0]+'?IDENTiTY='+episID+'&mode=playCODE', listitem=listitem)
		with open(WORKFILE, 'w') as input:
			input.write('\n'.join(uno_LIST))
	xbmcplugin.endOfDirectory(pluginhandle)

def getToken():
	debug_MS("(getToken) -------------------------------------------------- START = getToken --------------------------------------------------")
	nomURL = 'https://www.tvnow.de/'
	rq1 =  getUrl(nomURL)
	try: DOC = re.findall(r'<script src="(main\-[A-z0-9]+\.[A-z0-9]+\.js)"', rq1, re.S)[-1]
	except:
		failing("(getToken) ##### persToken-FIRST : Gesuchtes Token-Dokument NICHT gefunden !!! #####")
		return xbmcgui.Dialog().notification('ERROR - Token_01 - ERROR', translation(30528), icon, 12000)
	rq2 = getUrl(nomURL+DOC)
	NUM = re.search(r'{key:"getDefaultUserdata",value:function\(\){return{token:"([A-z0-9.]+)"', rq2)
	if NUM:
		return NUM.group(1)
	return '0'

def LOGIN():
	debug_MS("(LOGIN) >>>>> Starte LOGIN >>>>>")
	USER = addon.getSetting('user')
	PWD = addon.getSetting('pass')
	debug_MS("(LOGIN) ##### START-CHECK = Setting(freeonly) : {0} #####".format(str(addon.getSetting("freeonly"))))
	if USER == "" or PWD == "":
		debug_MS("(LOGIN) ##### KEIN Benutzername oder Passwort eingetragen #####")
		addon.setSetting('freeonly', 'true')
		addon.setSetting('high_definition', 'false')
		persToken = getToken()
		if persToken == '0':
			failing("(LOGIN) ##### persToken-SECOND : Token NICHT gefunden !!! #####")
			debug_MS("(LOGIN) ##### END-CHECK = Setting(freeonly) : {0} #####".format(str(addon.getSetting("freeonly"))))
			debug_MS("(LOGIN) <<<<< Ende LOGIN <<<<<")
			return 0,persToken
		else:
			debug_MS("(LOGIN) ##### persToken : {0} #####".format(str(persToken)))
			debug_MS("(LOGIN) ##### END-CHECK = Setting(freeonly) : {0} #####".format(str(addon.getSetting("freeonly"))))
			debug_MS("(LOGIN) <<<<< Ende LOGIN <<<<<")
			return 1,persToken
	try:
		url = 'https://auth.tvnow.de/login'
		headers = {'content-type': 'application/json', 'access-control-allow-headers': 'DNT,X-CustomHeader,Keep-Alive,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Authorization,X-Auth-Token,X-Now-Logged-In', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0'}
		payload = {'email': USER, 'password': PWD}
		debug_MS("(LOGIN) ##### Credentialz : {0} #####".format(payload))
		r = requests.post(url, headers=headers, json=payload)
		debug_MS("(LOGIN) ##### Response Status-Code : {0} #####".format(str(r.status_code)))
		result = r.json()
		if 'token' in result and result['token'] !="":
			persToken = result['token']
			debug_MS("(LOGIN) ##### persToken : {0} #####".format(str(persToken)))
			base64Parts = persToken.split('.')
			tokenRES = '%s==' %base64Parts[1]
			DATA = json.loads(base64.b64decode(tokenRES).decode('utf-8', 'ignore'))
			debug_MS("(LOGIN) ##### jsonDATA-Token base64-decoded : {0} #####".format(str(DATA)))
			addon.setSetting('license_ending', '')
			if 'licenceEndDate' in DATA and DATA['licenceEndDate'] !="":
				try:
					ENDING = datetime(*(time.strptime(DATA['licenceEndDate'][:19], '%Y{0}%m{0}%dT%H{1}%M{1}%S'.format('-', ':'))[0:6]))# 2019-11-05T18:09:41+00:00
					lic_end = ENDING.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
					addon.setSetting('license_ending', str(lic_end))
				except: pass
			if 'subscriptionState' in DATA and (DATA['subscriptionState']==5 or DATA['subscriptionState']==4):
				debug_MS("(LOGIN) ##### Paying-Member : subscriptionState = {0} = (Account is OK) #####".format(str(DATA["subscriptionState"])))
				addon.setSetting('freeonly', 'false')
				if forceBEST == '0': addon.setSetting('high_definition', 'true')
				else: addon.setSetting('high_definition', 'false')
				debug_MS("(LOGIN) ##### END-CHECK = Setting(freeonly) : {0} #####".format(str(addon.getSetting("freeonly"))))
				debug_MS("(LOGIN) <<<<< Ende LOGIN <<<<<")
				return 3,persToken
			elif 'hasAcquiredPackages' in DATA and DATA['hasAcquiredPackages']==True:
				debug_MS("(LOGIN) ##### Paying-Member : hasAcquiredPackages = {0} = (Account is OK) #####".format(str(DATA['hasAcquiredPackages'])))
				addon.setSetting('freeonly', 'false')
				if forceBEST == '0': addon.setSetting('high_definition', 'true')
				else: addon.setSetting('high_definition', 'false')
				debug_MS("(LOGIN) ##### END-CHECK = Setting(freeonly) : {0} #####".format(str(addon.getSetting("freeonly"))))
				debug_MS("(LOGIN) <<<<< Ende LOGIN <<<<<")
				return 3,persToken
			elif 'roles' in DATA and 'premium' in DATA['roles']:
				debug_MS("(LOGIN) ##### Paying-Member : roles = {0} = (Account is OK) #####".format(str(DATA['roles'])))
				addon.setSetting('freeonly', 'false')
				if forceBEST == '0': addon.setSetting('high_definition', 'true')
				else: addon.setSetting('high_definition', 'false')
				debug_MS("(LOGIN) ##### END-CHECK = Setting(freeonly) : {0} #####".format(str(addon.getSetting("freeonly"))))
				debug_MS("(LOGIN) <<<<< Ende LOGIN <<<<<")
				return 3,persToken
			else:
				debug_MS("(LOGIN) ##### Free-Member = Your Free-Account is OK #####")
				addon.setSetting('freeonly', 'true')
				addon.setSetting('high_definition', 'false')
				debug_MS("(LOGIN) ##### END-CHECK = Setting(freeonly) : {0} #####".format(str(addon.getSetting("freeonly"))))
				debug_MS("(LOGIN) <<<<< Ende LOGIN <<<<<")
				return 2,persToken
		else:
			failing("(LOGIN) ##### persToken-THIRD : Token NICHT gefunden !!! #####")
			addon.setSetting('freeonly', 'true')
			addon.setSetting('high_definition', 'false')
			debug_MS("(LOGIN) ##### END-CHECK = Setting(freeonly) : {0} #####".format(str(addon.getSetting("freeonly"))))
			debug_MS("(LOGIN) <<<<< Ende LOGIN <<<<<")
			return 0,'0'
	except:
		failing("(LOGIN) ##### Fehler - Fehler - Fehler : KEIN Login möglich !!! #####")
		addon.setSetting('freeonly', 'true')
		addon.setSetting('high_definition', 'false')
		debug_MS("(LOGIN) ##### END-CHECK = Setting(freeonly) : {0} #####".format(str(addon.getSetting("freeonly"))))
		debug_MS("(LOGIN) <<<<< Ende LOGIN <<<<<")
		return 0,'0'

def listStations():
	debug_MS("(listStations) -------------------------------------------------- START = listStations --------------------------------------------------")
	content = makeREQUEST('https://api.tvnow.de/v3/settings')
	settings = json.loads(content, object_pairs_hook=OrderedDict)
	aliases = settings['settings']['nowtv']['local']['stations']['aliases']
	for name, value in aliases.items():
		debug_MS("(listStations) ### STATION = {0} || URL = {1} || LOGO = {2} ###".format(str(value), str(name), str(artpic+name+'.png')))
		addDir(value, name, 'listSeries', artpic+name+'.png')
	xbmcplugin.endOfDirectory(pluginhandle)

def listThemes(url):
	debug_MS("(listThemes) -------------------------------------------------- START = listThemes --------------------------------------------------")
	#https://api.tvnow.de/v3/channels/station/rtl?fields=*&filter=%7B%22Active%22:true%7D&maxPerPage=500&page=1
	newURL = 'https://api.tvnow.de/v3/channels/station/'+url+'?fields=*&filter=%7B%22Active%22:true%7D&maxPerPage=500'
	content = makeREQUEST(newURL)
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	for themeITEM in DATA['items']:
		themeID = str(themeITEM['id'])
		name = py2_enc(themeITEM['title']).strip()
		logo = 'https://aistvnow-a.akamaihd.net/tvnow/cms/'+themeITEM['portraitImage']+'/image.jpg'
		debug_MS("(listThemes) ### IDD = {0} || NAME = {1} || PHOTO = {2} ###".format(themeID, name, logo))
		addDir(name, themeID, 'subThemes', logo)
	xbmcplugin.endOfDirectory(pluginhandle)

def listTopics():
	debug_MS("(listTopics) -------------------------------------------------- START = listTopics --------------------------------------------------")
	UN_Supported = ['2204', '2255', '7619', '10143', '10567', '11379'] # these lists are empty or not compatible
	content = makeREQUEST('https://api.tvnow.de/v3/pages/nowtv/tvnow?fields=teaserSets.headline,teaserSets.id')
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	for topicITEM in DATA['teaserSets']['items']:
		topicID = str(topicITEM['id'])
		name = py2_enc(topicITEM['headline']).strip()
		debug_MS("(listTopics) ### IDD = {0} || NAME = {1} ###".format(topicID, name))
		if not any(x in topicID for x in UN_Supported):
			addDir(name , topicID, 'subTopics', icon)
	xbmcplugin.endOfDirectory(pluginhandle)

def subTopics(Xidd):
	debug_MS("(subTopics) -------------------------------------------------- START = subTopics --------------------------------------------------")
	xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
	UNIKAT = set()
	content = makeREQUEST('https://api.tvnow.de/v3/teasersets/'+Xidd+'?fields=[%22teaserSetInformations%22,[%22format%22,[%22id%22,%22title%22,%22formatimageArtwork%22,%22defaultImage169Logo%22,%22defaultDvdImage%22,%22infoTextLong%22,%22infoText%22]]]')
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	for subITEM in DATA['teaserSetInformations']['items']:
		if subITEM['format'] != None:
			debug_MS("(subTopics) ##### subITEM : {0} #####".format(str(subITEM)))
			subID = str(subITEM['format']['id'])
			if subID in UNIKAT:
				continue
			UNIKAT.add(subID)
			name = py2_enc(subITEM['format']['title']).strip()
			logo = ""
			if 'defaultDvdImage' in subITEM['format'] and subITEM['format']['defaultDvdImage'] != "" and subITEM['format']['defaultDvdImage'] != None:
				logo = cleanPhoto(subITEM['format']['defaultDvdImage'])
			if logo == "" and 'formatimageArtwork' in subITEM['format'] and subITEM['format']['formatimageArtwork'] != "" and subITEM['format']['formatimageArtwork'] != None:
				logo = cleanPhoto(subITEM['format']['formatimageArtwork'])
			if logo == "" and 'defaultImage169Logo' in subITEM['format'] and subITEM['format']['defaultImage169Logo'] != "" and subITEM['format']['defaultImage169Logo'] != None:
				logo = cleanPhoto(subITEM['format']['defaultImage169Logo'])
			plot = ""
			if 'infoTextLong' in subITEM['format'] and subITEM['format']['infoTextLong'] != "" and subITEM['format']['infoTextLong'] != None:
				plot = py2_enc(subITEM['format']['infoTextLong']).strip()
			if plot == "" and 'infoText' in subITEM['format'] and subITEM['format']['infoText'] != "" and subITEM['format']['infoText'] != None:
				plot = py2_enc(subITEM['format']['infoText']).strip()
			debug_MS("(subTopics) ### subID = {0} || NAME = {1} || PHOTO = {2} ###".format(subID, name, logo))
			addDir(name, subID, 'listSeasons', logo, plot, origSERIE=name)
	xbmcplugin.endOfDirectory(pluginhandle)

def listGenres():
	debug_MS("(listGenres) -------------------------------------------------- START = listGenres --------------------------------------------------")
	xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
	content = makeREQUEST('https://cdn.static-fra.de/tvnow/app/e81664b7.main.js')
	liste = re.compile('return\[([^\]]+?)\]\}return', re.DOTALL).findall(content)[0]
	elements = liste.replace('"', '').split(',')
	for genreITEM in elements:
		newURL = 'https://api.tvnow.de/v3/formats/genre/'+quote_plus(genreITEM.lower())+'?fields=*&filter=%7B%22station%22:%22none%22%7D&maxPerPage=500&order=NameLong+asc'
		debug_MS("(listGenres) ### genreITEM = {0} || newURL = {1} ###".format(str(genreITEM), str(newURL)))
		addDir(genreITEM, newURL, 'is_Serie', icon)
	xbmcplugin.endOfDirectory(pluginhandle)

def getSearch(url, limit, default="", heading='Suche nach...', hidden=False):
	debug_MS("(getSearch) ### LIMIT : {0} ###".format(str(limit)))
	limit = int(limit)
	if limit == 1:
		keyboard = xbmc.Keyboard(default, heading, hidden)
		keyboard.doModal()
		if keyboard.isConfirmed() and keyboard.getText():
			limit += 1
			word = py2_enc(keyboard.getText())
			return listSearch(word, limit)
		else: return default
	return default

def listSearch(word, limit):
	debug_MS("(listSearch) -------------------------------------------------- START = Searching --------------------------------------------------")
	debug_MS("(listSearch) ### WORD : {0} ### LIMIT : {1} ###".format(word, str(limit)))
	xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
	url = 'https://api.tvnow.de/v3/formats?fields=id,title,station,hasFreeEpisodes,seoUrl,formatimageArtwork,formatimageMoviecover169,genre1,categoryId,searchAliasName,metaTags,infoText,infoTextLong&maxPerPage=500'
	#url = 'https://api.tvnow.de/v3/formats?fields=*,id,title,station,metaTags,searchAliasName,seoUrl,defaultDvdImage,formatimageArtwork,infoText,infoTextLong&maxPerPage=5000'
	limit = int(limit)
	pageNUMBER = 1
	position = 1
	total = 1
	while (total > 0) and limit < 3:
		newURL = url+'&page='+str(pageNUMBER)
		debug_MS("(listSearch) ### newURL : {0} ###".format(newURL))
		content = makeREQUEST(newURL)
		DATA = json.loads(content, object_pairs_hook=OrderedDict)
		for foundITEM in DATA['items']:
			COMBIstring = py2_enc(foundITEM['metaTags'].lower().replace('video,', '').replace('videos,', '').replace('online sehen,', '').replace('internet tv,', '').replace('fernsehen,', '').replace('video on demand,', '').replace('tv now,', ''))
			COMBIstring += py2_enc(foundITEM['searchAliasName'].lower().replace(';', ','))
			COMBIstring += py2_enc(foundITEM['title'].lower())
			searchID = str(foundITEM['id'])
			title = py2_enc(foundITEM['title']).strip()
			station = foundITEM['station'].upper()
			seoUrl = foundITEM['seoUrl']
			logo = ""
			if 'formatimageArtwork' in foundITEM and foundITEM['formatimageArtwork'] != "" and foundITEM['formatimageArtwork'] != None:
				logo = cleanPhoto(foundITEM['formatimageArtwork'])
			if logo == "" and 'formatimageMoviecover169' in foundITEM and foundITEM['formatimageMoviecover169'] != "" and foundITEM['formatimageMoviecover169'] != None:
				logo = cleanPhoto(foundITEM['formatimageMoviecover169'])
			if logo == "": logo = 'https://aistvnow-a.akamaihd.net/tvnow/format/'+searchID+'_02logo/image.jpg'
			genre = py2_enc(foundITEM['genre1']).strip()
			category = foundITEM['categoryId']
			plot = ""
			if 'infoTextLong' in foundITEM and foundITEM['infoTextLong'] != "" and foundITEM['infoTextLong'] != None:
				plot = py2_enc(foundITEM['infoTextLong']).strip()
			if plot == "" and 'infoText' in foundITEM and foundITEM['infoText'] != "" and foundITEM['infoText'] != None:
				plot = py2_enc(foundITEM['infoText']).strip()
			freeEP = foundITEM['hasFreeEpisodes']
			addType=1
			if os.path.exists(channelFavsFile):
				with open(channelFavsFile, 'r') as output:
					lines = output.readlines()
					for line in lines:
						if line.startswith('###START'):
							part = line.split('###')
							if searchID == part[2]: addType=2
			if category == 'film':
				addType=3
				if markMOVIES: name = '[I]'+name+'[/I]'
			if word.lower() in str(COMBIstring):
				debug_MS("(listSearch) ### Found in SEARCH = TITLE : {0} ###".format(title))
				debug_MS("(listSearch) ### Found in SEARCH = STRING : {0} ###".format(str(COMBIstring)))
				addDir(title, searchID, 'listSeasons', logo, plot, origSERIE=title, genre=genre, studio=station, addType=addType)
			position += 1
		debug_MS("(listSearch) Anzahl-in-Liste : {0}".format(str(int(position)-1)))
		try:
			debug_MS("(listSearch) Anzahl-auf-Webseite : {0}".format(str(DATA['total'])))
			total = DATA['total'] - position
		except: total = 0
		pageNUMBER += 1
	xbmcplugin.endOfDirectory(pluginhandle)

def liveTV():
	debug_MS("(liveTV) -------------------------------------------------- START = liveTV --------------------------------------------------")
	STATUS,TOKEN = LOGIN()
	if freeonly=='true' and STATUS < 3:
		failing("(liveTV) ##### Sie haben KEINE Berechtigung : Für LIVE-TV ist ein Premium-Account Voraussetzung !!! #####")
		return xbmcgui.Dialog().notification('KEINE Berechtigung', translation(30532), icon, 8000)
	content = getUrl('https://api.tvnow.de/v3/epgs/movies/nownext?fields=*,nowNextEpgTeasers.*,nowNextEpgMovies.*') 
	DATA = json.loads(content, object_pairs_hook=OrderedDict)
	for channelITEM in DATA['items']:
		debug_MS("(liveTV) ##### channelITEM : {0} #####".format(str(channelITEM)))
		short = channelITEM['nowNextEpgMovies']['items'][0]
		station = py2_enc(channelITEM['name']).upper()
		liveID = str(short['id'])
		title = py2_enc(short['title']).strip()
		subTitle = py2_enc(short['subTitle']).strip()
		if subTitle != "": title = '{0} - {1}'.format(title, subTitle)
		startDT = datetime(*(time.strptime(short['startDate'][:19], '%Y{0}%m{0}%d %H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2019-06-02 11:40:00
		START = startDT.strftime('{0}%H{1}%M').format('(', ':')
		endDT = datetime(*(time.strptime(short['endDate'][:19], '%Y{0}%m{0}%d %H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2019-06-02 11:40:00
		END = endDT.strftime(' {0} %H{1}%M{2}').format('-', ':', ')')
		normSD = short['manifest']['dash']
		highHD = short['manifest']['dashhd']
		image = 'https://aistvnow-a.akamaihd.net/tvnow/epg/'+liveID+'/960x0/image.jpg'
		plot = '[COLOR orangered]bis '+END.replace('-', '').replace(')', '').strip()+' Uhr[/COLOR]'
		if 'total' in channelITEM['nowNextEpgMovies'] and str(channelITEM['nowNextEpgMovies']['total']) == '2':
			shorten = channelITEM['nowNextEpgMovies']['items'][1]
			title_2 = py2_enc(shorten['title']).strip()
			subTitle_2 = py2_enc(shorten['subTitle']).strip()
			if subTitle_2 != "": title_2 = '{0} - {1}'.format(title_2, subTitle_2)
			startDT_2 = datetime(*(time.strptime(shorten['startDate'][:19], '%Y{0}%m{0}%d %H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2019-06-02 11:40:00
			START_2 = startDT_2.strftime('%H{0}%M').format(':')
			endDT_2 = datetime(*(time.strptime(shorten['endDate'][:19], '%Y{0}%m{0}%d %H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2019-06-02 11:40:00
			END_2 = endDT_2.strftime(' {0} %H{1}%M').format('-', ':')
			plot += '[CR][CR]Danach:[CR][COLOR yellow]{0}[/COLOR]'.format(title_2)
			plot += '[CR][COLOR yellow]{0}[/COLOR]'.format(START_2+END_2)
		name = '[COLOR lime]{0}:  [/COLOR]{1}  {2}'.format(station, title, START+END)
		vidURL = normSD
		if selectionHD: vidURL = highHD
		listitem = xbmcgui.ListItem(name, path=vidURL)
		listitem.setInfo(type='Video', infoLabels={'Title': name, 'Plot': plot, 'Studio': station})
		listitem.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': image})
		xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sys.argv[0]+'?mode=playChannel&url='+quote_plus(vidURL)+'&name='+str(name)+'&image='+str(image), listitem=listitem)
	xbmcplugin.endOfDirectory(pluginhandle, succeeded=True, updateListing=True, cacheToDisc=False)

def playChannel(url, Xtitle, Xbild):
	STATUS,TOKEN = LOGIN()
	station = Xtitle.replace('[COLOR lime]', '').split(':')[0]
	referer = 'https://www.tvnow.de/live-tv/'+station.lower()
	userAgent = 'User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0&Referer='+referer
	listitem = xbmcgui.ListItem(path=url+'|'+userAgent)
	debug_MS("(playChannel) PATH : {0}".format(str(url+'|'+userAgent)))
	listitem.setInfo(type='Video', infoLabels={'Title': Xtitle, 'Studio': station})
	listitem.setArt({'icon': icon, 'thumb': Xbild, 'poster': Xbild, 'fanart': Xbild})
	listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
	listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
	listitem.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
	licstring = 'https://widevine.tvnow.de/index/proxy|'+userAgent+'&x-auth-token='+TOKEN+'&content-type=text/html|R{SSM}|'
	listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')	
	listitem.setProperty('inputstream.adaptive.license_key', licstring)
	debug_MS("(playChannel) LICENSE : {0}".format(str(licstring)))
	xbmc.Player().play(item=url, listitem=listitem)

def playCODE(IDD):
	debug_MS("(playCODE) -------------------------------------------------- START = playCODE --------------------------------------------------")
	with open(WORKFILE, 'r') as output:
		lines = output.readlines()
		for line in lines:
			field = line.split('@@')
			if field[0]==IDD:
				finalURL = field[1]
				seriesname = field[2]
				title2 = field[3]
				photo = field[4]
				duration = field[5]
				season = field[6]
				episode = field[7]
				deeplink = field[8]
				DRM = field[9]
				token = field[10]
				pay = field[11]
	if IDD != '0' and finalURL != '0':
		debug_MS("--------------------------------------------------------------------------- Gefunden ---------------------------------------------------------------------------------")
		debug_MS("(playCODE) ### STREAM : {0} ###".format(finalURL))
		debug_MS("(playCODE) ### TOKEN : {0} ###".format(token))
		debug_MS("(playCODE) ### DRM : {0} ###".format(DRM))
		debug_MS("(playCODE) ### PAY : {0} ###".format(pay))
		userAgent = 'User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0'
		if deeplink != "": userAgent = userAgent+'&Referer='+deeplink
		listitem = xbmcgui.ListItem(path=finalURL+'|'+userAgent)
		log("(playCODE) finalURL : {0}".format(str(finalURL+'|'+userAgent)))
		listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
		listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
		#listitem.setProperty('inputstream.adaptive.manifest_update_parameter', 'full')
		if KODI_18 and DRM == 'True':
			if token == '0':
				failing("(playCODE) ##### persToken : Der erforderliche Token wurde NICHT gefunden !!! #####")
				xbmcgui.Dialog().notification('ERROR - Token_02 - ERROR', translation(30528), icon, 12000)
			else:
				licstring = 'https://widevine.tvnow.de/index/proxy|'+userAgent+'&x-auth-token='+token+'&content-type=text/html|R{SSM}|'
				listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
				listitem.setProperty('inputstream.adaptive.license_key', licstring)
				debug_MS("(playCODE) LICENSE : {0}".format(str(licstring)))
		elif not KODI_18 and DRM == 'True':
			failing("(playCODE) ##### ACHTUNG : ... Für diese Sendung ist mindestens *KODI 18* erforderlich !!!\nBitte die vorhandene KODI-Installation mindestens auf KODI-Version 18 updaten !!! #####")
			return xbmcgui.Dialog().ok(addon.getAddonInfo('id'), translation(30504))
		xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
	else:
		if DRM == 'True' and not KODI_18 and token == '0':
			failing("(playCODE) KEIN Token ##### ACHTUNG : ... Für diese Sendung ist mindestens *KODI 18* erforderlich !!!\nBitte die vorhandene KODI-Installation mindestens auf KODI-Version 18 updaten !!! #####")
			return xbmcgui.Dialog().ok(addon.getAddonInfo('id'), translation(30504))
		elif pay == 'False' and token.startswith('C3'):
			failing("(playCODE) ##### Sie haben KEINE Berechtigung : Für dieses Video ist ein Premium-Account Voraussetzung !!! #####")
			return xbmcgui.Dialog().notification('KEINE Berechtigung', translation(30530), icon, 8000)
		else:
			failing("(playCODE) ##### Die angeforderte Video-Url wurde leider NICHT gefunden !!! #####")
			return xbmcgui.Dialog().notification('KEIN Video gefunden', translation(30531), icon, 8000)

def playDash(*args):
	debug_MS("(playDash) -------------------------------------------------- START = playDash --------------------------------------------------")
	STATUS,TOKEN = LOGIN()
	streamURL = False
	FOUND = 0
	userAgent = 'User-Agent=Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0'
	if xlink != "": userAgent = userAgent+'&Referer='+xlink
	if (KODI_18 or KODI_17) and xnormSD != "" and xhighHD != "" and xdrm != "" and xstat != "":
		if not KODI_18 and xdrm == '1':
			failing("(playDash) no.1 ##### ACHTUNG : ... Für diese Sendung ist mindestens *KODI 18* erforderlich !!!\nBitte die vorhandene KODI-Installation mindestens auf KODI-Version 18 updaten !!! #####")
			return xbmcgui.Dialog().ok(addon.getAddonInfo('id'), translation(30504))
		if (freeonly == 'false' and STATUS == 3 and selectionHD and TOKEN != '0'):
			streamURL = xhighHD
			FOUND = 1
		elif (freeonly == 'false' and STATUS == 3 and not selectionHD and TOKEN != '0') or (freeonly == 'true' and TOKEN != '0' and xdrm == '1' and xstat == 'True') or (freeonly == 'true' and xdrm == '0' and xstat == 'True'):
			streamURL = xnormSD
			FOUND = 1
		else:
			failing("(playDash) ##### Sie haben KEINE Berechtigung : Für dieses Video ist ein Premium-Account Voraussetzung !!! #####")
			return xbmcgui.Dialog().ok(addon.getAddonInfo('id'), translation(30505))
	elif not KODI_18 and not KODI_17:
		failing("(playDash) no.2 ##### ACHTUNG : ... Für diese Sendung ist mindestens *KODI 18* erforderlich !!!\nBitte die vorhandene KODI-Installation mindestens auf KODI-Version 18 updaten !!! #####")
		return xbmcgui.Dialog().ok(addon.getAddonInfo('id'), translation(30504))
	if FOUND == 1 and streamURL:
		listitem = xbmcgui.ListItem(path=streamURL+'|'+userAgent)
		log("(playDash) streamURL : {0}".format(str(streamURL+'|'+userAgent)))
		listitem.setProperty('IsPlayable', 'true')
		listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
		listitem.setProperty('inputstream.adaptive.manifest_type', 'mpd')
		if KODI_18 and xdrm == '1':
			licstring = 'https://widevine.tvnow.de/index/proxy|'+userAgent+'&x-auth-token='+TOKEN+'&content-type=text/html|R{SSM}|'
			listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
			listitem.setProperty('inputstream.adaptive.license_key', licstring)
			debug_MS("(playDash) LICENSE : {0}".format(str(licstring)))
		xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
	else:
		failing("(playDash) ##### Der übertragene *Dash-Abspiel-Link* ist leider FEHLERHAFT !!! #####")
		return xbmcgui.Dialog().notification(translation(30521).format('DASH - URL'), translation(30529), icon, 8000)

def listShowsFavs():
	debug_MS("(listShowsFavs) -------------------------------------------------- START = listShowsFavs --------------------------------------------------")
	xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
	if os.path.exists(channelFavsFile):
		with open(channelFavsFile, 'r') as textobj:
			lines = textobj.readlines()
			for line in lines:
				if line.startswith('###START'):
					part = line.split('###')
					addDir(name=part[3], url=part[2], mode='listSeasons', image=cleanPhoto(part[4]), plot=part[5].replace('#n#', '\n').strip(), origSERIE=part[3], FAVdel=True)
					debug_MS("(listShowsFavs) ### TITLE = {0} || IDD = {1} || PHOTO = {2} ###".format(str(part[3]), str(part[2]), cleanPhoto(part[4])))
	xbmcplugin.endOfDirectory(pluginhandle)

def favs(param):
	mode = param[param.find('MODE=')+5:+8]
	TVSe = param[param.find('###START'):]
	TVSe = TVSe[:TVSe.find('END###')]
	url = TVSe.split('###')[2]
	name = TVSe.split('###')[3]
	if mode == 'ADD':
		if os.path.exists(channelFavsFile):
			with open(channelFavsFile, 'a+') as textobj:
				content = textobj.read()
				if content.find(TVSe) == -1:
					textobj.seek(0,2) # change is here (for Windows-Error = "IOError: [Errno 0] Error") - because Windows don't like switching between reading and writing at same time !!!
					textobj.write(TVSe+'END###\n')
		else:
			with open(channelFavsFile, 'a') as textobj:
				textobj.write(TVSe+'END###\n')
		xbmc.sleep(500)
		xbmcgui.Dialog().notification(translation(30533), translation(30534).format(name), icon, 8000)
	elif mode == 'DEL':
		with open(channelFavsFile, 'r') as output:
			lines = output.readlines()
		with open(channelFavsFile, 'w') as input:
			for line in lines:
				if url not in line:
					input.write(line)
		xbmc.executebuiltin('Container.Refresh')
		xbmc.sleep(1000)
		xbmcgui.Dialog().notification(translation(30533), translation(30535).format(name), icon, 8000)

def tolibrary(vid):
	debug_MS("(tolibrary) -------------------------------------------------- START = tolibrary --------------------------------------------------")
	if mediaPath =="":
		xbmcgui.Dialog().ok(addon.getAddonInfo('id'), translation(30507))
	elif mediaPath !="" and ADDON_operate('service.cron.autobiblio'):
		LIBe = vid[vid.find('###START'):]
		LIBe = LIBe[:LIBe.find('END###')]
		url = LIBe.split('###')[2]
		name = LIBe.split('###')[3]
		stunden = LIBe.split('###')[4]
		title = name
		if '@@' in url:
			title += '  ('+url.split('@@')[1]+')'
			addYear = url.split('@@')[1]
			newSOURCE = quote_plus(mediaPath+fixPathSymbols(name)+os.sep+addYear)
		else:
			title += '  (Serie)'
			newSOURCE = quote_plus(mediaPath+fixPathSymbols(name))
		newURL = '{0}?mode=generatefiles&url={1}&name={2}'.format(sys.argv[0], url, quote_plus(name))
		newURL = quote_plus(newURL)
		newNAME = quote_plus(name)
		debug_MS("(tolibrary) ### newNAME : {0} ###".format(str(newNAME)))
		debug_MS("(tolibrary) ### newURL : {0} ###".format(str(newURL)))
		debug_MS("(tolibrary) ### newSOURCE : {0} ###".format(str(newSOURCE)))
		xbmc.executebuiltin('RunPlugin(plugin://service.cron.autobiblio/?mode=adddata&name={0}&stunden={1}&url={2}&source={3})'.format(newNAME, stunden, newURL, newSOURCE))
		xbmcgui.Dialog().notification(translation(30536), translation(30537).format(title, str(stunden)), icon, 15000)

def generatefiles(*args):
	from threading import Thread
	debug_MS("(generatefiles) -------------------------------------------------- START = generatefiles --------------------------------------------------")
	threads = []
	th = Thread(target=LIBRARY_Worker, args=(args))
	if hasattr(th, 'daemon'): th.daemon = True
	else: th.setDaemon()
	threads.append(th)
	for th in threads: th.start()

def LIBRARY_Worker(BroadCast_Idd, BroadCast_Name):
	debug_MS("(LIBRARY_Worker) ### BroadCast_Idd = {0} ### BroadCast_Name = {1} ###".format(BroadCast_Idd, BroadCast_Name))
	if not enableLibrary or mediaPath =="":
		return
	STATUS,TOKEN = LOGIN()
	COMBINATION = []
	pos = 0
	elem_IDD = BroadCast_Idd
	if '@@' in BroadCast_Idd: elem_IDD = BroadCast_Idd.split('@@')[0]
	url_1 = 'http://api.tvnow.de/v3/formats/'+str(elem_IDD)+'?fields='+quote_plus('*,.*,formatTabs.*,formatTabs.headline,annualNavigation.*')
	debug_MS("(LIBRARY_Worker) ##### URL-01 : {0} #####".format(str(url_1)))
	TVS_Path = os.path.join(py2_uni(mediaPath), py2_uni(fixPathSymbols(BroadCast_Name)))
	if '@@' in BroadCast_Idd: 
		yearPath = BroadCast_Idd.split('@@')[1]
		EP_Path = os.path.join(py2_uni(mediaPath), py2_uni(fixPathSymbols(BroadCast_Name)), str(yearPath))
	else:
		EP_Path = os.path.join(py2_uni(mediaPath), py2_uni(fixPathSymbols(BroadCast_Name)))
	debug_MS("(LIBRARY_Worker) ### EP_Path = {0} ###".format(str(EP_Path)))
	if os.path.isdir(EP_Path):
		shutil.rmtree(EP_Path, ignore_errors=True)
		xbmc.sleep(500)
	if xbmcvfs.exists(os.path.join(TVS_Path, 'tvshow.nfo')):
		xbmcvfs.delete(os.path.join(TVS_Path, 'tvshow.nfo'))
		xbmc.sleep(500)
	os.makedirs(EP_Path)
	try:
		content_1 = getUrl(url_1)
		FIRST = json.loads(content_1, object_pairs_hook=OrderedDict)
		TVS_name = py2_enc(FIRST['title']).strip()
	except:
		return
	SERIES_IDD = str(FIRST['id'])
	TVS_studio = ""
	if 'station' in FIRST and FIRST['station'] != "" and FIRST['station'] != None: TVS_studio = FIRST['station'].upper()
	TVS_image = ""
	if 'defaultImage169Format' in FIRST and FIRST['defaultImage169Format'] != "" and FIRST['defaultImage169Format'] != None:
		TVS_image = cleanPhoto(FIRST['defaultImage169Format'])
	if TVS_image == "" and 'formatimageArtwork' in FIRST and FIRST['formatimageArtwork'] != "" and FIRST['formatimageArtwork'] != None:
		TVS_image = cleanPhoto(FIRST['formatimageArtwork'])
	if TVS_image == "": TVS_image = 'https://aistvnow-a.akamaihd.net/tvnow/format/'+SERIES_IDD+'_02logo/image.jpg'
	TVS_plot = ""
	if 'infoTextLong' in FIRST and FIRST['infoTextLong'] != "" and FIRST['infoTextLong'] != None:
		TVS_plot = py2_enc(FIRST['infoTextLong']).replace('\n\n\n', '\n\n').strip()
	if TVS_plot == "" and 'infoText' in FIRST and FIRST['infoText'] != "" and FIRST['infoText'] != None:
		TVS_plot = py2_enc(FIRST['infoText']).replace('\n\n\n', '\n\n').strip()
	TVS_airdate = ""
	if 'onlineDate' in FIRST and FIRST['onlineDate'] != "" and FIRST['onlineDate'] != None:
		TVS_airdate = FIRST['onlineDate'][:10]
	pageNUMBER = 1
	position = 1
	total = 1
	if '@@' in BroadCast_Idd:
		elem_YEAR = BroadCast_Idd.split('@@')[1]
		url_2 = 'https://api.tvnow.de/v3/movies?fields=*,format,paymentPaytypes,pictures,trailers&filter={%22BroadcastStartDate%22:{%22between%22:{%22start%22:%22'+elem_YEAR+'-01-01%2000:00:00%22,%22end%22:%20%22'+elem_YEAR+'-12-31%2023:59:59%22}},%20%22FormatId%22%20:%20'+SERIES_IDD+'}&maxPerPage=200'
	else:
		url_2 = 'https://api.tvnow.de/v3/movies?fields=*,format,paymentPaytypes,pictures,trailers&filter={%20%22FormatId%22%20:%20'+SERIES_IDD+'}&maxPerPage=200'
	debug_MS("(LIBRARY_Worker) ##### URL-02 : {0} #####".format(str(url_2)))
	while (total > 0):  
		newURL = url_2+'&page='+str(pageNUMBER)
		debug_MS("(LIBRARY_Worker) ### newURL : {0} ###".format(newURL))
		content = getUrl(newURL)
		DATA = json.loads(content, object_pairs_hook=OrderedDict)
		if 'formatTabPages' in DATA and 'items' in str(DATA['formatTabPages']):
			for each in DATA['formatTabPages']['items']:
				items = each['container']['movies']['items']
		elif not 'formatTabPages' in DATA and 'movies' in DATA and 'items' in str(DATA['movies']):
			items = DATA['movies']['items']
		else: items = DATA['items']
		for vid in items:
			debug_MS("(LIBRARY_Worker) ##### VIDEO-Item : {0} #####".format(str(vid)))
			try: debug_MS(str(vid['isDrm']))
			except: continue
			TVS_title = ""
			try: TVS_title = py2_enc(vid['format']['title']).strip()
			except: 
				try: TVS_title = py2_enc(vid['format']['seoUrl']).replace('-', ' ').title().strip()
				except: continue
			spezTIMES = None
			normTIMES = None
			try:
				broadcast = datetime(*(time.strptime(vid['broadcastStartDate'][:19], '%Y{0}%m{0}%d %H{1}%M{1}%S'.format('-', ':'))[0:6])) # 2019-06-02 11:40:00
				spezTIMES = broadcast.strftime('%a{0} %d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':').replace('Mon', translation(30621)).replace('Tue', translation(30622)).replace('Wed', translation(30623)).replace('Thu', translation(30624)).replace('Fri', translation(30625)).replace('Sat', translation(30626)).replace('Sun', translation(30627))
				normTIMES = broadcast.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
			except: pass
			EP_idd = ""
			if 'id' in vid and vid['id'] != "" and vid['id'] != None:
				EP_idd = str(vid['id'])
			else: continue
			EP_title1 = py2_enc(vid['title']).strip()
			pos += 1
			EP_season = '00'
			if 'season' in vid and vid['season'] != "" and str(vid['season']) != "0" and vid['season'] != None:
				EP_season = str(vid['season']).zfill(2)
			EP_episode = ""
			if 'episode' in vid and vid['episode'] != "" and str(vid['episode']) != "0" and vid['episode'] != None:
				EP_episode = str(vid['episode']).replace('P', '').zfill(2)
			EP_duration = ""
			if 'duration' in vid and vid['duration'] !="" and vid['duration'] != None: EP_duration = get_min(vid['duration'])
			EP_tagline = ""
			if 'teaserText' in vid and vid['teaserText'] !="" and vid['teaserText'] != None:
				EP_tagline = py2_enc(vid['teaserText']).strip()
			EP_plot = ""
			if 'articleLong' in vid and vid['articleLong'] !="" and vid['articleLong'] != None:
				EP_plot = py2_enc(vid['articleLong']).replace('\n\n\n', '\n\n').strip()
			if EP_plot =="" and 'articleShort' in vid and vid['articleShort'] !="" and vid['articleShort'] != None:
				EP_plot = py2_enc(vid['articleShort']).replace('\n\n\n', '\n\n').strip()
			Note_1 =""
			Note_2 =""
			Note_3 =""
			Note_4 =""
			Note_5 =""
			Note_6 =""
			if TVS_title !="": Note_1 = TVS_title
			if EP_season != '00' and EP_episode != "": Note_3 = translation(30628).format(EP_season, EP_episode)
			if spezTIMES: Note_4 = translation(30629).format(str(spezTIMES))
			EP_fsk = ""
			if 'fsk' in vid and vid['fsk'] != "" and str(vid['fsk']) != '0' and vid['fsk'] != None:
				EP_fsk = translation(30630).format(str(vid['fsk']))
			EP_yeardate = ""
			if 'productionYear' in vid and vid['productionYear'] != "" and str(vid['productionYear']) != '0' and vid['productionYear'] != None:
				EP_yeardate = vid['productionYear']
			if showDATE and normTIMES:
				Note_5 = translation(30631).format(str(normTIMES))
			PayType = True
			if 'payed' in vid and str(vid['payed']) !="" and vid['payed'] != None: PayType = vid['payed']
			videoHD = ""
			if 'manifest' in vid and 'dashhd' in vid['manifest'] and vid['manifest']['dashhd'] !="": # HD-Play
				videoHD = vid['manifest']['dashhd'].split('.mpd')[0]+'.mpd'
			videoFREE = ""
			if 'manifest' in vid and 'dash' in vid['manifest'] and vid['manifest']['dash'] !="": # Normal-Play
				videoFREE = vid['manifest']['dash'].split('.mpd')[0]+'.mpd'
			try: EP_deeplink = 'https://www.tvnow.de/'+vid['format']['formatType'].replace('show', 'shows').replace('serie', 'serien').replace('film', 'filme')+'/'+py2_enc(vid['format']['seoUrl'])+'-'+str(vid['format']['id'])
			except: EP_deeplink =""
			EP_image = 'https://aistvnow-a.akamaihd.net/tvnow/movie/'+EP_idd+'/1200x0/image.jpg'
			EP_studio = ""
			if 'format' in vid and 'station' in vid['format'] and vid['format']['station'] != "" and vid['format']['station'] != None:
				EP_studio = vid['format']['station'].upper()
			genreList=[]
			if 'format' in vid and 'genres' in vid['format'] and vid['format']['genres'] != "" and vid['format']['genres'] != None:
				for item in vid['format']['genres']:
					gNames = py2_enc(item)
					genreList.append(gNames)
			try: EP_genre1 = genreList[0]
			except: EP_genre1 = ""
			try: EP_genre2 = genreList[1]
			except: EP_genre2 = ""
			try: EP_genre3 = genreList[2]
			except: EP_genre3 = ""
			EP_protected = '0'
			if 'isDrm' in vid and vid['isDrm'] == True: EP_protected = '1'
			if (not KODI_18 and vid['isDrm'] == True and PayType == False):
				Note_2 = '   [COLOR skyblue](premium|[/COLOR][COLOR orangered]DRM)[/COLOR]'
				Note_6 = '     [COLOR deepskyblue](premium|[/COLOR][COLOR orangered]DRM)[/COLOR]'
			elif (not KODI_18 and vid['isDrm'] == True and PayType == True):
				Note_2 = '   [COLOR orangered](DRM)[/COLOR]'
				Note_6 = '     [COLOR orangered](DRM)[/COLOR]'
			elif (KODI_17 or KODI_18) and PayType == False and STATUS < 3:
				Note_2 = '   [COLOR skyblue](premium)[/COLOR]'
				Note_6 = '     [COLOR deepskyblue](premium)[/COLOR]'
			EP_plot = Note_1+Note_2+'[CR]'+Note_3+Note_4+'[CR][CR]'+EP_plot
			EP_title_long = EP_title1+Note_5+Note_6
			try: EP_airdate = vid['broadcastStartDate'][:10]
			except: EP_airdate = vid['broadcastPreviewStartDate'][:10]
			if EP_season != '00' and EP_episode != "":
				EP_title = 'S'+EP_season+'E'+EP_episode+'_'+EP_title1
			else:
				EP_episode = str(pos).zfill(2)
				EP_title = 'S00E'+EP_episode+'_'+EP_title1
			EP_nosub = '&xnormSD='+str(videoFREE)+'&xhighHD='+str(videoHD)+'&xlink='+str(EP_deeplink)+'&xdrm='+EP_protected+'&xstat='+str(PayType)
			episodeFILE = py2_uni(fixPathSymbols(EP_title))
			COMBINATION.append([episodeFILE, EP_title_long, TVS_title, EP_idd, EP_season, EP_episode, EP_plot, EP_tagline, EP_duration, EP_image, EP_fsk, EP_genre1, EP_genre2, EP_genre3, EP_yeardate, EP_airdate, EP_studio, EP_nosub])
			position += 1
		debug_MS("(LIBRARY_Worker) Anzahl-in-Liste : {0}".format(str(int(position)-1)))
		try:
			debug_MS("(LIBRARY_Worker) Anzahl-auf-Webseite : {0}".format(str(DATA['total'])))
			total = DATA['total'] - position
		except: total = 0
		pageNUMBER += 1
	for episodeFILE, EP_title_long, TVS_title, EP_idd, EP_season, EP_episode, EP_plot, EP_tagline, EP_duration, EP_image, EP_fsk, EP_genre1, EP_genre2, EP_genre3, EP_yeardate, EP_airdate, EP_studio, EP_nosub in COMBINATION:
		nfo_EPISODE_string = os.path.join(EP_Path, episodeFILE+'.nfo')
		with open(nfo_EPISODE_string, 'w') as textobj:
			textobj.write(
'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<episodedetails>
    <title>{0}</title>
    <showtitle>{1}</showtitle>
    <season>{2}</season>
    <episode>{3}</episode>
    <plot>{4}</plot>
    <tagline>{5}</tagline>
    <runtime>{6}</runtime>
    <thumb>{7}</thumb>
    <mpaa>{8}</mpaa>
    <genre clear="true">{9}</genre>
    <genre>{10}</genre>
    <genre>{11}</genre>
    <year>{12}</year>
    <aired>{13}</aired>
    <studio clear="true">{14}</studio>
</episodedetails>'''.format(EP_title_long, TVS_title, EP_season, EP_episode, EP_plot, EP_tagline, EP_duration, EP_image, EP_fsk, EP_genre1, EP_genre2, EP_genre3, EP_yeardate, EP_airdate, EP_studio))
		streamfile = os.path.join(EP_Path, episodeFILE+'.strm')
		debug_MS("(LIBRARY_Worker) ##### streamFILE : {0} #####".format(py2_enc(streamfile)))
		file = xbmcvfs.File(streamfile, 'w')
		file.write('plugin://'+addon.getAddonInfo('id')+'/?mode=playDash'+EP_nosub)
		file.close()
	nfo_SERIE_string = os.path.join(TVS_Path, 'tvshow.nfo')
	with open(nfo_SERIE_string, 'w') as textobj:
		textobj.write(
'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<tvshow>
    <title>{0}</title>
    <showtitle>{0}</showtitle>
    <season></season>
    <episode></episode>
    <plot>{1}</plot>
    <thumb aspect="landscape" type="" season="">{2}</thumb>
    <fanart url="">
        <thumb dim="1280x720" colors="" preview="{2}">{2}</thumb>
    </fanart>
    <genre clear="true">{3}</genre>
    <genre>{4}</genre>
    <genre>{5}</genre>
    <year>{6}</year>
    <aired>{7}</aired>
    <studio clear="true">{8}</studio>
</tvshow>'''.format(TVS_name, TVS_plot, TVS_image, EP_genre1, EP_genre2, EP_genre3, EP_yeardate, TVS_airdate, TVS_studio))
	debug_MS("(LIBRARY_Worker) XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX  ENDE = LIBRARY_Worker  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

def cleanPhoto(img): # UNICODE-Zeichen für Browser übersetzen - damit Fotos angezeigt werden
	img = py2_enc(img)
	for n in ((' ', '%20'), ('ß', '%C3%9F'), ('ä', '%C3%A4'), ('ö', '%C3%B6'), ('ü', '%C3%BC'), ('g:', '')
		, ('à', '%C3%A0'), ('á', '%C3%A1'), ('â', '%C3%A2'), ('è', '%C3%A8'), ('é', '%C3%A9'), ('ê', '%C3%AA'), ('ì', '%C3%AC'), ('í', '%C3%AD'), ('î', '%C3%AE')
		, ('ò', '%C3%B2'), ('ó', '%C3%B3'), ('ô', '%C3%B4'), ('ù', '%C3%B9'), ('ú', '%C3%BA'), ('û', '%C3%BB')):
		img = img.replace(*n)
	return img.strip()

def fixPathSymbols(structure): # Sonderzeichen für Pfadangaben entfernen
	structure = structure.strip()
	structure = structure.replace(' ', '_')
	structure = re.sub('[{@$%#^\\/;,:*?!\"+<>|}]', '_', structure)
	structure = structure.replace('______', '_').replace('_____', '_').replace('____', '_').replace('___', '_').replace('__', '_')
	if structure.startswith('_'):
		structure = structure[structure.rfind('_')+1:]
	if structure.endswith('_'):
		structure = structure[:structure.rfind('_')]
	return structure

def addQueue(vid):
	PL = xbmc.PlayList(1)
	STREAMe = vid[vid.find('###START'):]
	STREAMe = STREAMe[:STREAMe.find('END###')]
	url = STREAMe.split('###')[2]
	name = STREAMe.split('###')[3]
	image = STREAMe.split('###')[4]
	listitem = xbmcgui.ListItem(name)
	listitem.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	listitem.setProperty('IsPlayable', 'true')
	PL.add(url, listitem)

def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split('&')
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict

def addDir(name, url, mode, image, plot=None, tagline=None, origSERIE="", genre=None, mpaa=None, year=None, studio=None, addType=0, FAVdel=False, nosub=None):
	u = (sys.argv[0]+'?url='+quote_plus(url)+'&mode='+str(mode)+("" if image=="" or image==icon else '&image='+image)+("" if nosub is None else '&nosub='+str(nosub)))
	liz = xbmcgui.ListItem(name)
	liz.setInfo(type='Video', infoLabels={'Tvshowtitle': origSERIE, 'Title': name, 'Plot': plot, 'Tagline': tagline, 'Genre': genre, 'Mpaa': mpaa, 'Year': year, 'Studio': studio, 'Mediatype': 'video'})
	liz.setArt({'icon': icon, 'thumb': image, 'poster': image, 'fanart': defaultFanart})
	if image != icon and not artpic in image:
		liz.setArt({'fanart': image})
	entries = []
	if addType == 1 or addType == 2:
		if addType == 1 and FAVdel == False:
			FAVInfos_1 = 'MODE=ADD###START###{0}###{1}###{2}###{3}###END###'.format(url, origSERIE, py2_enc(image), plot.replace('\n', '#n#'))
			entries.append([translation(30651), 'RunPlugin('+sys.argv[0]+'?mode=favs&url='+quote_plus(FAVInfos_1)+')'])
		if enableLibrary:
			LIBInfos = '###START###{0}###{1}###{2}###END###'.format(url, origSERIE, updatestd)
			entries.append([translation(30653), 'RunPlugin('+sys.argv[0]+'?mode=tolibrary&url='+quote_plus(LIBInfos)+')'])
	if FAVdel == True:
		FAVInfos_2 = 'MODE=DEL###START###{0}###{1}###{2}###{3}###END###'.format(url, name, image, plot)
		entries.append([translation(30652), 'RunPlugin('+sys.argv[0]+'?mode=favs&url='+quote_plus(FAVInfos_2)+')'])
	liz.addContextMenuItems(entries, replaceItems=False)
	return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)

params = parameters_string_to_dict(sys.argv[2])
name = unquote_plus(params.get('name', ''))
url = unquote_plus(params.get('url', ''))
mode = unquote_plus(params.get('mode', ''))
image = unquote_plus(params.get('image', ''))
IDENTiTY = unquote_plus(params.get('IDENTiTY', ''))
nosub = unquote_plus(params.get('nosub', ''))
origSERIE = unquote_plus(params.get('origSERIE', ''))
stunden = unquote_plus(params.get('stunden', ''))
referer = unquote_plus(params.get('referer', ''))

xnormSD = unquote_plus(params.get('xnormSD', ''))
xhighHD = unquote_plus(params.get('xhighHD', ''))
xlink = unquote_plus(params.get('xlink', ''))
xdrm = unquote_plus(params.get('xdrm', ''))
xstat = unquote_plus(params.get('xstat', ''))

if mode == 'aSettings':
	addon.openSettings()
elif mode == 'iSettings':
	xbmcaddon.Addon('inputstream.adaptive').openSettings()
elif mode == 'clearCache':
	clearCache()
elif mode == 'listSeries':
	filter = quote_plus('{"Disabled": "0", "Station":"'+url+'"}')
	newUrl = "http://api.tvnow.de/v3/formats?filter="+filter+'&fields=id,title,station,hasFreeEpisodes,seoUrl,formatimageArtwork,defaultImage169Logo,genre1,categoryId,infoText,infoTextLong&maxPerPage=500'
	listSeries(newUrl)
elif mode == 'is_Serie':
	 listSeries(url)
elif mode == 'listSeasons':
	listSeasons(url, image)
elif mode == 'subThemes':
	newUrl = "https://api.tvnow.de/v3/channels/"+url+"?fields=[%22id%22,%22movies%22,[%22broadcastStartDate%22,%22id%22,%22title%22,%22season%22,%22episode%22,%22duration%22,%22teaserText%22,%22articleShort%22,%22articleLong%22,%22isDrm%22,%22free%22,%22seoUrl%22,%22fsk%22,%22productionYear%22,%22manifest%22,[%22dash%22,%22dashhd%22],%22format%22,[%22formatType%22,%22seoUrl%22,%22id%22,%22formatimageArtwork%22,%22defaultImage169Logo%22,%22title%22,%22station%22,%22genre1%22,%22genre2%22,%22genres%22,%22categoryId%22]]]"
	listEpisodes(newUrl)
elif mode == 'newShows':
	newUrl = "https://api.tvnow.de/v3/movies?fields=[%22broadcastStartDate%22,%22id%22,%22title%22,%22season%22,%22episode%22,%22duration%22,%22teaserText%22,%22articleShort%22,%22articleLong%22,%22isDrm%22,%22free%22,%22seoUrl%22,%22fsk%22,%22productionYear%22,%22manifest%22,[%22dash%22,%22dashhd%22],%22format%22,[%22formatType%22,%22seoUrl%22,%22id%22,%22formatimageArtwork%22,%22defaultImage169Logo%22,%22title%22,%22station%22,%22genre1%22,%22genre2%22,%22genres%22,%22categoryId%22]]&order=id%20desc&maxPerPage=100"
	listEpisodes(newUrl)
elif mode == 'listEpisodes':
	listEpisodes(url)
elif mode == 'listStations':
	listStations()
elif mode == 'listThemes':
	listThemes(url)
elif mode == 'listTopics':
	listTopics()
elif mode == 'subTopics':
	subTopics(url)
elif mode == 'listGenres':
	listGenres()
elif mode == 'getSearch':
	getSearch(url, nosub)
elif mode == 'listSearch':
	listSearch(url, nosub)
elif mode == 'liveTV':
	liveTV()
elif mode == 'playChannel':
	playChannel(url, name, image)
elif mode == 'playCODE':
	playCODE(IDENTiTY)
elif mode == 'playDash':
	playDash(xnormSD, xhighHD, xlink, xdrm, xstat)
elif mode == 'listShowsFavs':
	listShowsFavs()
elif mode == 'favs':
	favs(url)
elif mode == 'tolibrary':
	tolibrary(url)
elif mode == 'generatefiles':
	generatefiles(url, name)
elif mode == 'addQueue':
	addQueue(url)
else:
	index()