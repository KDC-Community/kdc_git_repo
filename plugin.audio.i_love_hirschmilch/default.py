# -*- coding: utf-8 -*-
import xbmc
import xbmcgui
import xbmcaddon
import xbmcplugin
import os
import sys


addon = xbmcaddon.Addon()
addon_path = addon.getAddonInfo('path').decode('utf-8')
pluginHandle = int(sys.argv[1])

name = "[B][COLOR antiquewhite]I [COLOR darkred] Love [COLOR antiquewhite] geschmeidigen Chillout [/B][/COLOR]"
url = "https://bit.ly/2LPzJno"
iconimage = os.path.join(addon_path,"chillicon.png")
liz=xbmcgui.ListItem(name, iconImage=iconimage,thumbnailImage=iconimage)
liz.setInfo( type="audio", infoLabels={ "Title": name } )
xbmcplugin.addDirectoryItem(pluginHandle, url, liz)

name = "[B][COLOR antiquewhite]I [COLOR darkred] Love [COLOR antiquewhite] kernigen Electro [/B][/COLOR]"
url = "https://bit.ly/35hm7IZ"
iconimage = os.path.join(addon_path,"electroicon.png")
liz=xbmcgui.ListItem(name, iconImage=iconimage,thumbnailImage=iconimage)
liz.setInfo( type="audio", infoLabels={ "Title": name } )
xbmcplugin.addDirectoryItem(pluginHandle, url, liz)

name = "[B][COLOR antiquewhite]I [COLOR darkred] Love [COLOR antiquewhite] Prog - House [/B][/COLOR]"
url = "https://bit.ly/35h33uz"
iconimage = os.path.join(addon_path,"proghouseicon.png")
liz=xbmcgui.ListItem(name, iconImage=iconimage,thumbnailImage=iconimage)
liz.setInfo( type="audio", infoLabels={ "Title": name } )
xbmcplugin.addDirectoryItem(pluginHandle, url, liz)

name = "[B][COLOR antiquewhite]I [COLOR darkred] Love [COLOR antiquewhite] Progressive Itsche [/B][/COLOR]"
url = "https://bit.ly/2IppnIG"
iconimage = os.path.join(addon_path,"progressiveicon.png")
liz=xbmcgui.ListItem(name, iconImage=iconimage,thumbnailImage=iconimage)
liz.setInfo( type="audio", infoLabels={ "Title": name } )
xbmcplugin.addDirectoryItem(pluginHandle, url, liz)

name = "[B][COLOR antiquewhite]I [COLOR darkred] Love [COLOR antiquewhite] Psytrance und UmpaLumPa [/B][/COLOR]"
url = "https://bit.ly/2njb4y1"
iconimage = os.path.join(addon_path,"psyicon.png")
liz=xbmcgui.ListItem(name, iconImage=iconimage,thumbnailImage=iconimage)
liz.setInfo( type="audio", infoLabels={ "Title": name } )
xbmcplugin.addDirectoryItem(pluginHandle, url, liz)

name = "[B][COLOR antiquewhite]I [COLOR darkred] Love [COLOR antiquewhite] Fettich geölten Techno [/B][/COLOR]"
url = "https://bit.ly/3acMXp8"
iconimage = os.path.join(addon_path,"technoicon.png")
liz=xbmcgui.ListItem(name, iconImage=iconimage,thumbnailImage=iconimage)
liz.setInfo( type="audio", infoLabels={ "Title": name } )
xbmcplugin.addDirectoryItem(pluginHandle, url, liz)

xbmcplugin.endOfDirectory(pluginHandle)
