#!/usr/bin/env python
# -*- coding: utf-8 -*- #

AUTHOR = u'Marconi Moreto'
SITENAME = u'marconijr'
SITEURL = 'http://marconijr.com'
TAGLINE = 'A grunt, member of a herd and I work for pie.'
TIMEZONE = 'Asia/Hong_Kong'

DEFAULT_LANG = u'en'

FEED_DOMAIN = SITEURL
FEED_ATOM = 'feeds/all.atom.xml'

# Blogroll
LINKS = (('@marconimjr', 'https://twitter.com/marconimjr'),
         ('Github', 'http://github.com/marconi'),
         ('Email', 'mailto:caketoad@gmail.com'))

DEFAULT_PAGINATION = False
THEME = 'themes/pelican-svbtle'
MARKUP = ('md',)
MD_EXTENSIONS = ['codehilite', 'extra']
