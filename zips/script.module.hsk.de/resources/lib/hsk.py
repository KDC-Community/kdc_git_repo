#!/usr/bin/python
# -*- coding: utf-8 -*-
import fixetzipfile as zipfile
import os,sys,re,cPickle,platform
import urllib,urlparse,json,base64,hashlib,time
import xbmc,xbmcgui,xbmcplugin,xbmcaddon,xbmcvfs
import urllib3,requests,cfscraper,cookielib,mimetypes,secretpy

from io import BytesIO
from contextlib import closing
from HTMLParser import HTMLParser
from datetime import datetime,timedelta
html_parser = HTMLParser()

plugin_handle = int(sys.argv[1])
music_playlist=xbmc.PlayList(0)
video_playlist=xbmc.PlayList(1)

def get_test_viewer(s=''):### ADDON PATH TEST_VIEWER ###
	xbmcgui.Dialog().textviewer('TEST_VIEWER',str(s))
	d = open(os.path.join(addon_path,'TEST_VIEWER.txt'),'wb')
	d.write(str(s))
	d.close()

def xbmc_log_writer(s):
	return xbmc.log(s)

def fix_encoding(path):
	if sys.platform.startswith('win'):return unicode(path,'utf-8')
	else:return unicode(path,'utf-8').encode('ISO-8859-1')

addon =  xbmcaddon.Addon()
addon_id = addon.getAddonInfo('id')
addon_name = addon.getAddonInfo('name')
addon_author = addon.getAddonInfo('author')
addon_version = addon.getAddonInfo('version')
addon_path = fix_encoding(addon.getAddonInfo('path'))
addon_icon = fix_encoding(addon.getAddonInfo('icon'))
addon_fanart = fix_encoding(addon.getAddonInfo('fanart'))

base_save_list = [addon_id,'Addons27.db','Textures13.db','kodi.log']

special_path_skin = fix_encoding(xbmc.translatePath('special://skin'))
special_path_temp = fix_encoding(xbmc.translatePath('special://temp'))
special_path_home = fix_encoding(xbmc.translatePath('special://home'))
special_path_cdrips = fix_encoding(xbmc.translatePath('special://cdrips'))
special_path_profile = fix_encoding(xbmc.translatePath('special://profile'))
special_path_logpath = fix_encoding(xbmc.translatePath('special://logpath'))
special_path_database = fix_encoding(xbmc.translatePath('special://database'))
special_path_userdata = fix_encoding(xbmc.translatePath('special://userdata'))
special_path_subtitles = fix_encoding(xbmc.translatePath('special://subtitles'))
special_path_recordings = fix_encoding(xbmc.translatePath('special://recordings'))
special_path_thumbnails = fix_encoding(xbmc.translatePath('special://thumbnails'))
special_path_screenshots = fix_encoding(xbmc.translatePath('special://screenshots'))
special_path_masterprofile = fix_encoding(xbmc.translatePath('special://masterprofile'))
special_path_musicplaylists = fix_encoding(xbmc.translatePath('special://musicplaylists'))
special_path_videoplaylists = fix_encoding(xbmc.translatePath('special://videoplaylists'))
special_path_packages = fix_encoding(xbmc.translatePath('special://home/addons/packages'))


def get_intern_ip():
	return xbmc.getIPAddress()

def get_platform_system():
	return platform.system()

def get_platform_python_version():
	return platform.python_version()

def get_xbmc_build_version():
	return xbmc.getInfoLabel('System.BuildVersion')[0:5]

def get_datetime_now_str():
	return str(datetime.now().strftime("%d%m%Y_%H%M%S"))


base_security_headers = {
	'Host':'',
	'Origin':'',
	'Referer':'',
	'User-Agent':'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'}

def get_url_specific_security_headers(url):

	if url:
		if '?' in url:url = url.split('?')[0]
		return {
			'Origin':urlparse.urlparse(url).scheme + '://' + urlparse.urlparse(url).netloc,
			'Referer':url,
			'User-Agent':'Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64 Safari/537.36'} # https://deviceatlas.com/blog/list-of-user-agent-strings #
	else:return {}

def get_post_data_dict_from_url():
	return dict(x.strip().split('=') for x in url.split('?')[1].split('&')if '=' in x)


