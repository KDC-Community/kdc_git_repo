# -*- coding: UTF-8 -*-

"""
    Lastship Add-on (C) 2019
    Credits to Lastship, Placenta and Covenant; our thanks go to their creators

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

# Addon Name: Lastship
# Addon id: plugin.video.lastship
# Addon Provider: Lastship

import urllib
import urlparse
import re
import urlresolver
import xbmc
from resources.lib.modules import dom_parser
from resources.lib.modules import source_utils
from resources.lib.modules import cleantitle
from resources.lib.modules import source_faultlog
from resources.lib.modules.handler.requestHandler import cRequestHandler
from resources.lib.parser import cParser

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['kinoger.to']
        self.base_link = 'http://kinoger.to/'
        self.search = self.base_link + 'index.php?do=search&subaction=search&search_start=1&full_search=0&result_from=1&titleonly=3&story=%s'
        #http://kinoger.to/index.php?do=search&subaction=search&search_start=1&full_search=0&result_from=1&titleonly=3&story=Captain%20Marvel

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search(False, [localtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and title != localtitle:
                url = self.__search(False, [title] + source_utils.aliases_to_array(aliases), year)
            return urllib.urlencode({'url': url, 'imdb': re.sub('[^0-9]', '', imdb)}) if url else None
            
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search(True, [localtvshowtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and tvshowtitle != localtvshowtitle:
                url = self.__search(True, [tvshowtitle] + source_utils.aliases_to_array(aliases), year)
            return urllib.urlencode({'url': url, 'imdb': re.sub('[^0-9]', '', imdb)}) if url else None
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            if not data["url"]:
                return
            data.update({'season': season, 'episode': episode})
            return urllib.urlencode(data)
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        data = urlparse.parse_qs(url)
        data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
        url = urlparse.urljoin(self.base_link, data.get('url', ''))
        xbmc.log('Now searching with url %s' % url, xbmc.LOGDEBUG)
        hosters = []
        sHtmlContent = cRequestHandler(url).request()
        pattern = "show[^>]\d,[^>][^>]'([^']+)"
        isMatch, aResult = cParser().parse(sHtmlContent, pattern)
        if isMatch:
            for sUrl in aResult:
                xbmc.log('Found match %s' % sUrl, xbmc.LOGDEBUG)
                if 'sst' in sUrl:
                    xbmc.log('Now checking: %s' % sUrl, xbmc.LOGDEBUG)
                    oRequest = cRequestHandler(sUrl)
                    oRequest.addHeaderEntry('Referer', sUrl)
                    sHtmlContent = oRequest.request()
                    pattern = 'file:"(.*?)"'
                    isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
                    pattern = '(http[^",]+)'
                    isMatch, aResult = cParser().parse(sContainer[0], pattern)
                    for sUrl in aResult:
                        xbmc.log('Found URL: %s' % sUrl, xbmc.LOGDEBUG)
                        valid, host = source_utils.is_host_valid(sUrl, hostDict)
                        xbmc.log('Valid host', xbmc.LOGDEBUG)
                        qualy = re.search('360p|480p|720p', sUrl)
                        if qualy is None:
                            sQualy = '1080p'
                        else:
                            sQualy = qualy.group(0)
                        xbmc.log('Regex match done: %s' % sQualy, xbmc.LOGDEBUG)
                        source = {'source': host, 'quality': sQualy, 'language': 'de', 'url': sUrl, 'direct': False,
                                  'debridonly': False, 'checkstreams': True}
                        xbmc.log('Appending match: %s' % source, xbmc.LOGDEBUG)
                        hosters.append(source)
                if 'kinoger.re' in sUrl:
                    xbmc.log('Now checking: %s' % sUrl, xbmc.LOGDEBUG)
                    oRequest = cRequestHandler(sUrl.replace('/v/', '/api/source/'))
                    oRequest.addHeaderEntry('Referer', sUrl)
                    oRequest.addParameters('r', 'https://kinoger.com/')
                    oRequest.addParameters('d', 'kinoger.re')
                    sHtmlContent = oRequest.request()
                    pattern = 'file":"([^"]+)","label":"([^"]+)'
                    isMatch, aResult = cParser.parse(sHtmlContent, pattern)
                    for sUrl, sQualy in aResult:
                        valid, host = source_utils.is_host_valid(sUrl, hostDict)
                        source = {'source': host, 'quality': sQualy, 'language': 'de', 'url': sUrl, 'direct': False,
                                  'debridonly': False, 'checkstreams': True}
                        xbmc.log('Appending match: %s' % source, xbmc.LOGDEBUG)
                        hosters.append(source)
                if 'cloudvideo.tv' in sUrl:
                    xbmc.log('Now checking: %s' % sUrl, xbmc.LOGDEBUG)
                    oRequest = cRequestHandler(sUrl.replace('emb.html?','embed-') + '.html')
                    oRequest.addHeaderEntry('Referer', sUrl)
                    sHtmlContent = oRequest.request()
                    pattern = 'source src="([^"]+)'
                    isMatch, aResult = cParser.parseSingleResult(sHtmlContent, pattern)
                    oRequest = cRequestHandler(aResult)
                    oRequest.addHeaderEntry('Referer', sUrl)
                    sHtmlContent = oRequest.request()

                    pattern = 'RESOLUTION=\d+x([\d]+).*?CODECS=".*?(http[^#]+)'
                    isMatch, aResult = cParser().parse(sHtmlContent, pattern)
                    for sQualy, sUrl in aResult:
                        if not 'iframe' in sUrl:
                            valid, host = source_utils.is_host_valid(sUrl, hostDict)
                            qualy = re.search('360p|480p|720p', sUrl)
                            if qualy is None:
                                sQualy = '1080p'
                            else:
                                sQualy = qualy.group(0)
                            source = {'source': host, 'quality': sQualy, 'language': 'de', 'url': sUrl, 'direct': False,
                                      'debridonly': False, 'checkstreams': True}
                            xbmc.log('Appending match: %s' % source, xbmc.LOGDEBUG)
                            hosters.append(source)
        elif 'hdgo' in sUrl or 'sst' in sUrl:
            xbmc.log('Now checking: %s' % sUrl, xbmc.LOGDEBUG)
            oRequest = cRequestHandler(sUrl)
            oRequest.addHeaderEntry('Referer', sUrl)
            sHtmlContent = oRequest.request()
            pattern = 'file:"(.*?)"'
            isMatch, sContainer = cParser.parseSingleResult(sHtmlContent, pattern)
            pattern = '(http[^",]+)'
            isMatch, aResult = cParser().parse(sContainer[0], pattern)
            for sUrl in aResult:
                valid, host = source_utils.is_host_valid(sUrl, hostDict)
                qualy = re.search('360p|480p|720p', sUrl)
                if qualy is None:
                    sQualy = '1080p'
                else:
                    sQualy = qualy.group(0)
                source = {'source': host, 'quality': sQualy, 'language': 'de', 'url': sUrl, 'direct': False,
                          'debridonly': False, 'checkstreams': True}
                xbmc.log('Appending match: %s' % source, xbmc.LOGDEBUG)
                hosters.append(source)

        xbmc.log('Found hosters: %s' % hosters, xbmc.LOGDEBUG)
        return hosters


    def resolve(self, url):
        try:
            if 'kinoger' in url:
                oRequest = cRequestHandler(url)
                oRequest.removeBreakLines(False)
                oRequest.removeNewLines(False)
                request = oRequest.request()
                pattern = 'src:  "(.*?)"'
                request = re.compile(pattern, re.DOTALL).findall(request)
                return request[0] + '|Referer=' + url
            return url
        except:
            source_faultlog.logFault(__name__, source_faultlog.tagResolve)
            return url

    def __search(self, isSerieSearch, titles, year):
        try:
            t = [cleantitle.get(i) for i in set(titles) if i]
            url = self.search % titles[0]
            oRequest = cRequestHandler(url)
            oRequest.removeBreakLines(False)
            oRequest.removeNewLines(False)
            sHtmlContent = oRequest.request()
            search_results = dom_parser.parse_dom(sHtmlContent, 'div', attrs={'class': 'title'})
            search_results = dom_parser.parse_dom(search_results, 'a')
            search_results = [(i.attrs['href'], i.content) for i in search_results]
            search_results = [(i[0], re.findall('(.*?)\((\d+)', i[1])[0]) for i in search_results]
            
            if isSerieSearch == True:
                for x in range(0, len(search_results)):
                    title = cleantitle.get(search_results[x][1][0])
                    if 'staffel' in title and any(k in title for k in t):
                        return source_utils.strip_domain(search_results[x][0])
            else:
                for x in range(0, len(search_results)):
                    title = cleantitle.get(search_results[x][1][0])
                    if any(k in title for k in t) and year == search_results[x][1][1]:
                        return source_utils.strip_domain(search_results[x][0])

            return
        except:
            try:
                source_faultlog.logFault(__name__, source_faultlog.tagSearch, titles[0])
            except:
                return
            return
