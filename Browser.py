#! /usr/bin/python
# -*- coding: utf-8 -*-

from urllib import urlopen

class Browser:

   def get(self, url):
      try:
         page = urlopen(url).read()
      except:
         print "Impossible d'ouvrir", url
         return None
      else:
         return page