def get_url(url,stream=False,allow_redirects=False,verify=True,timeout=30,headers_dict={}):
	with closing(requests.get(url,stream=stream,allow_redirects=allow_redirects,verify=verify,timeout=timeout,headers=headers_dict)) as req:
		return req

def get_url_ses(url,stream=False,allow_redirects=False,verify=True,timeout=30,headers_dict={}):
	with closing(requests.Session()) as ses:
		return ses.get(url,stream=stream,allow_redirects=allow_redirects,verify=verify,timeout=timeout,headers=headers_dict)


def post_url(url,data_dict={},allow_redirects=False,verify=True,timeout=30,headers_dict={}):
	with closing(requests.post(url=url,data=data_dict,allow_redirects=allow_redirects,verify=verify,timeout=timeout,headers=headers_dict)) as req:
		return req

def post_url_ses(url,data_dict={},allow_redirects=False,verify=True,timeout=30,headers_dict={}):
	with closing(requests.Session()) as ses:
		return ses.post(url=url,data=data_dict,allow_redirects=allow_redirects,verify=verify,timeout=timeout,headers=headers_dict)


def get_cfstokens_dict(url,timeout=30,scraper_delay=0,proxies_dict={}):
	with closing(cfscrape.create_scraper(scraper_delay)) as scraper:
		return scraper.get_tokens(url,timeout=timeout,proxies=proxies_dict)

def get_cfscookie_string(url,timeout=30,scraper_delay=0):
	with closing(cfscrape.create_scraper(scraper_delay)) as scraper:
		return scraper.get_cookie_string(url,timeout=timeout)


def get_cfscraper(url='',stream=False,allow_redirects=False,verify=True,timeout=30,delay=5,headers_dict={}):
	with closing(cfscraper.create_scraper(delay=delay)) as scraper:
		return scraper.get(url,stream=stream,allow_redirects=allow_redirects,verify=verify,timeout=timeout,headers=headers_dict)

def post_cfscraper(url='',data={},stream=False,allow_redirects=False,verify=True,timeout=30,delay=5,headers_dict={}):
	with closing(cfscraper.create_scraper(delay=delay)) as scraper:
		return scraper.post(url,data=data,stream=stream,allow_redirects=allow_redirects,verify=verify,timeout=timeout,headers=headers_dict)


def save_cfs_sess_cookies(cfs):
	cookie_dict_list = []
	cookie_file = os.path.join(addon_path,'cookie.cpi')
	cookie_list = cfs.raw.headers.getlist('Set-Cookie')
	if (cookie_list and os.path.exists(cookie_file)):os.remove(cookie_file)
	elif cookie_list:
		for cookie in cookie_list:
			cookie_dict_list.append(dict(x.strip().split('=') for x in cookie.split(';')if '=' in x))
		if cookie_dict_list:
			with open(cookie_file,'wb') as fi:cPickle.dump(cookie_dict_list,fi,protocol=cPickle.HIGHEST_PROTOCOL)

def load_cfs_sess_cookies(sess):
	if os.path.exists(os.path.join(addon_path,'cookie.cpi')):
		sess.cookies.clear()
		with open(os.path.join(addon_path,'cookie.cpi'),'rb') as fi:
			for cd in cPickle.load(fi):sess.cookies.update(cd)


def get_cfscraper_sess(url='',stream=False,allow_redirects=False,verify=True,timeout=30,delay=5,headers_dict={}):
	sess = requests.Session()
	load_cfs_sess_cookies(sess)
	with closing(cfscraper.create_scraper(sess=sess,delay=delay)) as scraper:
		cfs = scraper.get(url,stream=stream,allow_redirects=allow_redirects,verify=verify,timeout=timeout,headers=headers_dict)
	save_cfs_sess_cookies(cfs)
	return cfs

def post_cfscraper_sess(url='',data={},stream=False,allow_redirects=False,verify=True,timeout=30,delay=5,headers_dict={}):
	sess = requests.Session()
	load_cfs_sess_cookies(sess)
	with closing(cfscraper.create_scraper(sess=sess,delay=delay)) as scraper:
		cfs = scraper.post(url,data=data,stream=stream,allow_redirects=allow_redirects,verify=verify,timeout=timeout,headers=headers_dict)
	save_cfs_sess_cookies(cfs)
	return cfs


