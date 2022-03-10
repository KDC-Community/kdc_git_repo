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

name = "[B][COLOR antiquewhite]=============== [COLOR darkred] Club Zone [COLOR antiquewhite]=======================[/B][/COLOR]"
url = "ext"
iconimage = os.path.join(addon_path,"technoicon.png")
liz=xbmcgui.ListItem(name, iconImage=iconimage,thumbnailImage=iconimage)
liz.setInfo( type="audio", infoLabels={ "Title": name } )
xbmcplugin.addDirectoryItem(pluginHandle, url, liz)

name = "[B][COLOR antiquewhite]|||===  Audio Stream [COLOR lime] Clubbing TV [COLOR antiquewhite]===|||[/B][/COLOR]"
url = "https://bit.ly/3ufFvVY"
iconimage = os.path.join(addon_path,"clubbing.png")
liz=xbmcgui.ListItem(name, iconImage=iconimage,thumbnailImage=iconimage)
liz.setInfo( type="audio", infoLabels={ "Title": name } )
xbmcplugin.addDirectoryItem(pluginHandle, url, liz)

name = "[B][COLOR antiquewhite]|||===  Video Stream [COLOR lime] Clubbing TV [COLOR antiquewhite]===|||[/B][/COLOR]"
url = "https://bit.ly/346JARB"
iconimage = os.path.join(addon_path,"clubbing.png")
liz=xbmcgui.ListItem(name, iconImage=iconimage,thumbnailImage=iconimage)
liz.setInfo( type="video", infoLabels={ "Title": name } )
xbmcplugin.addDirectoryItem(pluginHandle, url, liz)

name = "[B][COLOR antiquewhite]|||===  Youtube Test Ohne ID und gedöns [COLOR lime] Meditation [COLOR antiquewhite]===|||[/B][/COLOR]"
url = "https://c10.x2convert.com/xbase/eusf40.x2convert.com/xcfiles//files/2021/3/25/happiness_frequency_serotonin_dopamine_endorphin_release_music_binaural_beats_meditation_music_6288812994547340732.mp3"
iconimage = os.path.join(addon_path,"chillicon.png")
liz=xbmcgui.ListItem(name, iconImage=iconimage,thumbnailImage=iconimage)
liz.setInfo( type="audio", infoLabels={ "Title": name } )
xbmcplugin.addDirectoryItem(pluginHandle, url, liz)

name = "[B][COLOR antiquewhite]|||===  Musikvideo Stream [COLOR lime] ext [COLOR antiquewhite]===|||[/B][/COLOR]"
url = "ext"
iconimage = os.path.join(addon_path,"technoicon.png")
liz=xbmcgui.ListItem(name, iconImage=iconimage,thumbnailImage=iconimage)
liz.setInfo( type="audio", infoLabels={ "Title": name } )
xbmcplugin.addDirectoryItem(pluginHandle, url, liz)

xbmcplugin.endOfDirectory(pluginHandle)
