# Copyright (C) 2015  http://www.github.com/lightisright
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

DEBUG = False

import sys
import urllib2
import json

# RSS parsing tools
# python-feedparser package for Ubuntu 14.04
try:
	from feedparser import parse
except ImportError:
    print >> sys.stderr, 'Error: you need the feedparser python module'
    sys.exit(1)

try:
    from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
except ImportError:
    print >> sys.stderr, 'Error: you need the BeautifulSoup(v3) python module'
    sys.exit(1)

class FranceInterDataManager(object):
	
	def __init__(self, nav):
		self.nav = nav
		self.DL_METHOD = 'WGET'
		# local programs list
		self.programs = []

	def __dl__(self):
		'''download programs'''
		print ':: Download programs'
		url = "http://www.franceinter.fr/programmes/liste"
		soup = BeautifulSoup(urllib2.urlopen(url).read(), convertEntities=BeautifulSoup.ALL_ENTITIES)
		# get the programs
		emissions = soup.findAll('div', {'class': 'contenu'})
		del self.programs[:]
		for emission in emissions:
			try:
				program = {}
				title = emission.find('h2').find('a')
				anchor = emission.find('a', {'class': 'podrss'})
				program['title'] = title.contents[0]
				program['id'] = title['href'].split('/')[-1]
				program['url'] = anchor['href']
				#~ print ":: %s (%s)" % (title.contents[0], title['href'].split('/')[-1])
				self.programs.append(program)
			except TypeError:
				if DEBUG == True:
					print >> sys.stderr, "An error occured while parsing France Inter programs page : missing data for program"
					print emission
	
	def list_programs(self):
		'''List available programs'''
		self.__dl__()
		result = []
		for program in self.programs:
			result.append({'id':program['id'],'desc':program['title']})
		return result
		
	def retrieve_streams(self, program):
		'''Get requested program streams index'''
		
		self.__dl__()
		
		# Select RSS uri
		rss_uri = ""
		title = ''
		for k in self.programs:
			if k['id'] == program:
				rss_uri = k['url']
				title = k['title']
				break
		
		if rss_uri == '':
			print "Program <%s> is not available." % program
			print "Please use ID for program selection."
			return None
		
		# Retrieve data
		streams = []
		try:
			print ':: Retrieving <' + program + '> list'
			myfeed = parse(rss_uri)
			print myfeed['feed']['title']
			for item in myfeed['entries']:
				year, month, day, timeh, timem, times, x1, x2, x3 = item.published_parsed
				streams.append({'channel': 'FranceInter', 'program': program, 'title':title+' - '+item.title+' ('+item.category+')', 'desc':item.description, 'date':"%02d/%02d/%04d" % (day, month, year), 'time':'', 'duration':item.itunes_duration, 'www-url':item.link, 'url':item.guid})
			return streams
		except urllib2.URLError:
			print >> sys.stderr, "Can't get the arte+7 Master JSON resource"
			
		return None

	def get_stream_uri(self, video):
		'''Return stream URI for selected stream (index) in Navigator results list'''
		return video['url']