def open_addon_settings():
	addon.openSettings()

def set_addon_settings(id,value):
	addon.setSetting(id,value)

def get_addon_settings(id):
	return addon.getSetting(id)

def open_url_resolver_settings():
	urlresolver.display_settings()


def get_newline(s,l=50,u='\n'):
	i=0
	ii=0
	ss=''
	s = s.strip()
	while i < len(s):
		ss += s[i:i+1]
		i+=1
		ii+=1
		if ii == l:ss +=u;ii=0
	return ss

def xbmc_get_localized_string(id):
	return xbmc.getLocalizedString(id)

def color_text(color,text):
	return '[COLOR '+color+']'+text+'[/COLOR]'

def dialog_select(heading='',list=[]):
	return xbmcgui.Dialog().select(heading=heading, list=list)

def dialog_ok(heading='',line1='',line2='',line3=''):
	return xbmcgui.Dialog().ok(heading=heading,line1=line1,line2=line2,line3=line3)

def dialog_textviewer(heading='',text=''):
	xbmcgui.Dialog().textviewer(heading=heading,text=text)

def dialog_yes_no(heading='',line1='',line2='',line3='',nolabel='No',yeslabel='Yes',autoclose=0):
	return xbmcgui.Dialog().yesno(heading=heading,line1=line1,line2=line2,line3=line3,nolabel=nolabel,yeslabel=yeslabel,autoclose=autoclose)

def dialog_notification_info(heading='',message='',time=2000,sound=True):
	xbmcgui.Dialog().notification(heading=heading,message=message,icon=xbmcgui.NOTIFICATION_INFO,time=time,sound=sound)

def dialog_notification_warning(heading='',message='',time=2000,sound=True):
	xbmcgui.Dialog().notification(heading=heading,message=message,icon=xbmcgui.NOTIFICATION_WARNING,time=time,sound=sound)

def dialog_notification_error(heading='',message='',time=2000,sound=True):
	xbmcgui.Dialog().notification(heading=heading,message=message,icon=xbmcgui.NOTIFICATION_ERROR,time=time,sound=sound)

def dialog_imput_alphanum(heading='',defaultt='',autoclose=0):
	return urllib.quote(xbmcgui.Dialog().input(heading=heading,defaultt=defaultt,type=xbmcgui.INPUT_ALPHANUM,option=xbmcgui.INPUT_ALPHANUM,autoclose=autoclose))

def dialog_imput_numeric(heading='',defaultt='',autoclose=0):
	return xbmcgui.Dialog().input(heading=heading,defaultt=defaultt,type=xbmcgui.INPUT_NUMERIC,option=xbmcgui.INPUT_NUMERIC,autoclose=autoclose)

def dialog_browse(type=0,heading='',shares='files',mask='',useThumbs=False,treatAsFolder=False,defaultt='',enableMultiple=False):
	return xbmcgui.Dialog().browse(type=type,heading=heading,shares=shares,mask=mask,useThumbs=useThumbs,treatAsFolder=treatAsFolder,defaultt=defaultt,enableMultiple=enableMultiple)

def close_all_dialog():xbmc.executebuiltin('Dialog.Close(all,true)')


