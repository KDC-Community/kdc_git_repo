# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 RACC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import unicode_literals, absolute_import

import sys
from xbmcgui import ListItem
from kodi_six import xbmc, xbmcgui, xbmcaddon, xbmcplugin
from routing import Plugin

import os
import io
import time
import json
from future.moves.urllib.parse import urlencode
from base64 import b64decode

from datetime import datetime
from dateutil.parser import parse
from dateutil.tz import gettz, tzlocal

from resources.lib.lntv_config_backendless import lntvConfig
from resources.lib.lntv_channels import lntvChannels


addon = xbmcaddon.Addon()
plugin = Plugin()
plugin.name = addon.getAddonInfo("name")
user_agent = "Dalvik/2.1.0 (Linux; U; Android 5.1.1; AFTT Build/LVY48F)"
USER_DATA_DIR = xbmc.translatePath(addon.getAddonInfo("profile"))
ADDON_DATA_DIR = xbmc.translatePath(addon.getAddonInfo("path"))
RESOURCES_DIR = os.path.join(ADDON_DATA_DIR, "resources")
if not os.path.exists(USER_DATA_DIR):
    os.makedirs(USER_DATA_DIR)
app_config_file = os.path.join(USER_DATA_DIR, "config.json")
channel_list_file = os.path.join(USER_DATA_DIR, "channels.json")
live_list_file = os.path.join(USER_DATA_DIR, "live.json")
vod_list_file = os.path.join(USER_DATA_DIR, "vod.json")

cert_file = os.path.join(RESOURCES_DIR, "com.lnt.androidnettv.crt")
cert_key_file = os.path.join(RESOURCES_DIR, "com.lnt.androidnettv.key")

cache_time = int(addon.getSetting("cache_time") or "0")
data_time = int(addon.getSetting("data_time36") or "0")
user_id = addon.getSetting("user_id36")
device_id = addon.getSetting("device_id36")
android_id = addon.getSetting("android_id36")
live_data_time = int(addon.getSetting("live_data_time36") or "0")
vod_data_time = int(addon.getSetting("vod_data_time36") or "0")

current_time = int(time.time())
if current_time - data_time > cache_time * 60 * 60:
    try:
        new_config = lntvConfig()
        app_config = new_config.get_data()
        with io.open(app_config_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(app_config, indent=2, sort_keys=True, ensure_ascii=False))
    except:
        with io.open(app_config_file, "r", encoding="utf-8") as f:
            app_config = json.loads(f.read())
    try:
        new_channels = lntvChannels(
            app_config, cert_file, cert_key_file, user_id, device_id, android_id
        )
        new_channels.get_api_key()
        new_channels.get_user_id()
        channel_list = new_channels.get_channel_list()
        addon.setSetting("user_id36", new_channels.user)
        addon.setSetting("device_id36", new_channels.device_id)
        addon.setSetting("android_id36", new_channels.android_id)
        with io.open(channel_list_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(channel_list, indent=2, sort_keys=True, ensure_ascii=False))
    except:
        with io.open(channel_list_file, "r", encoding="utf-8") as f:
            channel_list = json.loads(f.read())
    addon.setSetting("data_time36", str(int(time.time())))
else:
    try:
        with io.open(app_config_file, "r", encoding="utf-8") as f:
            app_config = json.loads(f.read())
    except IOError:
        app_config = ""
    new_channels = lntvChannels(
        app_config, cert_file, cert_key_file, user_id, device_id, android_id
    )
    try:
        with io.open(channel_list_file, "r", encoding="utf-8") as f:
            channel_list = json.loads(f.read())
    except IOError:
        channel_list = ""

try:
    locale_timezone = json.loads(
        xbmc.executeJSONRPC(
            '{"jsonrpc": "2.0", "method": "Settings.GetSettingValue", "params": {"setting": "locale.timezone"}, "id": 1}'
        )
    )
    if "result" in locale_timezone:
        if locale_timezone["result"]["value"]:
            local_tzinfo = gettz(locale_timezone["result"]["value"])
        else:
            local_tzinfo = tzlocal()
    else:
        local_tzinfo = tzlocal()
