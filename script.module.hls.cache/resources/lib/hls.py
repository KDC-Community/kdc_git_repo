#!/usr/bin/python
# -*- coding: utf-8 -*-
import os,sys,requests,re
import xbmc,xbmcgui,xbmcplugin,xbmcaddon
__addon_handle__ = int(sys.argv[1])

def fix_encoding(path):
	if sys.platform.startswith('win'):return unicode(path,'utf-8')
	else:return unicode(path,'utf-8').encode('ISO-8859-1')

__addon__ =  xbmcaddon.Addon(id='script.module.hls.cache')
__addon_path__ = fix_encoding(__addon__.getAddonInfo('path'))

__kodi_log_file__ = fix_encoding(xbmc.translatePath('special://logpath/kodi.log'))
__kodi_error_log_file_ = os.path.abspath(os.path.join(__addon_path__,'error.log'))

def clear_dir(dir_path):
	if os.path.exists(dir_path):
		for name in os.listdir(dir_path):
			path = os.path.join(dir_path,name)
			if os.path.isfile(path):
				try:os.unlink(path)
				except:pass

def cache_loader(m3u8_url,m3u8_headers={},segment_headers={}):

	ip = __addon__.getSetting('ip')
	if not ip:
		ip = xbmc.getIPAddress()
		__addon__.setSetting('ip',ip)
	port = __addon__.getSetting('port')

	cache_forward = int(__addon__.getSetting('cache_forward'))
	download_delay = int(__addon__.getSetting('download_delay'))
	cache_multiplier = int(__addon__.getSetting('cache_multiplier'))

	count = int(0)
	duration = int(0)
	m3u8_timeout = int(10)
	m3u8_segment_timeout = int(5)
	chunk_size = int(1024*cache_multiplier)
	
	segment_error = int(0)
	max_segment_error = int(0)

	sess = requests.Session()
	content_type = 'application/octet-stream'
	cache_path = os.path.abspath(os.path.join(__addon_path__,'cache'))
	new_m3u8_path = os.path.abspath(os.path.join(cache_path,'hls.m3u8'))

	try:
		req = sess.get(url=m3u8_url,stream=False,allow_redirects=True,verify=False,timeout=m3u8_timeout,headers=m3u8_headers)
		if req.status_code == 200:
		
			xbmc.startServer(iTyp=xbmc.SERVER_WEBSERVER,bStart=True,bWait=False)
			with open(new_m3u8_path,'wb',buffering=chunk_size) as m3u8:
				for line in req.iter_lines():
					line = line.strip()
					if line:

						if line.startswith('http'):
							m3u8.write('{0}\n'.format('http://'+ ip +':'+ port +'/cache/' + str(count)))
							count +=1
						else:m3u8.write('{0}\n'.format(line))

			count = 0
			for line in req.iter_lines():
				line = line.strip()
				if line:

					if line.startswith('#EXTINF:'):
						match = re.compile(r'#EXTINF:(\d+)',re.DOTALL).search(line)
						if match:duration = int(match.group(1))

					if line.startswith('http'):
					 
						try:
							req = sess.get(url=line,stream=True,allow_redirects=True,verify=False,timeout=m3u8_segment_timeout,headers=segment_headers)

							content_type_header = req.headers.get('Content-Type')
							if content_type_header:
								match = re.compile(r'(.+?);',re.DOTALL).search(content_type_header)
								if match:content_type = match.group(1)

							with open(os.path.abspath(os.path.join(cache_path,str(count))),'wb',buffering=chunk_size) as fi:
								while True:
									chunk = req.raw.read(chunk_size)
									if not chunk:break
									else:fi.write(chunk)

						except:
							segment_error +=1
							if segment_error <= 2:continue
							elif segment_error > 2:
								segment_error = 0
								max_segment_error +=1
							
						if max_segment_error >= 10:
							if bool(xbmcgui.Dialog().yesno(heading='[COLOR red]CACHE LOARDER SEGMENT ERROR[/COLOR]',line1='Maximum segment error X10 reached',line2='',line3='',nolabel='EXIT',yeslabel='CONTINUE',autoclose=0)):max_segment_error = 0
							else:break

						if count == cache_forward:
							listitem = xbmcgui.ListItem(path='http://'+ ip +':'+ port +'/cache/hls.m3u8')
							listitem.setMimeType(content_type)
							listitem.setContentLookup(False)
							xbmcplugin.setResolvedUrl(handle=__addon_handle__,succeeded=True,listitem=listitem)

						elif count > cache_forward:
							if not xbmc.getCondVisibility('Player.HasMedia'):break
							if download_delay > 0:xbmc.sleep(duration * download_delay)
						count +=1

			req.close()
			while True:
				if not xbmc.getCondVisibility('Player.HasMedia'):
					xbmc.startServer(iTyp=xbmc.SERVER_WEBSERVER,bStart=False,bWait=False)
					clear_dir(cache_path);break
				else:xbmc.sleep(1500)

		else:xbmcgui.Dialog().ok('REQUESTS INFO','Status code : ' + str(req.status_code))
	except Exception as e:xbmcgui.Dialog().ok('[COLOR red]CACHE LOARDER ERROR[/COLOR]',str(e))