### type ### music,video,pictures,game ###
def add_items(items_list=[{'title':'','url':'','image':'','fanart':'','imode':None,'add_info':{},'add_params':{},'add_contextmenu':[['','']],'type':'video','playlist':False,'is_folder':True,'is_playable':False}]):

	item_index = 0
	playlist_index = 0
	music_playlist.clear()
	video_playlist.clear()

	if len(items_list) > 0:

		for item in items_list:

			url = item['url']
			info={'title':item['title']}
			info.update(item['add_info'])

			iparams={'title':item['title'],'url':url,'image':item['image'],'fanart':item['fanart'],'imode':item['imode'],'item_index':item_index,'playlist_index':playlist_index}
			iparams.update(item['add_params'])
			cparams={'title':item['title'],'url':url,'image':item['image'],'fanart':item['fanart'],'item_index':item_index,'playlist_index':playlist_index}
			cparams.update(item['add_params'])

			listitem = xbmcgui.ListItem(label=item['title'],iconImage='DefaultFolder.png',thumbnailImage=item['image'],path=url)
			listitem.setInfo(type=item['type'],infoLabels=info)
			listitem.setProperty('Fanart_Image',item['fanart'])

			if (item['is_folder'] == True and item['is_playable'] == False):
				url=sys.argv[0] +'?'+ urllib.quote_plus(json.dumps(iparams))
				listitem.setProperty('IsPlayable','false')

			elif (item['is_folder'] == False and item['is_playable'] == False):
				url=sys.argv[0] +'?'+ urllib.quote_plus(json.dumps(iparams))
				listitem.setProperty('IsPlayable','true')

			elif (item['is_folder'] == False and item['is_playable'] == True):
				listitem.setProperty('IsPlayable','true')

			cmenu = []
			for title,cmode in item['add_contextmenu']:
				if title and cmode:
					cparams.update({'cmode':cmode})
					cmenu.append((title,'XBMC.RunPlugin('+ sys.argv[0] +'?'+ urllib.quote_plus(json.dumps(cparams)) +')'))
			if cmenu:listitem.addContextMenuItems(items=cmenu,replaceItems=True)

			if ((item['playlist'] == True) and (item['type'].lower() == 'music')):music_playlist.add(url=url,listitem=listitem,index=playlist_index);playlist_index +=1
			if ((item['playlist'] == True) and (item['type'].lower() == 'video')):video_playlist.add(url=url,listitem=listitem,index=playlist_index);playlist_index +=1

			xbmcplugin.addDirectoryItem(handle=plugin_handle,url=url,listitem=listitem,isFolder=item['is_folder'],totalItems=len(items_list));item_index +=1

		xbmcplugin.endOfDirectory(handle=int(sys.argv[1]),succeeded=True,updateListing=False,cacheToDisc=True)
	else:xbmcgui.Dialog().notification(heading='Items info',message='No items found !',icon=xbmcgui.NOTIFICATION_INFO,time=2000,sound=True)

def get_youtube_live_stream(channel_id):### is_folder = False and is_playable == True ###
	return'plugin://plugin.video.youtube/play/?channel_id=%s&live=1' % channel_id

def get_youtube_video(video_id):### is_folder = False and is_playable == True ###
	return'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % video_id

def get_youtube_playlist(playlist_id):### is_folder = True and is_playable == True ###
	return'plugin://plugin.video.youtube/playlist/%s/' % playlist_id

def get_youtube_channel(channel_id):### is_folder = True and is_playable == True ###
	return'plugin://plugin.video.youtube/channel/%s/' % channel_id

def get_youtube_search(search_text):### is_folder = True and is_playable == True ###
	return'plugin://plugin.video.youtube/search/?q=%s' % search_text


### import secretpy ###
### https://cryptii.com/ ###
### https://www.dcode.fr/rot-cipher ###
### https://www.geeksforgeeks.org/rot13-cipher/### 

def get_rot47(s):
	x = []
	for i in xrange(len(s)):
		j = ord(s[i])
		if j >= 33 and j <= 126:x.append(chr(33 + ((j + 14) % 94)))
		else:x.append(s[i])
	return ''.join(x)

def encode_base64(s):
	return base64.encodestring(s)

def decode_base64(s):
	return base64.decodestring(s)


def get_domain(url):
	return urlparse.urlparse(url).netloc

def get_base_url(url):
	return urlparse.urlparse(url).scheme + '://' + urlparse.urlparse(url).netloc

def urllib_quote_plus_save(url,safe='/:?=&'):
	return urllib.quote_plus(url,safe=safe)

def fix_url_end_backslash(path):
	if not path.endswith('/'):return path + '/'

def normalize_url_backslashes(url):
	return url.replace('\/','/')

def url_join(element_array=[]):
	return urlparse.urljoin(*element_array)

def clean_title(s):
	s = re.sub('[\\\/:"*?<>|]+','',s)
	return re.sub('\s+',' ',s)

### ([^>]*?) ### span tag regex ###
def regex_search(regex,content):
	return re.compile(regex,re.DOTALL).search(content)

def regex_findall(regex,content):
	return re.compile(regex,re.DOTALL).findall(content)

def json_dumps(js):
	return json.dumps(js)

def json_loads(js):
	return json.loads(js)

def list_dict_sorted(list_dict,dict_key,reverse=False):
	return sorted(list_dict, key = lambda i: i[dict_key],reverse=reverse)


