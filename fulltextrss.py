#!/usr/bin/env python
# -*- coding: utf-8 -*-

import BaseHTTPServer
from Browser import Browser
from xml.dom.minidom import parseString
import threading
import Queue

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
	
	def update(self, page, link, new_data):
		# remplace la "Description" correspondant au "link" par new_data
		new_page = page[ : page.find(link) + len(link)]
		page = page[ page.find(link) + len(link) : ]
		m = "<description>"
		new_page += page[ : page.find(m) + len(m)]
		new_page += "<![CDATA["
		new_data = new_data[ new_data.find('<body') : ]
		new_data = new_data[ : new_data.find('</body>') ]
		new_page += self.delete_script(new_data).replace("]]>", "")
		new_page += "]]>"
		page = page[ page.find(m) + len(m) : ]
		m = "</description>"
		new_page += page[ page.find(m) :]
		return new_page
	
	def parse_flux(self, url):
		page = self.browser.get(url)
		links = []
		dom = parseString(page)
		for node in dom.getElementsByTagName('item'):
			links.append( node.getElementsByTagName("link")[0].toxml().encode('utf8').replace("<link>", "").replace("</link>", "") )
		return page, links
	
	def dl_page(self, url):
		self.q.put( (url, self.browser.get(url)) )
		
	def main(self, url):
		page, links = self.parse_flux(url)
		for i in links :
			if i not in self.cache_db:
				self.dl_page(i)
		while threading.activeCount() != 1:
			sleep(0.05)
		while self.q.empty() == False:
			n = self.q.get()
			self.cache_db[n[0]] = n[1]
		for i in links :
			page = self.update(page, i, self.cache_db[i])
		return	page
	
class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def do_GET(s):
		p = ParseFlux()
		m = "?url="
		url = s.path[ s.path.find(m) + len(m) : ]
		data = p.main(url)
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
