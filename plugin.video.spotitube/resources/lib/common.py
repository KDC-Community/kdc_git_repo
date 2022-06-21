# -*- coding: utf-8 -*-

import sys
import os
import re
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import json
import xbmcvfs
import shutil
import socket
import random
import time
import datetime
import io
import pickle
import gzip
import ssl
PY2 = sys.version_info[0] == 2
if PY2:
	from urllib import urlencode, quote_plus, unquote_plus  # Python 2.X
	from urllib2 import urlopen, build_opener  # Python 2.X
	TRANS_PATH, LOG_MESSAGE, INPUT_APP = xbmc.translatePath, xbmc.LOGNOTICE, 'inputstreamaddon' # Stand: 05.12.20 / Python 2.X
else:
	from urllib.parse import urlencode, quote_plus, unquote_plus  # Python 3.X
	from urllib.request import urlopen, build_opener  # Python 3.X
	TRANS_PATH, LOG_MESSAGE, INPUT_APP = xbmcvfs.translatePath, xbmc.LOGINFO, 'inputstream' # Stand: 05.12.20  / Python 3.X

try: _create_unverified_https_context = ssl._create_unverified_context
except AttributeError: pass
else: ssl._create_default_https_context = _create_unverified_https_context


global debuging
socket.setdefaulttimeout(40)
HOST_AND_PATH             = sys.argv[0]
ADDON_HANDLE              = int(sys.argv[1])
dialog                                  = xbmcgui.Dialog()
addon                                  = xbmcaddon.Addon()
addon_id                             = addon.getAddonInfo('id')
addon_name                      = addon.getAddonInfo('name')
addon_version                   = addon.getAddonInfo('version')
addonPath                           = TRANS_PATH(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
dataPath                              = TRANS_PATH(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
tempCAPA                            = TRANS_PATH(os.path.join(dataPath, 'cache', '')).encode('utf-8').decode('utf-8')
defaultFanart                      = (os.path.join(addonPath, 'fanart.jpg') if PY2 else os.path.join(addonPath, 'resources', 'media', 'fanart.jpg'))
icon                                       = (os.path.join(addonPath, 'icon.png') if PY2 else os.path.join(addonPath, 'resources', 'media', 'icon.png'))
artpic                                    = os.path.join(addonPath, 'resources', 'media', '').encode('utf-8').decode('utf-8')
region                                   = xbmc.getLanguage(xbmc.ISO_639_1, region=True).split('-')[1]
blackList                               = addon.getSetting('blacklist').split(',')
cacheHours                         = int(addon.getSetting('cache_rhythm'))
enableINFOS                       = addon.getSetting('showInfo') == 'true'
infoType                               = addon.getSetting('infoType')
infoDelay                              = int(addon.getSetting('infoDelay'))
infoDuration                        = int(addon.getSetting('infoDuration'))
useThumbAsFanart            = addon.getSetting('useThumbAsFanart') == 'true'
enableADJUSTMENT           = addon.getSetting('show_settings') == 'true'
deezerSearchDisplay          = str(addon.getSetting('deezerSearch_count'))
deezerVideosDisplay           = str(addon.getSetting('deezerVideos_count'))
itunesShowSubGenres       = addon.getSetting('itunesShowSubGenres') == 'true'
itunesForceCountry            = addon.getSetting('itunesForceCountry') == 'true'
itunesCountry                      = addon.getSetting('itunesCountry')
forceView                              = addon.getSetting('forceView') == 'true'
viewIDGenres                      = str(addon.getSetting('viewIDGenres'))
viewIDPlaylists                    = str(addon.getSetting('viewIDPlaylists'))
viewIDVideos                       = str(addon.getSetting('viewIDVideos'))
myTOKEN                              = str(addon.getSetting('pers_apiKey'))
BASE_URL_BP                      = 'https://www.beatport.com'
BASE_URL_BB                      = 'https://www.billboard.com'
BASE_URL_DDP                   = 'https://www.dj-playlist.de/'
BASE_URL_HM                     = 'https://hypem.com'
BASE_URL_OC                      = 'https://www.officialcharts.com/'
BASE_URL_SCC                    = 'https://spotifycharts.com/'
BASE_URL_DZ                      = 'https://api.deezer.com/search'

xbmcplugin.setContent(ADDON_HANDLE, 'musicvideos')

def py2_enc(s, nom='utf-8', ign='ignore'):
	if PY2:
		if not isinstance(s, basestring):
			s = str(s)
		s = s.encode(nom, ign) if isinstance(s, unicode) else s
	return s

def py2_uni(s, nom='utf-8', ign='ignore'):
	if PY2 and isinstance(s, str):
		s = unicode(s, nom, ign)
	return s

def py3_dec(d, nom='utf-8', ign='ignore'):
	if not PY2 and isinstance(d, bytes):
		d = d.decode(nom, ign)
	return d

def translation(id):
	return py2_enc(addon.getLocalizedString(id))

def failing(content):
	log(content, xbmc.LOGERROR)

def debug(content):
	log(content, xbmc.LOGDEBUG)

def log(msg, level=LOG_MESSAGE): # kompatibel mit Python-2 und Python-3
	msg = py2_enc(msg)
	return xbmc.log('[{0} v.{1}]{2}'.format(addon_id, addon_version, msg), level)

def getUrl(url, header=None, referer=None, data=None, agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'):
	opener = build_opener()
	opener.addheaders = [('User-Agent', agent), ('Accept-Encoding', 'gzip, identity')]
	try:
		if header: opener.addheaders = header
		if referer: opener.addheaders = [('Referer', referer)]
		response = opener.open(url, data, timeout=30)
		if response.info().get('Content-Encoding') == 'gzip':
			content = py3_dec(gzip.GzipFile(fileobj=io.BytesIO(response.read())).read())
		else:
			content = py3_dec(response.read())
	except Exception as e:
		failure = str(e)
		failing("(common.getUrl) ERROR - ERROR - ERROR : ########## {0} === {1} ##########".format(url, failure))
		dialog.notification(translation(30521).format('URL'), "ERROR = [COLOR red]{0}[/COLOR]".format(failure), icon, 12000)
		return sys.exit(0)
	return content

def getCache(url):
	if not xbmcvfs.exists(tempCAPA) and not os.path.isdir(tempCAPA):
		xbmcvfs.mkdirs(tempCAPA)
	cacheFile = os.path.join(tempCAPA, (''.join(c for c in py2_uni(url) if c not in '[{@$%#^/\\;:*?!\"\'<>|}]')).strip())
	cacheFile = cacheFile[:255]
	if os.path.exists(cacheFile):
		with open(cacheFile, 'rb') as output:
			result = pickle.load(output)
	else:
		result = getUrl(url)
		with open(cacheFile, 'wb') as input:
			pickle.dump(result, input)
	return result

def trashCache():
	if xbmcvfs.exists(tempCAPA) and os.path.isdir(tempCAPA):
		shutil.rmtree(tempCAPA, ignore_errors=True)
		xbmc.sleep(1000)
		return dialog.ok(addon_id, translation(30501))
	return dialog.ok(addon_id, translation(30502))

def TitleCase(s):
	return re.sub(r"['\w]+", lambda m:m.group(0).capitalize(), s)

def cleanPlaylist():
	playlist = xbmc.PlayList(1)
	playlist.clear()
	return playlist

def fitme(text):
	return text.replace(' - ', ' ')

def cleaning(text):
	text = py2_enc(text)
	for n in (('&lt;', '<'), ('&gt;', '>'), ('&amp;', '&'), ('&Amp;', '&'), ('&apos;', "'"), ("&quot;", "\""), ("&Quot;", "\""), ('&szlig;', 'ß'), ('&mdash;', '-'), ('&ndash;', '-'), ('&nbsp;', ' '), ('&hellip;', '...'), ('\xc2\xb7', '-'),
				("&#x27;", "'"), ('&#34;', '"'), ('&#39;', '\''), ('&#039;', '\''), ('&#x00c4', 'Ä'), ('&#x00e4', 'ä'), ('&#x00d6', 'Ö'), ('&#x00f6', 'ö'), ('&#x00dc', 'Ü'), ('&#x00fc', 'ü'), ('&#x00df', 'ß'), ('&#xD;', ''),
				('&#xC4;', 'Ä'), ('&#xE4;', 'ä'), ('&#xD6;', 'Ö'), ('&#xF6;', 'ö'), ('&#xDC;', 'Ü'), ('&#xFC;', 'ü'), ('&#xDF;', 'ß'), ('&#x201E;', '„'), ('&#xB4;', '´'), ('&#x2013;', '-'), ('&#xA0;', ' '),
				('&Auml;', 'Ä'), ('&Euml;', 'Ë'), ('&Iuml;', 'Ï'), ('&Ouml;', 'Ö'), ('&Uuml;', 'Ü'), ('&auml;', 'ä'), ('&euml;', 'ë'), ('&iuml;', 'ï'), ('&ouml;', 'ö'), ('&uuml;', 'ü'), ('&#376;', 'Ÿ'), ('&yuml;', 'ÿ'),
				('&agrave;', 'à'), ('&Agrave;', 'À'), ('&aacute;', 'á'), ('&Aacute;', 'Á'), ('&acirc;', 'â'), ('&Acirc;', 'Â'), ('&egrave;', 'è'), ('&Egrave;', 'È'), ('&eacute;', 'é'), ('&Eacute;', 'É'), ('&ecirc;', 'ê'), ('&Ecirc;', 'Ê'),
				('&igrave;', 'ì'), ('&Igrave;', 'Ì'), ('&iacute;', 'í'), ('&Iacute;', 'Í'), ('&icirc;', 'î'), ('&Icirc;', 'Î'), ('&ograve;', 'ò'), ('&Ograve;', 'Ò'), ('&oacute;', 'ó'), ('&Oacute;', 'Ó'), ('&ocirc;', 'ô'), ('&Ocirc;', 'Ô'),
				('&ugrave;', 'ù'), ('&Ugrave;', 'Ù'), ('&uacute;', 'ú'), ('&Uacute;', 'Ú'), ('&ucirc;', 'û'), ('&Ucirc;', 'Û'), ('&yacute;', 'ý'), ('&Yacute;', 'Ý'),
				('&atilde;', 'ã'), ('&Atilde;', 'Ã'), ('&ntilde;', 'ñ'), ('&Ntilde;', 'Ñ'), ('&otilde;', 'õ'), ('&Otilde;', 'Õ'), ('&Scaron;', 'Š'), ('&scaron;', 'š'), ('&ccedil;', 'ç'), ('&Ccedil;', 'Ç'),
				('&alpha;', 'a'), ('&Alpha;', 'A'), ('&aring;', 'å'), ('&Aring;', 'Å'), ('&aelig;', 'æ'), ('&AElig;', 'Æ'), ('&epsilon;', 'e'), ('&Epsilon;', 'Ε'), ('&eth;', 'ð'), ('&ETH;', 'Ð'), ('&gamma;', 'g'), ('&Gamma;', 'G'),
				('&oslash;', 'ø'), ('&Oslash;', 'Ø'), ('&theta;', 'θ'), ('&thorn;', 'þ'), ('&THORN;', 'Þ'), ('&bull;', '•'), ('&iexcl;', '¡'), ('&iquest;', '¿'), ('&copy;', '(c)'), ('\t', '    '), ('<br />', ' - '),
				("&rsquo;", "’"), ("&lsquo;", "‘"), ("&sbquo;", "’"), ('&rdquo;', '”'), ('&ldquo;', '“'), ('&bdquo;', '”'), ('&rsaquo;', '›'), ('lsaquo;', '‹'), ('&raquo;', '»'), ('&laquo;', '«'),
				('\\xC4', 'Ä'), ('\\xE4', 'ä'), ('\\xD6', 'Ö'), ('\\xF6', 'ö'), ('\\xDC', 'Ü'), ('\\xFC', 'ü'), ('\\xDF', 'ß'), ('\\x201E', '„'), ('\\x28', '('), ('\\x29', ')'), ('\\x2F', '/'), ('\\x2D', '-'), ('\\x20', ' '), ('\\x3A', ':'), ('\\"', '"'),
				(' ft ', ' feat. '), (' FT ', ' feat. '), ('Ft.', 'feat.'), ('ft.', 'feat.'), (' FEAT ', ' feat. '), (' Feat ', ' feat. '), ('Feat.', 'feat.'), ('Featuring', 'feat.'), ('&reg;', '®'), ('™', '')):
				text = text.replace(*n)
	return text.strip()

def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split('&')
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict

params = parameters_string_to_dict(sys.argv[2])
url = unquote_plus(params.get('url', ''))
mode = unquote_plus(params.get('mode', 'root'))
image = unquote_plus(params.get('image', ''))
type = unquote_plus(params.get('type', 'browse'))
limit = unquote_plus(params.get('limit', '0'))
extras = unquote_plus(params.get('extras', 'DEFAULT'))
transmit = unquote_plus(params.get('transmit', icon))
