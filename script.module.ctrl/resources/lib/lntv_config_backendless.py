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

import pyamf
from pyamf import remoting
from pyamf.flex import messaging
import requests
import json
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from base64 import b64decode


class lntvConfig(object):
    def __init__(self, user=""):
        self.user = user
        self.url = "https://api.backendless.com/762F7A10-3072-016F-FF64-33280EE6EC00/E9A27666-CD62-10CD-FF05-ED45B12ABE00/binary"
        self.s = requests.Session()
        self.s.headers.update(
            {"User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1; AFTM Build/LMY47O)"}
        )
        self.config = {}
        self.key = b"kekekekekkekekek"

    @staticmethod
    def b64custom(s):
        return b64decode(s[1:])

    def get_config_key(self):
        cipher = AES.new(b"fwewokemlesdsdsd", AES.MODE_CBC, iv=b"\00" * 16)
        self.key = unpad(cipher.decrypt(b64decode(self.config["QXBwX2ludmVudG9y"])), 16)
        return self.key

    def decrypt_config_value(self, key):
        cipher = AES.new(self.key, AES.MODE_CBC, iv=b"896C5F41D8F2A22A")
        self.config[key] = unpad(cipher.decrypt(b64decode(self.config[key])), 16).decode("utf-8")
        return self.config[key]

    def get_data(self):
        data = {
            "clientId": None,
            "destination": "GenericDestination",
            "correlationId": None,
            "source": "com.backendless.services.persistence.PersistenceService",
            "operation": "first",
            "messageRefType": None,
            "headers": {"application-type": "ANDROID", "api-version": "1.0"},
            "timestamp": 0,
            "body": ["ConfigDelta"],
            "timeToLive": 0,
            "messageId": None,
        }
        msg = messaging.RemotingMessage(**data)
        req = remoting.Request(target="null", body=[msg])
        ev = remoting.Envelope(pyamf.AMF3)
        ev["null"] = req
        resp = requests.post(
            self.url,
            data=remoting.encode(ev).getvalue(),
            headers={"Content-Type": "application/x-amf"},
        )
        resp_msg = remoting.decode(resp.content)
        config = json.dumps(resp_msg.bodies[0][1].body.body, default=lambda obj: repr(obj))
        self.config = json.loads(config)
        for item in self.config:
            if self.config[item]:
                if self.config[item].endswith("="):
                    self.config[item] = self.b64custom(self.config[item]).decode("utf-8")
        self.get_config_key()
        for item in self.config:
            if self.config[item]:
                if self.config[item].endswith(" "):
                    self.decrypt_config_value(item)
        return self.config
