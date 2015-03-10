# JSON ressources found thanks to ArteFetcher software sources
# http://sourceforge.net/projects/artefetcher/
V_ALL="http://www.arte.tv/guide/%s/plus7.json"
V_SELECTION="http://www.arte.tv/guide/%s/plus7/selection.json"
V_MOSTRECENT="http://www.arte.tv/guide/%s/plus7/plus_recentes.json"
V_MOSTSEEN="http://www.arte.tv/guide/%s/plus7/plus_vues.json"
V_LASTCHANCE="http://www.arte.tv/guide/%s/plus7/derniere_chance.json"

V_JSONLANG = {'fr': 'F', 'de':'D', 'en': 'E'}
V_DOMAIN="http://www.arte.tv"

DL_PRIORITY = ( 
				'LD - 220p * 384x216 * RMP4 * VOF', 
				'LD - 220p * 384x216 * RMP4 * VF', 
				'LD - 220p * 384x216 * RMP4 * VOA-STF', 
				'LD - 220p * 384x216 * RMP4 * VOF-STF', 
				'LD - 220p * 384x216 * RMP4 * VA-STF', 
				'LD - 220p * 384x216 * RMP4 * VF-STF', 
				'MD - 400p * 640x360 * M3U8 * VOF', 
				'MD - 400p * 640x360 * M3U8 * VF', 
				'MD - 400p * 640x360 * M3U8 * VOA-STF', 
				'MD - 400p * 640x360 * M3U8 * VOF-STF', 
				'MD - 400p * 640x360 * M3U8 * VA-STF', 
				'MD - 400p * 640x360 * M3U8 * VF-STF', 
				'SD - 400p * 720x406 * HBBTV * VOF', 
				'SD - 400p * 720x406 * HBBTV * VF', 
				'SD - 400p * 720x406 * HBBTV * VOA-STF', 
				'SD - 400p * 720x406 * HBBTV * VOF-STF', 
				'SD - 400p * 720x406 * HBBTV * VA-STF', 
				'SD - 400p * 720x406 * HBBTV * VF-STF', 
				'HD - 720p * 1280x720 * HBBTV * VOF', 
				'HD - 720p * 1280x720 * HBBTV * VF',
				'HD - 720p * 1280x720 * HBBTV * VOA-STF', 
				'HD - 720p * 1280x720 * HBBTV * VOF-STF',
				'HD - 720p * 1280x720 * HBBTV * VA-STF',
				'HD - 720p * 1280x720 * HBBTV * VF-STF'
				)

import urllib2
import json

class ArteDataManager(object):
	
	def __init__(self, nav):
		self.nav = nav

	def list_programs(self):
		programs = ['plus7', 'selection', 'mostseen', 'lastchance']
		print ':: %d programs available :' % len(programs)
		for program in programs:
			print '.... %s' % program

	def __extract_streams__(self, lis, lang):
		'''Extract list of videos title, url, and teaser from JSON ressource'''
		streams = []
		for l in lis:
			vjson_url = "http://org-www.arte.tv/papi/tvguide/videos/stream/player/"+lang+"/"+l["em"]+"_PLUS7-"+lang+"/ALL/ALL.json"
			try:
				streams.append({'title':l["title"], 'desc':l["desc"], 'date':l['airdate_long'], 'time':'', 'duration':str(l['duration']), 'www-url':V_DOMAIN+l["url"], 'url':vjson_url})
			except IndexError:
				# empty title ??
				streams.append({'title':'== NO TITLE ==', 'desc':l["desc"], 'date':l['airdate_long'], 'time':'', 'duration':str(l['duration']), 'www-url':V_DOMAIN+l["url"], 'url':vjson_url})
		
		return streams
	
	def retrieve_streams(self, program):
		'''Get requested program streams index'''
		
		# Select JSON uri
		# Default = "plus7" catalog (all videos)
		json_uri = V_ALL
		if program == "selection":
			json_uri = V_SELECTION
		elif program == "recent":
			json_uri = V_MOSTRECENT
		elif program == "mostseen":
			json_uri = V_MOSTSEEN
		elif program == "lastchance":
			json_uri = V_LASTCHANCE

		# Retrieve JSON data
		try:
			print ':: Retrieving <' + program + '> list <'+self.nav.options.lang+'>'
			url = json_uri % (self.nav.options.lang)
			obj = json.load(urllib2.urlopen(url))
			lis = obj["videos"]
			streams = self.__extract_streams__(lis, V_JSONLANG[self.nav.options.lang])
			return streams
		except urllib2.URLError:
			die("Can't get the arte+7 Master JSON resource")
			
		return None

	def get_stream_uri(self, video):
		'''Return stream URI for selected stream (index) in Navigator results list'''
		
		stream_url = []
		stream_format = []

		try:
			# THIS SHOULD BE MADE BY A SPECIFIC OBJECT FOR EACH CHANNEL (ARTE / PLUZZ)
			# WE SHOULD ONLY WORK HERE ON A STANDARD VIDEO INTERFACE > title, desc, (url, format)
			# get the channels
			print ':: Select video format for : '+video["title"]
			obj = json.load(urllib2.urlopen(video["url"]))			
			lis = obj["videoJsonPlayer"]["VSR"]
			for (key, details) in lis.items():
				stream_url.append(details['url'])
				stream_format.append(details['quality']+' * '+str(details['width'])+'x'+str(details['height'])+' * '+details['videoFormat']+' * '+details['versionCode']);
		except urllib2.URLError:
			die("Can't get resource : "+video["url"])
		
		# Try to find requested video format by priority
		k = 0
		vurl = ""
		vfmt = ""
		for i in DL_PRIORITY:
			for j in stream_format:
				if i == j:
					vurl = stream_url[k]
					vfmt = j
				k = k + 1
			k = 0
		
		if vurl == "":
			print ":: Available string formats :"
			for j in stream_format:
				print ":: > " + j
			print ":: Selected formats :"
			for j in DL_PRIORITY:
				print ":: > " + j
			print >> sys.stderr, "Stream search : not match found... "
			return False
			
		print ":: Stream format matched : " + vfmt
		
		return vurl
		