except:
    local_tzinfo = ""


def time_from_zone(timestring, newfrmt="default", in_zone="UTC"):
    try:
        if newfrmt == "default":
            newfrmt = xbmc.getRegion("time").replace(":%S", "")
        in_time = parse(timestring)
        in_time_with_timezone = in_time.replace(tzinfo=gettz(in_zone))
        local_time = in_time_with_timezone.astimezone(local_tzinfo)
        return local_time.strftime(newfrmt)
    except:
        return timestring


@plugin.route("/")
def root():
    categories = channel_list.get("categories_list")
    list_items = []

    li = ListItem("[Live]", offscreen=True)
    url = plugin.url_for(list_live)
    list_items.append((url, li, True))

    for c in categories:
        li = ListItem(c.get("cat_name"), offscreen=True)
        url = plugin.url_for(list_channels, cat=c.get("cat_id"))
        list_items.append((url, li, True))

    li = ListItem("[VOD]", offscreen=True)
    url = plugin.url_for(vod)
    list_items.append((url, li, True))

    xbmcplugin.addDirectoryItems(plugin.handle, list_items)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route("/vod")
def vod():
    if current_time - vod_data_time > cache_time * 60 * 60:
        new_channels.get_api_key()
        vod_data = new_channels.get_vod_list()
        with io.open(vod_list_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(vod_data, indent=2, sort_keys=True, ensure_ascii=False))
        addon.setSetting("vod_data_time36", str(int(time.time())))
    else:
        with io.open(vod_list_file, "r", encoding="utf-8") as f:
            vod_data = json.loads(f.read())

    categories = vod_data.get("categories_list")
    list_items = []

    for c in categories:
        li = ListItem(c.get("cat_name"), offscreen=True)
        url = plugin.url_for(vod_list, cat=c.get("cat_id"))
        list_items.append((url, li, True))

    xbmcplugin.addDirectoryItems(plugin.handle, list_items)
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route("/vod_list/<cat>")
def vod_list(cat=None):
    if current_time - vod_data_time > cache_time * 60 * 60:
        new_channels.get_api_key()
        vod_data = new_channels.get_vod_list()
        with io.open(vod_list_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(vod_data, indent=2, sort_keys=True, ensure_ascii=False))
        addon.setSetting("vod_data_time36", str(int(time.time())))
    else:
        with io.open(vod_list_file, "r", encoding="utf-8") as f:
            vod_data = json.loads(f.read())

    list_items = []
    for channel in vod_data.get("eY2hhbm5lbHNfbGlzdA=="):
        if channel.get("cat_id") == cat:
            title = b64decode(channel.get("ZY19uYW1l")[:-1])
            icon = b64decode(channel.get("abG9nb191cmw=")[1:])
            image = "{0}|{1}".format(icon, urlencode({"User-Agent": user_agent}))
            c_id = channel.get("rY19pZA==")

            li = ListItem(title, offscreen=True)
            li.setProperty("IsPlayable", "true")
            li.setInfo(type="Video", infoLabels={"Title": title, "mediatype": "video"})
            li.setArt({"thumb": image, "icon": image})
            li.setContentLookup(False)
            url = plugin.url_for(play_vod, c_id=c_id)
            list_items.append((url, li, False))

    xbmcplugin.addDirectoryItems(plugin.handle, list_items)
    xbmcplugin.setContent(plugin.handle, "videos")
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route("/list_live")
def list_live():
    if current_time - live_data_time > 30 * 60:
        live_data = new_channels.get_live_list()
        with io.open(live_list_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(live_data, indent=2, sort_keys=True, ensure_ascii=False))
        addon.setSetting("live_data_time36", str(int(time.time())))
    else:
        with io.open(live_list_file, "r", encoding="utf-8") as f:
            live_data = json.loads(f.read())

    list_items = []
    for day, events in live_data.items():
        for event in events:
            if len(event["channel_list"]) == 0:
                continue
            event_time = time_from_zone(
                datetime.utcfromtimestamp(int(event["start"])).strftime("%c"), "%Y-%m-%d %H:%M"
            )
            title = "[{0}] {1}".format(event_time, event["title"])
            li = ListItem(title, offscreen=True)
            li.setProperty("IsPlayable", "true")
            li.setInfo(type="Video", infoLabels={"Title": title, "mediatype": "video"})
            li.setContentLookup(False)
            url = plugin.url_for(event_resolve, title=event["title"].encode("utf-8"))
            list_items.append((url, li, False))

    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL)
    xbmcplugin.addDirectoryItems(plugin.handle, list_items)
    xbmcplugin.setContent(plugin.handle, "videos")
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route("/event_resolve.pvr")
def event_resolve():
    def find_event(data, title):
        for day, events in live_data.items():
            for event in events:
                if event["title"] == title:
                    return event

    with io.open(live_list_file, "r", encoding="utf-8") as f:
        live_data = json.loads(f.read())

    live_event = find_event(live_data, plugin.args["title"][0])

    if len(live_event["channel_list"]) > 1:
        select_list = []
        for channel in live_event["channel_list"]:
            select_list.append(channel["c_name"])
        dialog = xbmcgui.Dialog()
        ret = dialog.select("Choose Stream", select_list)
        selected_channel = live_event["channel_list"][ret]
    else:
        selected_channel = live_event["channel_list"][0]

    link = selected_channel["links"][0]
    stream = new_channels.get_live_link(link)

    if str(stream["token"]) == "18":
        resolved_stream = new_channels.get_stream_18(stream)
    elif str(stream["token"]) == "45":
        resolved_stream = new_channels.get_stream_45(stream)
    elif str(stream["token"]) == "0":
        resolved_stream = (
            stream["link"],
            {
                "verifypeer": "false",
                "User-Agent": stream["player_user_agent"],
                "Referer": stream["player_referer"],
            },
        )

    media_url = resolved_stream[0]
    media_headers = resolved_stream[1]
    if "m3u8" in media_url:
        if addon.getSetting("inputstream") == "true":
            li = ListItem(path=media_url)
            li.setMimeType("application/vnd.apple.mpegurl")
            li.setProperty("inputstreamaddon", "inputstream.adaptive")
            li.setProperty("inputstream.adaptive.manifest_type", "hls")
            li.setProperty("inputstream.adaptive.stream_headers", urlencode(media_headers))
            li.setProperty("inputstream.adaptive.license_key", "|" + urlencode(media_headers))
            li.setMimeType("application/vnd.apple.mpegurl")
            li.setContentLookup(False)
        else:
            li = ListItem(
                path="{0}|{1}".format(media_url, urlencode(media_headers))
            )
            li.setMimeType("application/vnd.apple.mpegurl")
            li.setContentLookup(False)
    else:
        li = ListItem(path="{0}|{1}".format(media_url, urlencode(media_headers)))

    xbmcplugin.setResolvedUrl(plugin.handle, True, li)


