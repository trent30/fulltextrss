#!/usr/bin/env python
# -*- coding: utf-8 -*-

import BaseHTTPServer
from Browser import Browser
from xml.dom.minidom import parseString
import threading
import Queue
from time import sleep
import urllib
from dtc import dtc

class ParseFlux():
	
	browser = Browser()
	q = Queue.Queue(0)
	cache_db = {}
	
	def delete_script(self, texte):
		new_texte = ''
		m1 = "<script"
		m2 = "</script>"
		if texte.find(m1) == -1:
			return texte
		while texte.find(m1) != -1:
			p1 = texte.find(m1)
			p2 = texte.find(m2) + len(m2)
			new_texte = texte[ : p1 ]
			new_texte += texte[ p2 :]
			texte = new_texte
		return new_texte
	
	def update(self, page, link, new_data, start, end):
		# remplace la "Description" correspondant au "link" par new_data
		if start != '':
			if new_data.find(start) == -1:
				print 'Avertissement : Le début "' + start + '" n''a pas été trouvé dans ' + link 
			else : 
				new_data = new_data[ new_data.find(start) + len(start) : ]
		if end != '':
			if new_data.find(end) == -1:
				print 'Avertissement : La fin "' + end + '" n''a pas été trouvé dans ' + link  
			else:
				new_data = new_data[ : new_data.find(end) ]
		new_data = new_data.replace(']]>', '').decode('utf8')
		try:
			dom = parseString(page)
		except:
			return page
		
		for node in dom.getElementsByTagName('item'):
			if node.getElementsByTagName('link')[0].childNodes[0].data == link:
				node.getElementsByTagName('description')[0].childNodes[0].data = new_data
		return dom.toxml('utf-8')
	
	def parse_flux(self, url):
		page = self.browser.get(url)
		page = page.replace('<description></description>','<description> </description>')
		links = []
		try:
			dom = parseString(page)
		except:
			return page, links
		for node in dom.getElementsByTagName('item'):
			links.append( node.getElementsByTagName("link")[0].childNodes[0].data)
		return page, links
	
	def dl_page(self, url):
		self.q.put( (url, self.browser.get(url)) )
		
	def main(self, url, start, end):
		page, links = self.parse_flux(url)
		for i in links :
			if i not in self.cache_db:
				th=threading.Thread(target = self.dl_page, args=(i,))
				th.setDaemon(True)
				th.start()
		while threading.activeCount() != 1:
			sleep(0.05)
		while self.q.empty() == False:
			n = self.q.get()
			self.cache_db[n[0]] = n[1]
		for i in links :
			if self.cache_db.get(i) != None:
				page = self.update(page, i, self.cache_db[i], start, end)
		return	page
	
class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def do_GET(s):
		p = ParseFlux()
		start = ''
		end = ''
		m = "?url="
		url = s.path[ s.path.find(m) + len(m) : ]
		m = "&start=" 
		m2 = "&end="
		if m in url:
			url = url[ : url.find(m) ]
			start = s.path[ s.path.find(m) + len(m) : ]
			if m2 in start:
				start = start[ : start.find(m2) ]
		if m2 in s.path:
			end = s.path[ s.path.find(m2) + len(m2) : ]
		if m2 in url:
			url = url[ : url.find(m2) ]
		start = urllib.unquote(start)
		end = urllib.unquote(end)
		#hook
		if url == "http://danstonchat.com/rss.xml":
			d = dtc()
			data = d.run(url)
		else:
			data = p.main(url, start, end)
		s.send_response(200)
		s.send_header("Content-type", "text/html")                                   
		s.end_headers()
		s.wfile.write(data)

class MyHTTPServer():
	
	def run(self, server_class, handler_class):
		server_address = ('', 8001)
		httpd = server_class(server_address, handler_class)
		httpd.timeout = 300
		httpd.serve_forever()

if __name__ == "__main__":
	httpd = MyHTTPServer()
	httpd.run(BaseHTTPServer.HTTPServer, MyHandler)
