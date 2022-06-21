# -*- coding: utf-8 -*-

'''
    Copyright (C) 2022 realvito

    You(T) Musicbox

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.
'''

import os
import xbmc
import xbmcvfs
import shutil
from resources.lib.common import *
from resources.lib import navigator


def run():
	SEP = os.sep
	if mode == 'root': ##### Delete complete old Userdata-Folder to cleanup old Entries #####
		DONE = False    ##### [plugin.video.spotitube v.2.1.9] - 25.09.2020 #####
		firstSCRIPT = TRANS_PATH(os.path.join('special://home'+SEP+'addons'+SEP+addon_id+SEP+'lib'+SEP)).encode('utf-8').decode('utf-8')
		UNO = os.path.join(firstSCRIPT, 'only_at_FIRSTSTART')
		if xbmcvfs.exists(UNO):
			sourceUSER = TRANS_PATH(os.path.join('special://home'+SEP+'userdata'+SEP+'addon_data'+SEP+addon_id+SEP)).encode('utf-8').decode('utf-8')
			if xbmcvfs.exists(sourceUSER):
				try:
					xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Addons.SetAddonEnabled", "params":{"addonid":"'+addon_id+'", "enabled":false}}')
					shutil.rmtree(sourceUSER, ignore_errors=True)
				except: pass
				xbmcvfs.delete(UNO)
				xbmc.executeJSONRPC('{"jsonrpc":"2.0", "id":1, "method":"Addons.SetAddonEnabled", "params":{"addonid":"'+addon_id+'", "enabled":true}}')
				xbmc.sleep(500)
				DONE = True
			else:
				xbmcvfs.delete(UNO)
				xbmc.sleep(500)
				DONE = True
		else:
			DONE = True
		if DONE is True: navigator.mainMenu()
	elif mode == 'beatportMain':
		navigator.beatportMain(url)
	elif mode == 'listBeatportVideos':
		navigator.listBeatportVideos(url, type, limit)
	elif mode == 'billboardMain':
		navigator.billboardMain()
	elif mode == 'listBillboardCharts':
		navigator.listBillboardCharts(url)
	elif mode == 'listBillboardArchive':
		navigator.listBillboardArchive(url)
	elif mode == 'listBillboardVideos':
		navigator.listBillboardVideos(url, type, limit)
	elif mode == 'ddpMain':
		navigator.ddpMain(url)
	elif mode == 'listDdpYearCharts':
		navigator.listDdpYearCharts(url)
	elif mode == 'listDdpVideos':
		navigator.listDdpVideos(url, type, limit)
	elif mode == 'hypemMain':
		navigator.hypemMain()
	elif mode == 'listHypemMachine':
		navigator.listHypemMachine()
	elif mode == 'listHypemVideos':
		navigator.listHypemVideos(url, type, limit)
	elif mode == 'itunesMain':
		navigator.itunesMain()
	elif mode == 'listItunesVideos':
		navigator.listItunesVideos(url, type, limit)
	elif mode == 'ocMain':
		navigator.ocMain()
	elif mode == 'listOcVideos':
		navigator.listOcVideos(url, type, limit)
	elif mode == 'spotifyMain':
		navigator.spotifyMain()
	elif mode == 'listSpotifyCC_Countries':
		navigator.listSpotifyCC_Countries(url)
	elif mode == 'listSpotifyCC_Videos':
		navigator.listSpotifyCC_Videos(url, type, limit)
	elif mode == 'SearchDeezer':
		navigator.SearchDeezer()
	elif mode == 'listDeezerSelection':
		navigator.listDeezerSelection(url, extras) 
	elif mode == 'listDeezerVideos':
		navigator.listDeezerVideos(url, type, limit, extras, transmit)
	elif mode == 'playTITLE':
		navigator.playTITLE(url)
	elif mode == 'AddToQueue':
		navigator.AddToQueue()
	elif mode == 'trashCache':
		navigator.trashCache()
	elif mode == 'aConfigs':
		addon.openSettings()

run()
