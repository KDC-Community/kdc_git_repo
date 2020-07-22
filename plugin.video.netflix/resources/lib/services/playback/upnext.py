# -*- coding: utf-8 -*-
"""
    Copyright (C) 2017 Sebastian Golasch (plugin.video.netflix)
    Copyright (C) 2018 Caphm (original implementation module)
    Relay playback info to UP NEXT add-on

    SPDX-License-Identifier: MIT
    See LICENSES/MIT.md for more information.
"""
from __future__ import absolute_import, division, unicode_literals

import resources.lib.common as common

from .action_manager import PlaybackActionManager


class UpNextNotifier(PlaybackActionManager):
    """
    Triggers the AddonSignal for Up Next addon integration.
    Needed because the signal must be sent after playback started.
    """
    def __init__(self):  # pylint: disable=super-on-old-class
        super(UpNextNotifier, self).__init__()
        self.upnext_info = None

    def __str__(self):
        return 'enabled={}'.format(self.enabled)

    def _initialize(self, data):
        self.upnext_info = data['upnext_info']
        self.enabled = bool(self.upnext_info)

    def _on_playback_started(self, player_state):
        # pylint: disable=unused-argument
        common.debug('Sending initialization signal to Up Next')
        common.send_signal(common.Signals.UPNEXT_ADDON_INIT,
                           self.upnext_info,
                           non_blocking=True)

    def _on_tick(self, player_state):
        pass
