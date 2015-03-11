# PLUZZ: http://webservices.francetelevisions.fr/catchup/flux/flux_main.zip
#		 cf. https://gitorious.org/grilo/grilo-lua-sources/commit/f9f0c7d7d40561a49ba56a35c2748fd02759fd81
#		 cf. https://github.com/mikebzh44/France-TV-Pluzz-for-XBMC/blob/master/plugin.video.FranceTVPluzz/default.py

PLUZZ_RES_URL = 'http://webservices.francetelevisions.fr/catchup/flux/flux_main.zip'
PLUZZ_DOMAIN = 'http://www.pluzz.fr'

# internal configuration vars
PLUZZ_CACHE_FILE = 'cache/pluzz_flux_main.zip'
PLUZZ_CACHE_DIR = 'cache'
PLUZZ_PROGRAMS = ['france1', 'france2', 'france2', 'france3', 'france4', 'france5', 'franceo']
PLUZZ_CACHE_REFRESH_THRESHOLD = 600    # cache refresh thresold in seconds

import urllib
import json

# Zipfile package needed to extract Pluzz ressources
import zipfile
import os.path, time
import os

import datetime
from datetime import date

class PluzzDataManager(object):
	
	def __init__(self, nav):
		self.nav = nav
		self.DL_METHOD = 'FFMPEG'
		# videos base uri (loaded dynamically in message_FT.json)
		self.video_base_uri = ""

	def __dl__(self):
		'''Download replay ressources'''
		# check if ressource exists and if cache time expired
		dl = True
		if os.path.isfile(PLUZZ_CACHE_FILE) :
			#print ":: Pluzz master ressource created : %s" % time.ctime(os.path.getctime(PLUZZ_CACHE_DIR))
			#print ":: Pluzz master ressource last modification : %s" % time.ctime(os.path.getmtime(PLUZZ_CACHE_DIR))
			delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(os.path.getmtime(PLUZZ_CACHE_FILE))
			if delta.total_seconds() < PLUZZ_CACHE_REFRESH_THRESHOLD :
				print ":: Pluzz master ressource cache (%d) didn't expired thresold of %d seconds." % (delta.total_seconds(), PLUZZ_CACHE_REFRESH_THRESHOLD)
				dl = False
			else:
				print ":: Pluzz master ressource cache (%d) expired thresold of %d seconds." % (delta.total_seconds(), PLUZZ_CACHE_REFRESH_THRESHOLD)
		
		if dl == True:
			try:
				# download ressources
				print ':: Download Pluzz master ressource...'
				urllib.urlretrieve (PLUZZ_RES_URL, PLUZZ_CACHE_FILE)
				# unzip ressources
				zfile = zipfile.ZipFile(PLUZZ_CACHE_FILE)
				for name in zfile.namelist():
					(dirname, filename) = os.path.split(name)
					#print ":: Pluzz master ressource - decompressing " + filename + " on " + dirname
					if not os.path.exists(PLUZZ_CACHE_DIR+'/'+dirname):
						os.makedirs(PLUZZ_CACHE_DIR+'/'+dirname)
					zfile.extract(name, PLUZZ_CACHE_DIR+'/'+dirname)
			except OSError.URLError:
				die("Can't get the Pluzz master ressource : wrong URL")
			except OSError.HTTPError:
				die("Can't get the Pluzz master ressource : HTTP error")
				
		# Save video server URI locally
		
		json_uri = PLUZZ_CACHE_DIR+'/message_FT.json'
		try:
			print ':: Retrieving global streams informations'
			obj = json.loads(open(json_uri).read())			
			self.video_base_uri = obj["configuration"]["url_base_videos"]
		except IOError:
			print "Can't read ressource for <%s>" % program
		
	def list_programs(self):
		'''List available programs'''
		print ':: %d programs available :' % len(PLUZZ_PROGRAMS)
		self.__dl__()
		for program in PLUZZ_PROGRAMS:
			print '.... %s' % program

	def retrieve_streams(self, program):
		'''Get requested program streams index'''
		
		self.__dl__()
		
		if program not in PLUZZ_PROGRAMS:
			print "Program <%s> is not available." % program
			return None
		
		# Select JSON uri
		json_uri = PLUZZ_CACHE_DIR+'/catch_up_'+program+'.json'

		# Retrieve JSON data
		try:
			print ':: Retrieving <' + program + '> list'
			obj = json.loads(open(json_uri).read())			
			lis = obj["programmes"]
			streams = []
			for l in lis:
				title = l["genre_simplifie"]+' - '+l["titre"]
				streams.append({'title':title, 'desc':l["accroche"], 'date':l["date"], 'time':l["heure"], 'duration':l["duree"], 'www-url':PLUZZ_DOMAIN+l["OAS_sitepage"], 'url':self.video_base_uri+l["url_video"]})
			return streams
		except IOError:
			print "Can't read ressource for <%s>" % program
				
		return None

	def get_stream_uri(self, video):
		'''Return stream URI for selected stream (index) in Navigator results list'''
		return video['url']
		