def get_resolved_url(url):
	try:
		source = urlresolver.HostedMediaFile(url=url)
		if source.valid_url():return source.resolve()
	except Exception as exc:xbmcgui.Dialog().notification('URL RESOLVER',str(exc),xbmcgui.NOTIFICATION_ERROR,2000,True);sys.exit(0)

### is_folder == False and is_playable == True ### directly item play ###
### +'|verifypeer=false&Origin=xxx&Referer=xxx' ####

def set_resolved_url(url=''):### is_folder = False and is_playable = False ###
	listitem = xbmcgui.ListItem(path=url)
	xbmcplugin.setResolvedUrl(handle=plugin_handle,succeeded=True,listitem=listitem)

def xbmc_player_play(title='',url='',image='',type='video',windowed=False):### is_folder = True and is_playable = False ###
	listitem = xbmcgui.ListItem(label=title,iconImage=image,thumbnailImage=image,path=url)
	listitem.setInfo(type=type,infoLabels={'Title':title})
	listitem.setProperty('IsPlayable','true')
	xbmc.Player().play(item=url,listitem=listitem,windowed=windowed)

def xbmc_show_picture(url=''):
	xbmc.executebuiltin('ShowPicture(%s)' % (url))

def get_slideshow(dir_path):
	xbmc.executebuiltin('Slideshow(%s)' % (dir_path))

def get_recursive_slideshow(dir_path):
	xbmc.executebuiltin('RecursiveSlideShow(%s)' % (dir_path))


def get_profile_name():
	return xbmc.getInfoLabel('System.ProfileName') 

def load_profile(profil):
	xbmc.executebuiltin('LoadProfile(%s)' % (profil))

def reload_profile():
	profil=xbmc.getInfoLabel('System.ProfileName') 
	xbmc.executebuiltin('LoadProfile('+profil+')')

def update_addons():
	xbmc.executebuiltin('UpdateLocalAddons')    

def update_repos():  
	xbmc.executebuiltin('UpdateAddonRepos')

def unload_skin():
	xbmc.executebuiltin('UnloadSkin()')

def reload_skin():
	xbmc.executebuiltin('ReloadSkin()')

def container_refresh():
	xbmc.executebuiltin('Container.Refresh')  


def start_android_activity(package='',intent='',data_type='',data_url=''):
	xbmc.executebuiltin('XBMC.StartAndroidActivity("%s", "%s", "%s", "%s")' % (package,intent,data_type,data_url))

def install_apk(apk_path):
	xbmc.executebuiltin('XBMC.StartAndroidActivity("com.android.packageinstaller","android.intent.action.INSTALL_PACKAGE","application/vnd.android.package-archive","file:%s")' % (apk_path))


def set_addon_disabled(addon_id):
	xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","params":{"addonid":"%s","enabled":"false"},"id":1}' % (addon_id))

def set_addon_enabled(addon_id):
	xbmc.executeJSONRPC('{"jsonrpc":"2.0","method":"Addons.SetAddonEnabled","params":{"addonid":"%s","enabled":"true"},"id":1}' % (addon_id))


def xbmc_sleep_ms(ms):
	xbmc.sleep(ms)

def time_sleep_sec(sec):
	time.sleep(sec)
	
def timestamp_ms():
	return str(int(time.time()*1000))


def os_sep():
	return os.sep

def abspath(path):
	return os.path.abspath(path)

def normpath(path):
	return os.path.normpath(path)

def realpath(path):
	return os.path.realpath(path)

def fix_path_end_backslash(path):
	if not path.endswith(os.sep):return path + os.sep

def path_join(element_array=[]):
	return os.path.join(*element_array)

def check_and_create_dir_path(path):
	if not os.path.exists(path):os.makedirs(path)
	return path


def isfile(path):
	return os.path.isfile(path)

def isdir(path):
	return os.path.isdir(path)

def path_exists(path):
	return os.path.exists(path)

def path_split(path):
	return os.path.split(path)

def dir_name(path):
	return os.path.dirname(path)

def last_dir_name(path):
	return os.path.split(path)[0].split(os.sep)[-1]
	
def base_name(path):
	return os.path.basename(path)


def remove_dir(dir_path):
	if os.path.exists(dir_path):
		shutil.rmtree(dir_path,ignore_errors=True)