@plugin.route("/list_channels/<cat>")
def list_channels(cat=None):
    list_items = []
    for channel in channel_list.get("eY2hhbm5lbHNfbGlzdA=="):
        if channel.get("cat_id") == cat:
            if (
                len(
                    [
                        stream
                        for stream in channel.get("Qc3RyZWFtX2xpc3Q=")
                        if stream.get("AdG9rZW4=", "0") in new_channels.implemented
                    ]
                )
                == 0
            ):
                continue

            title = new_channels.custom_base64(channel.get("ZY19uYW1l"))
            icon = new_channels.custom_base64(channel.get("abG9nb191cmw=")[1:])
            image = "{0}|{1}".format(icon, urlencode({"User-Agent": user_agent}))
            c_id = channel.get("rY19pZA==")

            li = ListItem(title, offscreen=True)
            li.setProperty("IsPlayable", "true")
            li.setInfo(type="Video", infoLabels={"Title": title, "mediatype": "video"})
            li.setArt({"thumb": image, "icon": image})
            li.setContentLookup(False)
            url = plugin.url_for(play, c_id=c_id)
            list_items.append((url, li, False))

    xbmcplugin.addDirectoryItems(plugin.handle, list_items)
    xbmcplugin.setContent(plugin.handle, "videos")
    xbmcplugin.endOfDirectory(plugin.handle)


