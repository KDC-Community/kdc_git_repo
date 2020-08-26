# -*- coding: utf-8 -*-
#
# Copyright (C) 2019 RACC
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
from __future__ import unicode_literals

import re
import requests
import time
import json
import string
import random
import uuid
import base64
import datetime
from future.moves.urllib.parse import urljoin, urlencode, urlparse, parse_qs
from base64 import b64decode, b64encode
from binascii import b2a_hex
from hashlib import md5
from collections import OrderedDict
from itertools import chain

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from Cryptodome.Random import get_random_bytes

import warnings

warnings.simplefilter("ignore")


class lntvChannels(object):
    def __init__(self, config, cert, cert_key, user="", device_id="", android_id=""):
        self.implemented = ["0", "23", "33", "34", "38", "44", "48", "51", "52", "54"]
        self.api_url = "https://echo.livenettv.io/data/1/"
        self.api_stamp = ""
        self.api_key = ""
        self.rapi_key = ""
        self.config = config
        self.user = user
        self.s = requests.Session()
        self.s.cert = (cert, cert_key)
        """ app variables """
        self.user_agent = "Dalvik/2.1.0 (Linux; Android 7.1.2; AFTN Build/NS6212)"
        self.player_user_agent = "stagefright/1.2 (Linux;Android 7.1.2)"
        self.apk_build = "36"
        self.apk_version = "4.7 (36)"
        self.apk_name = "com.lnt.androidnettv"
        self.apk_cert = "39:A0:97:F6:A5:98:2E:2E:BE:15:4D:A4:36:8F:94:7A:97:EE:F9:FC"
        self.api_level = "26"
        if device_id:
            self.device_id = device_id
        else:
            self.device_id = str(uuid.uuid4())
        if android_id:
            self.android_id = android_id
        else:
            self.android_id = self.id_generator(16)
        self.device_name = "Amazon AFTN"
        self.server_time = str(int(time.time()) * 1000)

    @staticmethod
    def id_generator(size=8, chars=string.ascii_lowercase + string.digits):
        return "".join(random.choice(chars) for _ in range(size))

    @staticmethod
    def custom_base64(encoded):
        custom_translate = string.maketrans(
            b"zyxwvutsrqponmlkjihgfedcbaZYXWVUTSRQPONMLKJIHGFEDCBA9876543210+/",
            b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/",
        )
        return b64decode(encoded.encode("utf-8").translate(custom_translate)).decode("utf-8")

    @staticmethod
    def fix_auth_date(auth):
        now = datetime.datetime.utcnow()
        _in = list(auth)
        _in.pop(len(_in) + 2 - 3 - int(str(now.year)[:2]))
        _in.pop(len(_in) + 3 - 4 - int(str(now.year)[2:]))
        # java January = 0
        _in.pop(len(_in) + 4 - 5 - (now.month - 1 + 1 + 10))
        _in.pop(len(_in) + 5 - 6 - now.day)
        return "".join(_in)

    @staticmethod
    def modified_header():
        value = 1234567
        return "".join(list(chain(*zip(str(int(time.time()) ^ value), "0123456789"))))

    @staticmethod
    def modified2_header():
        value = 1234567
        s1 = [
            random.choice(string.digits),
            random.choice(string.digits),
            random.choice(string.digits),
        ]
        s2 = [
            random.choice(string.digits),
            random.choice(string.digits),
            random.choice(string.digits),
        ]
        return "".join(s1 + list(chain(*zip(str(int(time.time()) ^ value), "0123456789"))) + s2)

    # live-regex
    def get_stream_18(self, stream):
        headers = {
            "User-Agent": stream.get("user_agent", self.user_agent),
            "Referer": stream.get("referer", ""),
        }
        if "link" in stream:
            url = stream["link"]
        else:
            url = self.custom_base64(stream.get("Bc3RyZWFtX3VybA==")[1:])
        r = self.s.get(url, headers=headers, timeout=5, verify=False)
        r.raise_for_status()
        m3u8 = re.search("['\"](http[^\"']*m3u8[^\"']*)", r.text).group(1)
        return (
            m3u8,
            {
                "verifypeer": "false",
                "User-Agent": stream.get("player_user_agent", self.player_user_agent),
                "Referer": stream.get("player_referer", ""),
            },
        )

    # vod
    def get_stream_21(self, stream):
        stream_url = b64decode(stream.get("Bc3RyZWFtX3VybA==")[1:])
        token_url = self.config["Y2FsYWFtb19pa3Mw"]
        _split_url = stream_url.split("/")
        stream_id = "$".join([_split_url[2][1:], _split_url[-3], _split_url[-2],])
        post_encoded = urlencode({"_": stream_id}) + "&"
        headers = OrderedDict(
            [
                ("Public-Key-Pins", b64encode(self.user.encode("utf-8"))),
                ("Modified", self.modified_header()),
                ("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8"),
                ("User-Agent", self.user_agent),
                ("Connection", "Keep-Alive"),
                ("Accept-Encoding", "gzip"),
                ("Content-Length", str(len(post_encoded))),
            ]
        )
        req = requests.Request("POST", token_url, data=post_encoded)
        prepped = req.prepare()
        prepped.headers = headers
        r = self.s.send(prepped, timeout=5, verify=False)
        r.raise_for_status()

        key = "nck" + self.user[1:6] + self.user_agent[-8:]
        iv = self.user_agent[-8:] + "sdd" + self.user[1:6]

        cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv=iv.encode("utf-8"))
        res = unpad(cipher.decrypt(b64decode(r.text)), 16).decode("utf-8")
        host = b64decode(r.headers["Session"]).decode("utf-8").split("$")
        _split_url[2], _split_url[-3], _split_url[-2] = host
        return (
            "{0}{1}".format("/".join(_split_url), res),
            {"User-Agent": self.player_user_agent},
        )

    # {"streamUrl":"http://$0/hera/aande/playlist.m3u8","token":"23"}
    def get_stream_23(self, stream):
        def fix_auth(auth):
            return "".join([auth[:-92], auth[-91:-56], auth[-55:-46], auth[-45:-36], auth[-35:]])

        stream_url = self.custom_base64(stream.get("Bc3RyZWFtX3VybA==")[1:])
        token_url = self.config["dGhlX3RlYXMw"]
        _split_url = stream_url.split("/")
        stream_id = "$".join([_split_url[2][1:], _split_url[-3], _split_url[-2],])
        post_encoded = urlencode({"_": stream_id}) + "&"
        headers = OrderedDict(
            [
                ("Public-Key-Pins", b64encode(self.user.encode("utf-8"))),
                ("Modified", self.modified_header()),
                ("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8"),
                ("User-Agent", self.user_agent),
                ("Connection", "Keep-Alive"),
                ("Accept-Encoding", "gzip"),
                ("Content-Length", str(len(post_encoded))),
            ]
        )
        req = requests.Request("POST", token_url, data=post_encoded)
        prepped = req.prepare()
        prepped.headers = headers
        r = self.s.send(prepped, timeout=5, verify=False)
        r.raise_for_status()

        key = "nck" + self.user[1:6] + self.user_agent[-8:]
        iv = self.user_agent[-8:] + "sdd" + self.user[1:6]

        cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv=iv.encode("utf-8"))
        res = unpad(cipher.decrypt(b64decode(r.text)), 16).decode("utf-8")
        host = b64decode(r.headers["Session"]).decode("utf-8").split("$")
        _split_url[2], _split_url[-3], _split_url[-2] = host
        return (
            "{0}{1}".format("/".join(_split_url), res),
            {"User-Agent": self.player_user_agent},
        )

    # {"streamUrl":"http://$1/nyx/geokahani/playlist.m3u8","token":"33"}
    def get_stream_33(self, stream):
        def fix_auth(auth):
            return "".join([auth[:-82], auth[-81:-50], auth[-49:-42], auth[-41:-34], auth[-33:]])

        stream_url = self.custom_base64(stream.get("Bc3RyZWFtX3VybA==")[1:])
        token_url = self.config["ZmFtYW50YXJhbmFfdGF0aTAw"]
        _split_url = stream_url.split("/")
        stream_id = "$".join([_split_url[2][1:], _split_url[-3], _split_url[-2],])
        post_encoded = urlencode({"_": stream_id}) + "&"
        headers = OrderedDict(
            [
                ("Public-Key-Pins", b64encode(self.user.encode("utf-8"))),
                ("Modified", self.modified_header()),
                ("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8"),
                ("User-Agent", self.user_agent),
                ("Connection", "Keep-Alive"),
                ("Accept-Encoding", "gzip"),
                ("Content-Length", str(len(post_encoded))),
            ]
        )

        req = requests.Request("POST", token_url, data=post_encoded)
        prepped = req.prepare()
        prepped.headers = headers
        r = self.s.send(prepped, timeout=5, verify=False)
        r.raise_for_status()

        key = "kaf" + self.user[1:6] + self.user_agent[-8:]
        iv = self.user_agent[-8:] + "ios" + self.user[1:6]

        cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv=iv.encode("utf-8"))
        res = fix_auth(unpad(cipher.decrypt(b64decode(r.text)), 16).decode("utf-8"))
        host = b64decode(r.headers["Session"]).decode("utf-8").split("$")
        _split_url[2], _split_url[-3], _split_url[-2] = host
        return (
            "{0}{1}".format("/".join(_split_url), res),
            {"User-Agent": self.player_user_agent},
        )

    # {"streamUrl":"http://sportsvideoline3.pw/player?channel=sportklub|null|null|null|m3u8","token":"34"}
    def get_stream_34(self, stream):
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
        stream_url = self.custom_base64(stream.get("Bc3RyZWFtX3VybA==")[1:])
        page_url = b64decode(stream_url[1:]).split("|")[0]
        headers = {
            "User-Agent": ua,
            "Referer": stream.get("referer"),
        }
        r = requests.get(page_url, headers=headers, timeout=10)
        token_url = self.config["ZGVjcnlwdGV1cl9MaWVu"]
        data = {"stream_url": stream_url, "token": stream.get("AdG9rZW4="), "response_body": r.text}
        post_encoded = urlencode({"data": json.dumps(data, separators=(",", ":"))}) + "&"
        headers = OrderedDict(
            [
                ("Modified", self.modified_header()),
                ("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8"),
                ("User-Agent", self.user_agent),
                ("Connection", "Keep-Alive"),
                ("Accept-Encoding", "gzip"),
                ("Content-Length", str(len(post_encoded))),
            ]
        )
        req = requests.Request("POST", token_url, data=post_encoded)
        prepped = req.prepare()
        prepped.headers = headers
        r = self.s.send(prepped, timeout=5, verify=False)
        r.raise_for_status()
        return (
            r.json().get("stream_url"),
            {"User-Agent": ua, "Referer": stream.get("player_referer")},
        )

    # {"streamUrl":"http://$0/eos/bolent/playlist.m3u8","token":"38"}
    def get_stream_38(self, stream):
        def fix_auth(auth):
            return "".join([auth[:-92], auth[-91:-56], auth[-55:-46], auth[-45:-36], auth[-35:]])

        stream_url = self.custom_base64(stream.get("Bc3RyZWFtX3VybA==")[1:])
        token_url = self.config["YmVsZ2lfMzgw"]
        _split_url = stream_url.split("/")
        stream_id = "$".join([_split_url[2][1:], _split_url[-3], _split_url[-2],])
        post_encoded = urlencode({"_": stream_id}) + "&"
        headers = OrderedDict(
            [
                ("Public-Key-Pins", b64encode(self.user.encode("utf-8"))),
                ("Modified", self.modified_header()),
                ("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8"),
                ("User-Agent", self.user_agent),
                ("Connection", "Keep-Alive"),
                ("Accept-Encoding", "gzip"),
                ("Content-Length", str(len(post_encoded))),
            ]
        )
        req = requests.Request("POST", token_url, data=post_encoded)
        prepped = req.prepare()
        prepped.headers = headers
        r = self.s.send(prepped, timeout=5, verify=False)
        r.raise_for_status()

        key = "kaf" + self.user[1:6] + self.user_agent[-8:]
        iv = self.user_agent[-8:] + "ios" + self.user[1:6]

        cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv=iv.encode("utf-8"))
        res = fix_auth(unpad(cipher.decrypt(b64decode(r.text)), 16).decode("utf-8"))
        host = b64decode(r.headers["Session"]).decode("utf-8").split("$")
        _split_url[2], _split_url[-3], _split_url[-2] = host
        return (
            "{0}{1}".format("/".join(_split_url), res),
            {"User-Agent": self.player_user_agent},
        )

    # {"streamUrl":"http://$0/gaia/aapkacolorshd/playlist.m3u8","token":"44"}
    def get_stream_44(self, stream):
        def fix_auth(auth):
            return "".join([auth[:-92], auth[-91:-56], auth[-55:-46], auth[-45:-36], auth[-35:]])

        stream_url = self.custom_base64(stream.get("Bc3RyZWFtX3VybA==")[1:])
        token_url = self.config["YmVsa2lpdW1uXzk2"]
        _split_url = stream_url.split("/")
        stream_id = "$".join([_split_url[2][1:], _split_url[-3], _split_url[-2],])
        post_encoded = urlencode({"_": stream_id}) + "&"
        headers = OrderedDict(
            [
                ("Public-Key-Pins", b64encode(self.user.encode("utf-8"))),
                ("Modified", self.modified_header()),
                ("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8"),
                ("User-Agent", self.user_agent),
                ("Connection", "Keep-Alive"),
                ("Accept-Encoding", "gzip"),
                ("Content-Length", str(len(post_encoded))),
            ]
        )

        req = requests.Request("POST", token_url, data=post_encoded)
        prepped = req.prepare()
        prepped.headers = headers
        r = self.s.send(prepped, timeout=5, verify=False)
        r.raise_for_status()

        key = "ijk" + self.user[1:6] + self.user_agent[-8:]
        iv = self.user_agent[-8:] + "kms" + self.user[1:6]

        cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv=iv.encode("utf-8"))
        res = self.fix_auth_date(unpad(cipher.decrypt(b64decode(r.text)), 16).decode("utf-8"))
        host = b64decode(r.headers["Session"]).decode("utf-8").split("$")
        _split_url[2], _split_url[-3], _split_url[-2] = host
        return (
            "{0}{1}".format("/".join(_split_url), res),
            {"User-Agent": self.player_user_agent},
        )

    # live-wstream
    def get_stream_45(self, stream):
        ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"
        if "link" in stream:
            stream_url = stream["link"]
        else:
            stream_url = self.custom_base64(stream.get("Bc3RyZWFtX3VybA==")[1:])

        _split_decode = b64decode(stream_url[1:]).split("|")
        page_url = _split_decode[0]
        headers = {
            "User-Agent": ua,
            "Referer": _split_decode[1].split(",")[1],
        }
        r = requests.get(page_url, headers=headers, timeout=10)
        token_url = self.config["bmdhZGVrcmlwUGF0YWxpbmFzazQ1"]
        data = {
            "stream_url": stream_url,
            "token": stream.get("AdG9rZW4=", stream.get("token")),
            "docs": [r.text],
        }
        post_encoded = urlencode({"data": json.dumps(data, separators=(",", ":"))}) + "&"
        headers = OrderedDict(
            [
                ("Accept-Encoding", "gzip"),
                ("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8"),
                ("User-Agent", self.user_agent),
                ("Connection", "Keep-Alive"),
                ("Content-Length", str(len(post_encoded))),
            ]
        )
        req = requests.Request("POST", token_url, data=post_encoded)
        prepped = req.prepare()
        prepped.headers = headers
        r = self.s.send(prepped, timeout=5, verify=False)
        r.raise_for_status()
        return (
            r.json().get("stream_url"),
            {"verifypeer": "false", "User-Agent": ua, "Referer": stream.get("player_referer")},
        )

    # {"streamUrl":"http://$2/hera/aplus/playlist.m3u8","token":"48"}
    def get_stream_48(self, stream):
        stream_url = self.custom_base64(stream.get("Bc3RyZWFtX3VybA==")[1:])
        token_url = self.config["Ym9ya3lsd3VyXzQ4"]
        _split_url = stream_url.split("/")
        stream_id = "$".join([_split_url[2][1:], _split_url[-3], _split_url[-2],])
        post_encoded = urlencode({"_": stream_id}) + "&"
        headers = OrderedDict(
            [
                ("Public-Key-Pins", b64encode(self.user.encode("utf-8"))),
                ("Modified", self.modified2_header()),
                ("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8"),
                ("User-Agent", self.user_agent),
                ("Connection", "Keep-Alive"),
                ("Accept-Encoding", "gzip"),
                ("Content-Length", str(len(post_encoded))),
            ]
        )

        req = requests.Request("POST", token_url, data=post_encoded)
        prepped = req.prepare()
        prepped.headers = headers
        r = self.s.send(prepped, timeout=5, verify=False)
        r.raise_for_status()

        key = "akl" + self.user[1:6] + self.user_agent[-8:]
        iv = self.user_agent[-8:] + "pks" + self.user[1:6]

        cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv=iv.encode("utf-8"))
        res = self.fix_auth_date(unpad(cipher.decrypt(b64decode(r.text)), 16).decode("utf-8"))
        host = b64decode(r.headers["Session"]).decode("utf-8").split("$")
        _split_url[2], _split_url[-3], _split_url[-2] = host
        return (
            "{0}{1}".format("/".join(_split_url), res),
            {"User-Agent": self.player_user_agent},
        )

    # {"streamUrl":"http://$/aryd/playlist.m3u8","token":"51"}
    def get_stream_51(self, stream):
        stream_url = self.custom_base64(stream.get("Bc3RyZWFtX3VybA==")[1:])
        token_url = self.config["cHJlZmVjdHVyZTUx"]
        _split_url = stream_url.split("/")
        stream_id = "$".join([_split_url[2][1:], _split_url[-3], _split_url[-2],])
        headers = OrderedDict(
            [
                (
                    "Public-Key-Pins",
                    b64encode("{0}.{1}".format(self.user, stream_id).encode("utf-8")),
                ),
                ("Modified", self.modified_header()),
                ("Content-Type", "application/x-www-form-urlencoded"),
                ("User-Agent", self.user_agent),
                ("Connection", "Keep-Alive"),
                ("Accept-Encoding", "gzip"),
                ("Content-Length", "0"),
            ]
        )

        req = requests.Request("POST", token_url, data="")
        prepped = req.prepare()
        prepped.headers = headers
        r = self.s.send(prepped, timeout=5, verify=False)
        r.raise_for_status()

        key = self.user[1:7] + "jib" + self.user_agent[-7:]
        iv = self.user_agent[-8:] + "sig" + self.user[1:6]

        cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv=iv.encode("utf-8"))
        res = unpad(cipher.decrypt(b64decode(r.text)), 16).decode("utf-8")
        host = b64decode(r.headers["Session"]).decode("utf-8")
        return (
            "{0}{1}".format(stream_url.replace("$", host), self.fix_auth_date(res)),
            {"User-Agent": self.player_user_agent},
        )

    # {"streamUrl":"http://$/chd/playlist.m3u8","token":"52"}
    def get_stream_52(self, stream):
        stream_url = self.custom_base64(stream.get("Bc3RyZWFtX3VybA==")[1:])
        token_url = self.config["d2lsYXlhaDUx"]
        _split_url = stream_url.split("/")
        stream_id = "$".join([_split_url[2][1:], _split_url[-3], _split_url[-2],])
        headers = OrderedDict(
            [
                (
                    "Public-Key-Pins",
                    b64encode("{0}.{1}".format(self.user, stream_id).encode("utf-8")),
                ),
                ("Modified", self.modified_header()),
                ("Content-Type", "application/x-www-form-urlencoded"),
                ("User-Agent", self.user_agent),
                ("Connection", "Keep-Alive"),
                ("Accept-Encoding", "gzip"),
                ("Content-Length", "0"),
            ]
        )

        req = requests.Request("POST", token_url, data="")
        prepped = req.prepare()
        prepped.headers = headers
        r = self.s.send(prepped, timeout=5, verify=False)
        r.raise_for_status()

        key = self.user[1:7] + "jib" + self.user_agent[-7:]
        iv = self.user_agent[-8:] + "sig" + self.user[1:6]

        cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv=iv.encode("utf-8"))
        res = unpad(cipher.decrypt(b64decode(r.text)), 16).decode("utf-8")
        host = b64decode(r.headers["Session"]).decode("utf-8")
        return (
            "{0}{1}".format(stream_url.replace("$", host), self.fix_auth_date(res)),
            {"User-Agent": self.player_user_agent},
        )

    # {"streamUrl":"http://$:7623/cobra/bein1fr/playlist.m3u8","token":"54"}
    def get_stream_54(self, stream):
        stream_url = self.custom_base64(stream.get("Bc3RyZWFtX3VybA==")[1:])
        token_url = self.config["Ym9rYXJpc2hvbDc3"]
        _split_url = stream_url.split("/")
        stream_id = "$".join([_split_url[2][1:], _split_url[-3], _split_url[-2],])
        headers = OrderedDict(
            [
                ("Content-Type", "application/x-www-form-urlencoded"),
                ("User-Agent", self.user_agent),
                ("Connection", "Keep-Alive"),
                ("Accept-Encoding", "gzip"),
                ("Content-Length", "0"),
            ]
        )

        req = requests.Request("POST", token_url, data="")
        prepped = req.prepare()
        prepped.headers = headers
        r = self.s.send(prepped, timeout=5, verify=False)
        r.raise_for_status()

        _pattern = re.compile("<script>([^<]+)</script>", re.M)
        _split = re.search(_pattern, r.text).group(1).strip().split("\n")
        _upperCase = urlparse(token_url).path.split("/")[1].upper()
        _c = ord(_upperCase[0]) - ord("@")
        _s2 = _split[ord(_upperCase[(len(_upperCase) - 1)]) - ord("@") - 1].split("?")[1]
        _n = len(_s2) - 1
        _in = list(_s2)
        _in.pop(2 + _n - (_c + 3))
        _in.pop(3 + _n - (_c + 11))
        _in.pop(4 + _n - (_c + 19))
        _in.pop(5 + _n - (_c + 27))

        host = b64decode(r.headers["Session"]).decode("utf-8")
        return (
            "{0}?{1}".format(stream_url.replace("$", host), "".join(_in)),
            {"User-Agent": self.player_user_agent},
        )

    @staticmethod
    def rand_aes(plain_bytes):
        rand_key = get_random_bytes(32)
        rand_iv = get_random_bytes(16)
        rand_cipher = AES.new(rand_key, AES.MODE_CBC, iv=rand_iv)
        c_bytes = rand_cipher.encrypt(pad(plain_bytes, 16))
        return b64encode(rand_key + rand_iv + c_bytes)

    def allow_token(self, ver):
        ms_time = str(int(time.time()) * 1000)
        token = [
            md5(ms_time.encode("utf-8")).hexdigest(),
            self.apk_name,
            self.apk_cert,
            self.user,
            ver,  # ?? 3 > new user
        ]
        return b64encode("$".join(token).encode("utf-8"))

    def new_allow_token(self):
        ms_time = str(int(time.time()) * 1000)
        token = [
            md5(ms_time.encode("utf-8")).hexdigest(),
            self.apk_name,
            self.apk_cert,
            ms_time,
            self.user,
            self.apk_build,
        ]
        return b64encode("$".join(token).encode("utf-8"))

    def cache_token(self):
        index = random.randint(0, 9)
        token = [
            self.server_time,
            md5(self.apk_name.encode("utf-8")).hexdigest()[index : index + 16],
            md5(self.apk_cert.encode("utf-8")).hexdigest()[index + 2 : index + 2 + 12],
            md5(self.server_time.encode("utf-8")).hexdigest(),
            str(index),
            "",
        ]
        cipher = AES.new(b"434vwt2tmqkj3trc", AES.MODE_CBC, iv=b"\00" * 16)
        token1 = b64encode(cipher.encrypt(pad("$".join(token).encode("utf-8"), 16)))

        return self.rand_aes(token1)

    def id_token(self):
        ms_time = str(int(time.time() * 1000))
        token_1 = [
            self.api_level.encode("utf-8"),
            base64.encodestring(self.apk_build.encode("utf-8")),
            base64.encodestring(ms_time.encode("utf-8")),
            base64.encodestring("null".encode("utf-8")),
            base64.encodestring(self.device_id.encode("utf-8")),
        ]
        token = [
            md5(ms_time.encode("utf-8")).hexdigest().encode("utf-8"),
            base64.encodestring(self.apk_name.encode("utf-8")),
            base64.encodestring(self.apk_cert.encode("utf-8")),
            base64.encodestring(self.device_name.encode("utf-8")),
            base64.encodestring(b"|".join(token_1)),
        ]
        return base64.encodestring(b"|".join(token)).decode("utf-8")

    def get_api_key(self):
        index_url = self.config["YXBpS2V5TGluazQ2"]
        headers = OrderedDict(
            [
                ("Accept-Encoding", "gzip"),
                ("User-Agent", self.user_agent),
                ("Connection", "Keep-Alive"),
            ]
        )
        req = requests.Request("GET", index_url)
        prepped = req.prepare()
        prepped.headers = headers
        r = self.s.send(prepped, timeout=5, verify=False)
        r.raise_for_status()
        self.server_time = str(int(time.time()) * 1000)

        headers = OrderedDict(
            [
                ("Accept-Encoding", "gzip"),
                ("User-Agent", self.user_agent),
                ("Cache-Control", self.cache_token()),
                ("ALLOW", self.allow_token("3")),
                ("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8"),
                ("Connection", "Keep-Alive"),
            ]
        )
        req = requests.Request("POST", index_url)
        prepped = req.prepare()
        prepped.headers = headers
        r = self.s.send(prepped, timeout=5, verify=False)
        r.raise_for_status()

        if "ETag" in r.headers:
            tag_key = r.headers["ETag"].split(":")
            self.api_key = tag_key[0]
            self.api_stamp, self.api_url = b64decode(tag_key[1]).decode("utf-8").split("|")
            self.rapi_key = r.json(strict=False).get("funguo")
            return self.api_key

    def get_user_id(self):
        adduser_url = urljoin(self.api_url, "adduserinfo.nettv/")

        post_data = {
            "device_id": "0" * 16,
            "key": self.rapi_key,
            "device_name": self.device_name,
            "api_level": self.api_level,
            "version": self.apk_version,
            "id": self.id_token(),
            "time": self.server_time,
            "android_id": self.android_id,
            "state": "{0, 2}",
            "pro": "true",
            "detail": '{"DetectTestKeys":0,"DetectRootManagmentApps":0,"DetectPotentiallyDangerousApps":0,"DetectRootCloakingApps":0,"CheckForSuBinary":0,"CheckForDangerousProps":0,"CheckForRWPaths":0,"CheckForMagiskFiles":0,"CheckForMagiskManagerApp":0,"CheckSuExists":0}',
            "retail": '{"DetectNox":0,"DetectQemu":0,"DetectQemuDriver":0,"DetectEmulator":0}',
        }
        post_dump = json.dumps(post_data, separators=(",", ":")).encode("utf-8")
        post_encoded = urlencode({"_": self.rand_aes(post_dump)}) + "&"
        content_length = len(post_encoded)
        headers = OrderedDict(
            [
                ("Referer", self.config["SXNpc2VrZWxvX3Nlc2lzdGltdV95ZXppbm9tYm9sbzAw"]),
                ("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8"),
                ("User-Agent", self.user_agent),
                ("Connection", "Keep-Alive"),
                ("Accept-Encoding", "gzip"),
                ("Content-Length", str(content_length)),
            ]
        )
        req = requests.Request("POST", adduser_url, data=post_encoded)
        prepped = self.s.prepare_request(req)
        prepped.headers = headers
        r = self.s.send(prepped, timeout=5, verify=False)
        r.raise_for_status()

        user_id = r.json()
        self.user = user_id.get("user_id")
        return user_id

    def get_channel_list(self):
        list_url = urljoin(self.api_url, "list.nettv/")
        post_data = {
            "key": self.rapi_key,
            "user_id": self.user,
            "version": self.apk_build,
            "check": "13",
            "time": self.server_time,
            "state": "{0, 2}",
            "pro": "true",
            "detail": '{"DetectTestKeys":0,"DetectRootManagmentApps":0,"DetectPotentiallyDangerousApps":0,"DetectRootCloakingApps":0,"CheckForSuBinary":0,"CheckForDangerousProps":0,"CheckForRWPaths":0,"CheckForMagiskFiles":0,"CheckForMagiskManagerApp":0,"CheckSuExists":0}',
            "retail": '{"DetectNox":0,"DetectQemu":0,"DetectQemuDriver":0,"DetectEmulator":0}',
        }
        post_dump = json.dumps(post_data, separators=(",", ":")).encode("utf-8")
        post_encoded = urlencode({"_": self.rand_aes(post_dump)}) + "&"
        content_length = len(post_encoded)
        headers = OrderedDict(
            [
                ("Referer", self.config["SXNpc2VrZWxvX3Nlc2lzdGltdV95ZXppbm9tYm9sbzAw"]),
                ("Meta", self.api_key),
                ("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8"),
                ("User-Agent", self.user_agent),
                ("Connection", "Keep-Alive"),
                ("Accept-Encoding", "gzip"),
                ("Content-Length", str(content_length)),
            ]
        )
        req = requests.Request("POST", list_url, data=post_encoded)
        prepped = self.s.prepare_request(req)
        prepped.headers = headers
        r = self.s.send(prepped, timeout=5, verify=False)
        r.raise_for_status()
        return r.json()

    def get_vod_list(self):
        list_url = urljoin(self.api_url, "vods.nettv/")
        post_data = {
            "user_id": self.user,
            "check": "5",
            "version": self.apk_build,
            "key": self.rapi_key,
        }
        post_encoded = urlencode(post_data) + "&"
        content_length = len(post_encoded)
        headers = OrderedDict(
            [
                ("Referer", self.config["SXNpc2VrZWxvX3Nlc2lzdGltdV95ZXppbm9tYm9sbzAw"]),
                ("Meta", self.api_key),
                ("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8"),
                ("User-Agent", self.user_agent),
                ("Connection", "Keep-Alive"),
                ("Accept-Encoding", "gzip"),
                ("Content-Length", str(content_length)),
            ]
        )
        req = requests.Request("POST", list_url, data=post_encoded)
        prepped = self.s.prepare_request(req)
        prepped.headers = headers
        r = self.s.send(prepped, timeout=5, verify=False)
        r.raise_for_status()
        return r.json()

    def get_live_list(self):
        list_url = urljoin(self.api_url, "live.nettv/")
        post_data = {"ALLOW": self.new_allow_token()}
        post_encoded = urlencode(post_data) + "&"
        content_length = len(post_encoded)
        headers = OrderedDict(
            [
                ("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8"),
                ("User-Agent", self.user_agent),
                ("Connection", "Keep-Alive"),
                ("Accept-Encoding", "gzip"),
                ("Content-Length", str(content_length)),
            ]
        )
        req = requests.Request("POST", list_url, data=post_encoded)
        prepped = self.s.prepare_request(req)
        prepped.headers = headers
        r = self.s.send(prepped, timeout=5, verify=False)
        r.raise_for_status()
        return r.json()

    def get_live_link(self, link):
        post_data = {"v": parse_qs(urlparse(link).query)["id"][0], "ALLOW": self.new_allow_token()}
        post_encoded = urlencode(post_data) + "&"
        content_length = len(post_encoded)
        headers = OrderedDict(
            [
                ("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8"),
                ("User-Agent", self.user_agent),
                ("Connection", "Keep-Alive"),
                ("Accept-Encoding", "gzip"),
                ("Content-Length", str(content_length)),
            ]
        )
        req = requests.Request("POST", link, data=post_encoded)
        prepped = self.s.prepare_request(req)
        prepped.headers = headers
        r = self.s.send(prepped, timeout=5, verify=False)
        r.raise_for_status()
        print(repr(r.text.strip()))
        return json.loads(b64decode(r.text.strip()[3:]))