def remove_file(file_path):
	if os.path.exists(file_path):
		os.remove(file_path)


def read_file(file_path):
	if os.path.exists(file_path):
		with open(file_path,'rb') as fi:
			return fi.read()

def write_file(file_path,s):
	with open(file_path,'wb') as fi:
		fi.write(s)


def save_pickle(file_path,value):
	with open(file_path,'wb') as fi:
		cPickle.dump(value,fi)

def load_pickle(file_path):
	if os.path.exists(file_path):
		with open(file_path,'rb') as fi:
			return cPickle.load(fi)


def list_dir(dir_path):
	return os.listdir(dir_path)

def os_walk(dir_path,topdown=False,onerror=None,followlinks=True):
	return os.walk(dir_path,topdown=topdown,onerror=onerror,followlinks=followlinks)


def xbmcvfs_file_exists(file_path):
	return xbmcvfs.exists(file_path)

def xbmcvfs_read_file(file_path):
	with xbmcvfs.File(file_path) as fi:
		return fi.read()

def xbmcvfs_write_file(file_path,buffer):
	with xbmcvfs.File(file_path,'w') as fi:
		return fi.write(buffer)

def xbmcvfs_get_file_size(file_path):
	with xbmcvfs.File(file_path) as fi:
		return fi.size()

def xbmcvfs_file_seek(file_path,start_byte,end_byte):
	with xbmcvfs.File(file_path) as fi:
		return fi.seek(start_byte,end_byte)

def xbmcvfs_copy_file(source,destination):
	return xbmcvfs.copy(source,destination)

def xbmcvfs_delete_file(file_path):
	return xbmcvfs.delete(file_path)

def xbmcvfs_rename_file(file_path,new_filename):
	return xbmcvfs.rename(file_path,new_filename)

def xbmcvfs_mkdir(dir_path):
	return xbmcvfs.mkdir(dir_path)

def xbmcvfs_mkdirs(dir_path):
	return xbmcvfs.mkdirs(dir_path)

def xbmcvfs_rmdir(dir_path,force=False):
	return xbmcvfs.rmdir(dir_path,force=force)

def xbmcvfs_listdir(dir_path):
	return xbmcvfs.listdir(dir_path)


def get_xbmc_platform():
	if xbmc.getCondVisibility('System.Platform.Windows'):return 'Windows'
	if xbmc.getCondVisibility('System.Platform.UWP'):return 'UWP'
	if xbmc.getCondVisibility('System.Platform.Android'):return 'Android'
	if xbmc.getCondVisibility('System.Platform.Linux'):return 'Linux'
	if xbmc.getCondVisibility('System.Platform.Linux.RaspberryPi'):return 'RaspberryPi'
	if xbmc.getCondVisibility('System.Platform.OSX'):return 'OSX'
	if xbmc.getCondVisibility('System.Platform.IOS'):return 'IOS'
	if xbmc.getCondVisibility('System.Platform.Darwin'):return 'Darwin'


def hash_file(file_path,mode_int=1):
	if os.path.exists(file_path):
		with open(file_path) as fi:
			data = fi.read()
			if mode_int == 1:return hashlib.md5(data).hexdigest()
			elif mode_int == 2:return hashlib.sha1(data).hexdigest()
			elif mode_int == 3:return hashlib.sha224(data).hexdigest()
			elif mode_int == 4:return hashlib.sha256(data).hexdigest()
			elif mode_int == 5:return hashlib.sha384(data).hexdigest()
			elif mode_int == 6:return hashlib.sha512(data).hexdigest()


def get_directory_size(dir_path):
	size = int(0)
	for path,dirs,files in os.walk(dir_path,topdown=False,onerror=None,followlinks=True):
		for file in files:
			full_file_path = os.path.join(path, file)
			size += int(os.path.getsize(full_file_path))
	return int(size)

def get_convert_size(size):
	if (size == 0 ):return '0 B'
	units = (' B',' KB',' MB',' GB',' TB',' PB',' EB',' ZB',' YB' )
	i = int(math.floor( math.log(size,1024)))
	p = math.pow(1024,i)
	size = "%.3f" % round((size / p ),3)
	return '{}{}'.format(size,units[i])

