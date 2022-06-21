#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc,xbmcgui, xbmcaddon,os,sys


def __fix_encoding__(path):
    if sys.version_info.major == 2:

        if sys.platform.startswith('win'):return path.decode('utf-8')
        else:return path.decode('utf-8').encode('ISO-8859-1')

    elif sys.version_info.major == 3:return path

__addon__ = xbmcaddon.Addon()
#addon_path = addon.getAddonInfo('path')
__addon_path__ = __fix_encoding__(__addon__.getAddonInfo('path'))

name = "Krawall Radio"
url = "http://144.91.86.171:9977"
image = os.path.join(__addon_path__,"resources/icon.png")

liz=xbmcgui.ListItem(name, path=url); liz.setInfo( type="audio", infoLabels={ "Title": name } ) ;liz.setArt({ 'thumb': image , 'icon' :image })
xbmc.Player ().play(url, liz, True)