@plugin.route("/play/<c_id>/play.pvr")
def play(c_id):
    for channel in channel_list.get("eY2hhbm5lbHNfbGlzdA=="):
        if channel.get("rY19pZA==") == c_id:
            selected_channel = channel
            break

    # stream_list = selected_channel.get("Qc3RyZWFtX2xpc3Q=")
    stream_list = [
        stream
        for stream in selected_channel.get("Qc3RyZWFtX2xpc3Q=")
        if stream.get("AdG9rZW4=", "0") in new_channels.implemented
    ]
    if len(stream_list) > 1:
        select_list = []
        for stream in stream_list:
            select_list.append(
                "Link {0} {1}".format(
                    stream.get("AdG9rZW4=", "0"), stream.get("cc3RyZWFtX2lk", "0")
                )
            )

        dialog = xbmcgui.Dialog()
        ret = dialog.select("Choose Stream", select_list)
        selected_stream = stream_list[ret]
    else:
        selected_stream = stream_list[0]

    # [ "0", "23", "33", "34", "38", "44", "48", "51", "52", "54"]
    if "AdG9rZW4=" in selected_stream:
        if selected_stream.get("AdG9rZW4=") == "18":
            resolved_stream = new_channels.get_stream_18(selected_stream)
        elif selected_stream.get("AdG9rZW4=") == "23":
            resolved_stream = new_channels.get_stream_23(selected_stream)
        elif selected_stream.get("AdG9rZW4=") == "33":
            resolved_stream = new_channels.get_stream_33(selected_stream)
        elif selected_stream.get("AdG9rZW4=") == "34":
            resolved_stream = new_channels.get_stream_34(selected_stream)
        elif selected_stream.get("AdG9rZW4=") == "38":
            resolved_stream = new_channels.get_stream_38(selected_stream)
        elif selected_stream.get("AdG9rZW4=") == "44":
            resolved_stream = new_channels.get_stream_44(selected_stream)
        elif selected_stream.get("AdG9rZW4=") == "48":
            resolved_stream = new_channels.get_stream_48(selected_stream)
        elif selected_stream.get("AdG9rZW4=") == "51":
            resolved_stream = new_channels.get_stream_51(selected_stream)
        elif selected_stream.get("AdG9rZW4=") == "52":
            resolved_stream = new_channels.get_stream_52(selected_stream)
        elif selected_stream.get("AdG9rZW4=") == "54":
            resolved_stream = new_channels.get_stream_54(selected_stream)
    else:
        resolved_stream = (
            new_channels.custom_base64(selected_stream.get("Bc3RyZWFtX3VybA==")[1:]),
            {"User-Agent": user_agent},
        )

    title = new_channels.custom_base64(selected_channel.get("ZY19uYW1l"))
    icon = new_channels.custom_base64(selected_channel.get("abG9nb191cmw=")[1:])
    image = "{0}|{1}".format(icon, urlencode({"User-Agent": user_agent}))

    media_url = resolved_stream[0]
    media_headers = resolved_stream[1]
    if "playlist.m3u8" in media_url:
        if addon.getSetting("inputstream") == "true":
            li = ListItem(title, path=media_url)
            li.setArt({"thumb": image, "icon": image})
            li.setMimeType("application/vnd.apple.mpegurl")
            li.setProperty("inputstreamaddon", "inputstream.adaptive")
            li.setProperty("inputstream.adaptive.manifest_type", "hls")
            li.setProperty("inputstream.adaptive.stream_headers", urlencode(media_headers))
            li.setMimeType("application/vnd.apple.mpegurl")
            li.setContentLookup(False)
        else:
            li = ListItem(
                title, path="{0}|{1}".format(media_url, urlencode(media_headers))
            )
            li.setArt({"thumb": image, "icon": image})
            li.setMimeType("application/vnd.apple.mpegurl")
            li.setContentLookup(False)
    else:
        li = ListItem(
            title, path="{0}|{1}".format(media_url, urlencode(media_headers))
        )
        li.setArt({"thumb": image, "icon": image})

    xbmcplugin.setResolvedUrl(plugin.handle, True, li)