def get_kahan_sum(l):
    summation = 0.0
    c = 0.0
    for i in l:
        y = i - c
        t = summation + y
        c = (t - summation) - y
        summation = t
    return summation


def request_download_file_dp(file_name='',file_url='',save_path='',verify=True,timeout=30,headers_dict={},dp_mode=1):

	req = requests.get(file_url,stream=True,verify=verify,timeout=30,headers=headers_dict)
	if req.status_code == 200:

		if dp_mode == 1:dp = xbmcgui.DialogProgress()
		if dp_mode == 2:dp = xbmcgui.DialogProgressBG()
		dp.create('REQUESTS FILE DOWNLOADER','Download file:')
		dp.update(0)

		content_size = 0
		content_size = int(req.headers.get('Content-Length'))
		content_type = mimetypes.guess_extension(req.headers.get('Content-Type'))
		if not content_type:content_type = '.xxx'

		chunk_len = 0
		chunk_size = 1024*16

		file_name = file_name + content_type
		with open(os.path.join(save_path,file_name),'wb',buffering=chunk_size) as fi:
			while True:

				chunk = req.raw.read(chunk_size)
				if not chunk:break

				fi.write(chunk)
				chunk_len +=len(chunk)

				try:dp.update(min(chunk_len * 100 / content_size,100),'Download file :',file_name)
				except:pass

				if dp_mode == 1:
					if dp.iscanceled():break

		req.close()
		fi.close()		
		dp.close()

def request_download_file_bytes_dp(file_url,verify=True,timeout=30,headers={}):

	req = requests.get(file_url,stream=True,verify=verify,timeout=timeout,headers=headers)
	if req.status_code == 200:

		dp = xbmcgui.DialogProgress()
		dp.create('DOWNLOAD FILE CONTENT','Loading data !','Please wait ...')
		dp.update(0)

		bytes = BytesIO()
		chunk_len= int(0)
		content_bytes_len = int(req.headers.get('Content-Length'))

		while True:

			chunk = req.raw.read(1024*16)
			if not chunk:break

			chunk_len += len(chunk)
			bytes.write(chunk)

			try:
				percent = min(chunk_len * 100 / content_bytes_len ,100)
				dp.update(percent)
			except:pass

			if dp.iscanceled():
				req.close()
				dp.close()
				return

		req.close()
		dp.close()
		return bytes


def extract_zip_dp(zip_path,extract_path,zip_pwd=None,save_list=[]):

	dp = xbmcgui.DialogProgress()
	dp.create('EXTRACT ZIP','Unpacking data !','Please wait ...')
	dp.update(0)

	zip_path = os.path.abspath(zip_path)
	extract_path = os.path.abspath(extract_path)
	zip = zipfile.ZipFile(zip_path,mode='r',compression=zipfile.ZIP_STORED,allowZip64=True)

	count = int(0)
	list_len = len(zip.infolist())
	for item in zip.infolist():

		count += 1
		try:
			percent = min(count * 100 / list_len ,100)
			dp.update(percent)
		except:pass

		if not any((x in item.filename for x in save_list)):
			try:zip.extract(item,path=extract_path,pwd=zip_pwd)
			except:pass

		if dp.iscanceled():break

	zip.close()
	dp.close()


def zip_dir_dp(dir_path,zip_save_path,new_archive_name,base_dir=True):

	dp = xbmcgui.DialogProgress()
	dp.create('CREATE ZIP','Create zip archive !','Please wait ...')
	dp.update(0)

	dir_path = os.path.abspath(dir_path)
	zip_save_path = os.path.abspath(zip_save_path)
	zip_full_save_path = os.path.join(zip_save_path,new_archive_name + '.zip')
	zip = zipfile.ZipFile(zip_full_save_path,mode='w',compression=zipfile.ZIP_STORED,allowZip64=True)

	count = int(0)
	files_list = []

	files_list = list(os.walk(dir_path,topdown=False,onerror=None,followlinks=True))
	list_len = sum(len(files) for path,dirs,files in files_list)

	root_len = len(dir_path)
	if base_dir == True:root_len = root_len - len(os.path.basename(dir_path))

	for root,dirs,files in files_list:

		for file in files:
			path = os.path.join(root,file)
			archive_name = os.path.join(os.path.abspath(root)[root_len:],file)
			try:zip.write(path,archive_name,zipfile.ZIP_DEFLATED)
			except:pass

			count += 1
			try:
				percent = min(count * 100 / list_len ,100)
				dp.update(percent)
			except:pass

			if dp.iscanceled():break

	zip.close()
	dp.close()


