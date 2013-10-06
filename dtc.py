#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Browser import Browser
import re

class dtc :
	
	browser = Browser()
	
	def get_href(self, t):
		return t.split('href="')[1].split('"')[0]
		
	def get_last_number(self, l):
		for i in l:
			if "Numéro 1 du Top 50" in i:
				return l.index(i)
				
	def build_article_header(self, header, description):
		title = self.get_href(description)
		h = "<item><title>" + title + "</title>"
		h += "<link>" + title + "</link>"
		m = re.search("<pubDate>.*</pubDate>", header)
		h += m.group(0)
		h += '<guid isPermaLink="false">' + title + "</guid>"
		h += "<description>" + description + "</description></item>"
		return h
		
	def split_article(self, t):
		m = "<description>"
		header = t[ : t.find(m)]
		data = t[t.find(m) +len(m) : t.find("</description>")]
		l = data.split("Voir les commentaires")
		l = l[ : self.get_last_number(l)]
		ret = ""
		for i in l:
			ret += self.build_article_header(header, i)
		return ret
	
	def split_flux(self, page):
		if page == None or page == "":
			return None
		l = page.split('<item>')
		header = l.pop(0)
		footer = "</channel></rss>"
		ret = ""
		for i in l:
			ret += self.split_article(i)
		return header +  ret + footer
		
	def run(self, url):
		page = self.browser.get(url)
		return self.split_flux(page)
	
if __name__ == "__main__":
	d = dtc()
	print d.run(None)
