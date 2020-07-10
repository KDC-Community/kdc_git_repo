# -*- coding: utf-8 -*-
import re
try:
    from urlparse import urlparse
    from urllib import quote, unquote, quote_plus, unquote_plus
except ImportError:
    from urllib.parse import quote, unquote, quote_plus, unquote_plus, urlparse

class cParser:
    @staticmethod
    def parseSingleResult(sHtmlContent, pattern):
        aMatches = re.compile(pattern).findall(sHtmlContent)
        if len(aMatches) == 1:
            aMatches[0] = cParser.__replaceSpecialCharacters(aMatches[0])
            return (True, aMatches[0])
        return (False, aMatches)

    @staticmethod
    def __replaceSpecialCharacters(s):
        s = s.replace('\\/', '/').replace('&amp;', '&').replace('\\u00c4', 'Ä').replace('\\u00e4', 'ä')
        s = s.replace('\\u00d6', 'Ö').replace('\\u00f6', 'ö').replace('\\u00dc', 'Ü').replace('\\u00fc', 'ü')
        s = s.replace('\\u00df', 'ß').replace('\\u2013', '-').replace('\\u00b2', '²').replace('\\u00b3', '³')
        s = s.replace('\\u00e9', 'é').replace('\\u2018', '‘').replace('\\u201e', '„').replace('\\u201c', '“')
        s = s.replace('\\u00c9', 'É').replace('\\u2026', '...').replace('\\u202fh', 'h').replace('\\u2019', '’')
        s = s.replace('\\u0308', '̈').replace('\\u00e8', 'è').replace('#038;', '').replace('\\u00f8', 'ø')
        s = s.replace('／', '/')
        return s

    @staticmethod
    def parse(sHtmlContent, pattern, iMinFoundValue=1, ignoreCase=False):
        sHtmlContent = cParser.__replaceSpecialCharacters(sHtmlContent)
        if ignoreCase:
            aMatches = re.compile(pattern, re.DOTALL | re.I).findall(sHtmlContent)
        else:
            aMatches = re.compile(pattern, re.DOTALL).findall(sHtmlContent)
        if len(aMatches) >= iMinFoundValue:
            return (True, aMatches)
        return (False, aMatches)

    @staticmethod
    def replace(pattern, sReplaceString, sValue):
        return re.sub(pattern, sReplaceString, sValue)

    @staticmethod
    def search(sSearch, sValue):
        return re.search(sSearch, sValue, re.IGNORECASE)

    @staticmethod
    def escape(sValue):
        return re.escape(sValue)

    @staticmethod
    def getNumberFromString(sValue):
        pattern = '\d+'
        aMatches = re.findall(pattern, sValue)
        if len(aMatches) > 0:
            return int(aMatches[0])
        return 0

    @staticmethod
    def urlparse(sUrl):
        return urlparse(sUrl).netloc.title()

    @staticmethod
    def urlDecode(sUrl):
        return unquote(sUrl)

    @staticmethod
    def urlEncode(sUrl, safe=''):
        return quote(sUrl, safe)

    @staticmethod
    def unquotePlus(sUrl):
        return unquote_plus(sUrl)

    @staticmethod
    def quotePlus(sUrl):
        return quote_plus(sUrl)
