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

# Great thanks to all contributors of :
# https://github.com/pelrol/xbmc-my-canal

import scraper
import pprint

import urllib2
import json

class CanalPlusDataManager(object):
	
	def __init__(self, nav):
		self.nav = nav
		self.DL_METHOD = 'FFMPEG'

	def list_programs(self):
		emission_types = scraper.Emission.get_emission_types()
		programs = []
		for emission_type in emission_types:
			emissions = scraper.Emission.get_emissions_from_index(emission_type['index'])
			programs.append({ 'id': emission_type['name'], 'desc': '%d emissions' % len(emissions) })
		return programs

	def retrieve_streams(self, program):
		'''Get requested program streams index'''
		
		if program == '':
			self.list_programs()
			return None
		
		streams = []
		
		emission_types = scraper.Emission.get_emission_types()
		for emission_type in emission_types:
			if program == emission_type['name']:
				emissions = scraper.Emission.get_emissions_from_index(emission_type['index'])
				print ':::: %d emissions found for : %s' % (len(emissions), emission_type['name'])
				for emission in emissions:
					videos = scraper.Video.from_url(emission['url'])
					print ':::::: %d streams found from : %s' % (len(videos), emission['name'])
					for video in videos:
						streams.append({'channel': 'CanalPlus', 'program': program, 'title':video['name'], 'desc':'', 'date':'', 'time':'', 'duration':'', 'www-url':emission['url'], 'url':video['url']})
			
		return streams

	def get_stream_uri(self, video):
		'''Return stream URI for selected stream (index) in Navigator results list'''
		media = scraper.Media.from_url(video['url'])
		return media['url']