def clean_dir(dir_path,save_list=[]):

	dp = xbmcgui.DialogProgress()
	dp.create('CLEAN DIR','Clean data !','Please wait ...')
	dp.update(0)

	files_list = []
	counter = int(0)
	files_list = list(os.walk(dir_path,topdown=False,onerror=None,followlinks=True))
	list_len = sum(len(files) for path,dirs,files in files_list)

	for root,dirs,files in files_list:

		for dir in dirs:
			path = os.path.join(root,dir)
			if not any((x in path for x in save_list)):

				if os.path.islink(path):
					try:os.unlink(path)
					except:pass
				else:
					try:os.rmdir(path)
					except:pass

		for file in files:
			path = os.path.join(root,file)
			if not any((x in path for x in save_list)):

				try:os.unlink(path)
				except:pass

			counter +=1
			try:
				percent = min(counter * 100 / list_len,100)
				dp.update(percent,'Clean data :',path,file)
			except:pass

		if dp.iscanceled():break

	dp.close()


def get_xbmc_log():
	file_path = os.path.join(special_path_logpath,'kodi.log')
	if os.path.exists(file_path):
		with open(file_path,'rb') as fi:
			log_file_content = fi.read()
			return log_file_content.replace('ERROR:','[COLOR red]ERROR[/COLOR]:').replace('WARNING:','[COLOR gold]WARNING[/COLOR]:')


def close_xbmc(special_home_path=''):

	if xbmc.getCondVisibility('System.Platform.Windows'):
		try:os.system('@ECHO off')
		except:pass
		try:os.system('TSKKILL Kodi*')
		except:pass
		try:os.system('TASKKILL /IM Kodi* /T /F')
		except:pass

	elif xbmc.getCondVisibility('System.Platform.Android'):
		try: os.system('adb shell kill org.xbmc.kodi')
		except: pass
		try:os.system('adb shell am force-stop org.xbmc.kodi')
		except:pass

		xbmcgui.Dialog().ok('[COLOR red]DANGER ![/COLOR]','[COLOR red]Android system discovered ![/COLOR]','[COLOR red]Force the termination of the program ![/COLOR]','[COLOR red]Do not exit the program via Exit or Quit !\nPress OK ![/COLOR]')
		if 'kodi'in special_home_path.lower():xbmc.executebuiltin('StartAndroidActivity("","android.settings.APPLICATION_DETAILS_SETTINGS","","package:org.xbmc.kodi")')
		else:xbmc.executebuiltin('StartAndroidActivity("","android.settings.APPLICATION_SETTINGS","","")')
		sys.exit(0)

	elif xbmc.getCondVisibility('System.Platform.Linux') or xbmc.getCondVisibility('System.Platform.Darwin'):
		try:os.system('killall Kodi')
		except:pass
		try:os.system('killall -9 Kodi')
		except:pass
		try:os.system('killall -9 kodi.bin')
		except:pass

	elif xbmc.getCondVisibility('System.Platform.OSX'):
		try:os.system('killall AppleTV')
		except:pass
		try:os.system('killall -9 AppleTV')
		except:pass

	elif xbmc.getCondVisibility('System.Platform.Linux.RaspberryPi'):
		try:os.system('sudo initctl stop kodi')
		except:pass

	xbmcgui.Dialog().ok('[COLOR red]DANGER ![/COLOR]','[COLOR red]Program could not be stopped ![/COLOR]','[COLOR red]Force the termination of the program ![/COLOR]','[COLOR red]Do not exit the program via Exit or Quit ![/COLOR]')
	sys.exit(0)


def set_content_type(content_type='files'):
	xbmcplugin.setContent(plugin_handle,content_type)

def get_view_mode():
	return str(xbmcgui.Window(xbmcgui.getCurrentWindowId()).getFocusId())

def set_view_mode(view_mode=''):
	xbmc.executebuiltin('Container.SetViewMode(%s)' % (view_mode))

def get_params():
	argv = urllib.unquote_plus(sys.argv[2][1:])
	if argv.startswith('{') and argv.endswith('}'):return json.loads(argv)