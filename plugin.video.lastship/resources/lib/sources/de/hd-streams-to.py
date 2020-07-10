# -*- coding: utf-8 -*-

"""
    Infinity Add-on (C) 2019
    Credits to Exodus and Covenant; our thanks go to their creators

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

# Addon Name: Infinity
# Addon id: plugin.video.infinity
# Addon Provider: Infinity

import urlparse
import re
import cfscrape
import urlresolver
import xbmc

try:
    from providerModules.LastShip import cache
    from providerModules.LastShip import cleantitle
    from providerModules.LastShip import dom_parser
    from providerModules.LastShip import source_utils
    from resources.lib.modules.handler.requestHandler import cRequestHandler
    from resources.lib.parser import cParser
except:
    from resources.lib.modules import cache
    from resources.lib.modules import cleantitle
    from resources.lib.modules import dom_parser
    from resources.lib.modules import source_utils
    from resources.lib.modules.handler.requestHandler import cRequestHandler
    from resources.lib.parser import cParser

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['hd-streams.to']
        self.base_link = 'https://hd-streams.to/de/'
        self.search_link = self.base_link + "?s=%s"
        self.get_hoster = self.base_link + 'wp-admin/admin-ajax.php'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):

        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases), year)
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases), year)
        if not url and localtvshowtitle != tvshowtitle: url = self.__search([tvshowtitle] + source_utils.aliases_to_array(aliases), year)
        return url

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        url = urlparse.urljoin(self.base_link, url)

        content = cache.get(self.scraper.get, 8, url).content
        links = dom_parser.parse_dom(content, 'div', attrs={'id': 'seasons'})
        links = dom_parser.parse_dom(links, 'div', attrs={'class': 'se-c'})
        links = [i for i in links if dom_parser.parse_dom(i, 'span', attrs={'class': 'se-t'})[0].content == season]
        links = dom_parser.parse_dom(links, 'li')
        links = [dom_parser.parse_dom(i, 'a')[0].attrs['href'] for i in links if dom_parser.parse_dom(i, 'div', attrs={'class': 'numerando'})[0].content == season + ' - ' + episode]

        return source_utils.strip_domain(links[0])

    def sources(self, url, hostDict, hostprDict):
        xbmc.log("logge: sources aufgerufen", xbmc.LOGNOTICE)
        data = urlparse.parse_qs(url)
        data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
        sUrl = urlparse.urljoin(self.base_link, data.get('url', ''))
        xbmc.log("logge: sources URL: %s" % sUrl, xbmc.LOGNOTICE)
        sUrl = urlparse.urljoin(self.base_link, url)
        xbmc.log('logge: Now searching with url %s' % sUrl, xbmc.LOGNOTICE)

        hosters = []
        xbmc.log("logge: hosters", xbmc.LOGNOTICE)
        sHtmlContent = cRequestHandler(sUrl).request()
        xbmc.log("logge: request handler", xbmc.LOGNOTICE)
        pattern = "</span><a data-id='([\d]+)' "
        xbmc.log("logge: pattern", xbmc.LOGNOTICE)
        isMatch, aResult = cParser().parse(sHtmlContent, pattern)
        xbmc.log("logge: cparser", xbmc.LOGNOTICE)

        if isMatch:
            xbmc.log("logge: ismatching", xbmc.LOGNOTICE)
            for post in aResult:
                xbmc.log("logge: vor filecrypt", xbmc.LOGNOTICE)
                oRequest = cRequestHandler(self.base_link + 'wp-admin/admin-ajax.php')
                oRequest.addParameters('action', 'doo_player_ajax')
                oRequest.addParameters('post', post)
                oRequest.addParameters('nume', '1')
                if 'tvshows' in sUrl:
                    oRequest.addParameters('type', 'tv')
                else:
                    oRequest.addParameters('type', 'movie')
                oRequest.setRequestType(1)
                sHtmlContent = oRequest.request()
                isMatch, aResult = cParser().parse(sHtmlContent, "src=[^>]([^']+)")
                xbmc.log("logge: kommst du bis hier?", xbmc.LOGNOTICE)
                for sUrl in aResult:
                    valid, host = source_utils.is_host_valid(sUrl, hostDict)
                    source = {'source': '', 'quality': '720p', 'language': 'de', 'url': sUrl, 'direct': False,
                    'debridonly': False, 'checkquality': False}
                    xbmc.log("logge: source gefunden: %s" % source, xbmc.LOGNOTICE)
                    hosters.append(source)
        # Ab hier auskommentiert wie du sagtest!
        # if hosters:
        #     hosters.append('getHosterUrl')
        return hosters

        # sources = []

        # try:
        #     if not url:
        #         return sources

        #     url = urlparse.urljoin(self.base_link, url)

        #     content = cache.get(self.scraper.get, 48, url).content
        #     links = dom_parser.parse_dom(content, 'div', attrs={'class': 'options'})
        #     links = re.findall('data-post="(.*?)" data-nume="(.*?)"(.*?)class="server">(.*?)<',links[0].content)

        #     for post, nume, usless, hoster in links:
        #         if not 'trailer' in nume:
        #             link = self.__resolve(post, nume)
        #             valid, hoster = source_utils.is_host_valid(link, hostDict)
        #             if not valid: continue

        #             sources.append({'source': hoster, 'quality': '720p' if 'openload' in hoster else 'SD', 'language': 'de', 'url': link, 'direct': False, 'debridonly': False, 'checkquality': False})

        #     if len(sources) == 0:
        #         raise Exception()
        #     return sources
        # except:

        #     return sources

    def __resolve(self, post, nume):

        url = urlparse.urljoin(self.base_link, self.get_hoster)

        params ={
            'action': 'doo_player_ajax',
            'post': post,
            'nume': nume,
            'type': 'movie'
        }

        result = self.scraper.post(url, data=params).content

        link = dom_parser.parse_dom(result, 'iframe')[0].attrs['src']

        if 'streamit' in link:
            content = self.scraper.get(link, verify=False).content
            link = dom_parser.parse_dom(content, 'meta', attrs={'name': 'og:url'})[0].attrs['content']

        link = self.scraper.get(link).content
        link = re.findall('name="og:url" content="(.*?)"', link)[0]
        return link
        
    def resolve(self, url):
        return url

    def __search(self, titles, year):
        try:
            t = [cleantitle.get(i) for i in set(titles) if i]
    
            for title in titles:
                url = self.search_link % cleantitle.getsearch(title)
                r = cache.get(self.scraper.get, 8, self.search_link % cleantitle.getsearch(title)).content                
                link = dom_parser.parse_dom(r, 'div', attrs={'class': 'result-item'})
                link = [(dom_parser.parse_dom(l, 'div', attrs={'class': 'title'}), dom_parser.parse_dom(l, 'span', attrs={'class': 'year'})[0].content) for l in link]
                link = [(dom_parser.parse_dom(i[0], 'a')[0], i[1]) for i in link]
                link = [(i[0].attrs['href'], i[0].content, i[1]) for i in link]
                link = [i[0] for i in link if cleantitle.get(i[1]) in t and abs(int(i[2]) - int(year)) < 2]

                if len(link) > 0:
                    return source_utils.strip_domain(link[0])
            return
        except:
            return