@plugin.route("/play_vod/<c_id>/play.pvr")
def play_vod(c_id):
    with io.open(vod_list_file, "r", encoding="utf-8") as f:
        vod_data = json.loads(f.read())

    for channel in vod_data.get("eY2hhbm5lbHNfbGlzdA=="):
        if channel.get("rY19pZA==") == c_id:
            selected_channel = channel
            break

    stream_list = selected_channel.get("Qc3RyZWFtX2xpc3Q=")
    if len(stream_list) > 1:
        select_list = []
        for stream in stream_list:
            select_list.append(stream.get("quality", "0"))
        dialog = xbmcgui.Dialog()
        ret = dialog.select("Choose Stream", select_list)
        selected_stream = stream_list[ret]
    else:
        selected_stream = stream_list[0]

    # [ "0", "21", "127"]
    if "AdG9rZW4=" in selected_stream:
        if b64decode(selected_stream.get("AdG9rZW4=")[:-1]) == b"21":
            resolved_stream = new_channels.get_stream_21(selected_stream)
        elif b64decode(selected_stream.get("AdG9rZW4=")[:-1]) == b"127":
            resolved_stream = new_channels.get_stream_21(selected_stream)
    else:
        resolved_stream = (
            b64decode(selected_stream.get("Bc3RyZWFtX3VybA==")[1:]),
            {"User-Agent": user_agent},
        )

    title = b64decode(selected_channel.get("ZY19uYW1l")[:-1])
    icon = b64decode(selected_channel.get("abG9nb191cmw=")[1:])
    image = "{0}|{1}".format(icon, urlencode({"User-Agent": user_agent}))

    media_url = resolved_stream[0]
    media_headers = resolved_stream[1]
    if "playlist.m3u8" in media_url:
        if addon.getSetting("inputstream") == "true":
            li = ListItem(title, path=media_url)
            li.setArt({"thumb": image, "icon": image})
            li.setMimeType("application/vnd.apple.mpegurl")
            li.setProperty("inputstreamaddon", "inputstream.adaptive")
            li.setProperty("inputstream.adaptive.manifest_type", "hls")
            li.setProperty("inputstream.adaptive.stream_headers", urlencode(media_headers))
            li.setMimeType("application/vnd.apple.mpegurl")
            li.setContentLookup(False)
        else:
            li = ListItem(
                title, path="{0}|{1}".format(media_url, urlencode(media_headers))
            )
            li.setArt({"thumb": image, "icon": image})
            li.setMimeType("application/vnd.apple.mpegurl")
            li.setContentLookup(False)
    else:
        li = ListItem(
            title, path="{0}|{1}".format(media_url, urlencode(media_headers))
        )
        li.setArt({"thumb": image, "icon": image})

    xbmcplugin.setResolvedUrl(plugin.handle, True, li)


if __name__ == "__main__":
    plugin.run(sys.argv)
