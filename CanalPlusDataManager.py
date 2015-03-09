# Great thanks to all contributors of :
# https://github.com/pelrol/xbmc-my-canal

import scraper
import pprint

import urllib2
import json

class CanalPlusDataManager(object):
	
	def __init__(self, nav):
		self.nav = nav

	def list_programs(self):
		emission_types = scraper.Emission.get_emission_types()
		print ':: %d programs available :' % len(emission_types)
		for emission_type in emission_types:
			emissions = scraper.Emission.get_emissions_from_index(emission_type['index'])
			print '.... %s : %d emissions' % (emission_type['name'], len(emissions))
			for emission in emissions:
				videos = scraper.Video.from_url(emission['url'])
				print ':::::: %s : %d streams' % (emission['name'], len(videos))

	def retrieve_streams(self, program, search=None):
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
						if search.lower() in video['name'].lower() or search == '':
							streams.append({'title':video['name'], 'desc':'', 'date':'', 'time':'', 'duration':'', 'www-url':emission['url'], 'url':video['url']})
				
		self.nav.results.append(streams)
			
		return streams

	def get_stream_uri(self, video):
		'''Return stream URI for selected stream (index) in Navigator results list'''
		media = scraper.Media.from_url(video['url'])
		return media['url']



