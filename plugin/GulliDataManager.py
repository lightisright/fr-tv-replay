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

# ======================================================================
# Credits
# ======================================================================
# Thanks to XBMC Gulli Replay plugin staff
# http://kodi-passion.fr/addons/?Page=View&ID=plugin.video.GulliReplay
# ======================================================================

import urllib2, sys
import parsedom
import re

common = parsedom

class GulliDataManager(object):
	
	def __init__(self, nav):
		self.nav = nav
		self.DL_METHOD = 'FFMPEG'
		self.debug_mode = False

	def list_programs(self):
		programs = [{'id':'AaZ', 'desc':'De A a Z'}, {'id':'nouveautes', 'desc':'Nouveautes'}]
		return programs
	
	# ==============================================================
	# XBMC Gulli Replay plugin code copy
	# @see http://kodi-passion.fr/addons/?Page=View&ID=plugin.video.GulliReplay
	# ==============================================================
	def get_soup(self,url):
		req  = urllib2.Request(url)
		req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 5.1; rv:15.0) Gecko/20100101 Firefox/15.0.1')           
		soup = urllib2.urlopen(req).read()
		if (self.debug_mode):
			print str(soup)
		return soup 

	def get_embed_url(self,url):
		soup  = self.get_soup(url)
		html  = soup.decode("utf-8")
		src   = re.findall("""jQuery\(\'.flashcontent\'\)\.html\(\'<iframe src=\"(.+?)\"""",html)
		if src :
			return src[0]
		else :
			return False

	def get_video_url(self,url):
		soup           = self.get_soup(url)
		html           = soup.decode("utf-8")
		file_url = re.findall("""file: '(.+?)',""", html)
		if file_url :
			return file_url[0]
		else :
			return False
	# ==============================================================
	# END XBMC Gulli Replay plugin code copy
	# ==============================================================

	def retrieve_streams(self, program):
		'''Get requested program streams index'''
		
		if program == '':
			program = "AaZ"
			
		url = "http://replay.gulli.fr/"+program
		streams = []

		try:
			# ==============================================================
			# XBMC Gulli Replay plugin code copy
			# @see http://kodi-passion.fr/addons/?Page=View&ID=plugin.video.GulliReplay
			# ==============================================================
			soup						= self.get_soup(url)
			html                        = soup.decode("utf-8")
			wrapper_pattern             = common.parseDOM(html,"div",attrs={"id":u"wrapper"}) [0]
			ul_liste_resultats_pattern  = common.parseDOM(wrapper_pattern,"ul",attrs={"class":"liste_resultats"})
			for ul in ul_liste_resultats_pattern :
				li_pattern_list = common.parseDOM(ul,"li")
				for li_pattern in li_pattern_list :
					image_url_pattern   = common.parseDOM(li_pattern,"img",ret="src") [0]
					image_url           = image_url_pattern.encode("utf-8")
					if self.debug_mode :
						print "image_url :"+image_url
					episode_url_pattern = common.parseDOM(li_pattern,"a",ret="href") [0]
					episode_url         = episode_url_pattern.encode("utf-8")
					if self.debug_mode :
						print "episode_url : "+episode_url
					titre1_pattern      = common.parseDOM(li_pattern,"strong") [0]
					titre1              = titre1_pattern.encode("utf-8")
					if self.debug_mode :
						print "titre1 :"+titre1
					p_list_pattern      = common.parseDOM(li_pattern,"p") [0]
					titre2_pattern      = common.parseDOM(p_list_pattern,"span") [0]
					titre2_tmp          = titre2_pattern.encode("utf-8")
					titre2_tmp          = "//".join(titre2_tmp.split("""<br/>"""))
					titre2_tmp          = "".join(titre2_tmp.split("\n"))
					titre2_tmp          = "".join(titre2_tmp.split("\s"))
					titre2_tmp          = "".join(titre2_tmp.split("\t"))
					titre2_tmp          = "".join(titre2_tmp.split("\r"))
					titre2_tmp          = "".join(titre2_tmp.split("\f"))
					titre2_tmp          = "".join(titre2_tmp.split("\v"))
					titre2              = " ".join(titre2_tmp.split("&nbsp;"))
					if self.debug_mode :
						print "titre2 : "+titre2                                
					titre_episode = titre1 +" : "+ titre2
					if self.debug_mode :
						print "titre_episode :"+titre_episode
					# ==============================================================
					# END XBMC Gulli Replay plugin code copy
					# ==============================================================

					stream 				= {'channel': 'Gulli', 'program': program }
					stream['title'] 	= titre_episode
					stream['desc'] 		= ''
					stream['date'] 		= ''
					stream['time'] 		= ''
					stream['duration'] 	= ''
					stream['www-url'] 	= episode_url
					stream['url'] 		= episode_url

					streams.append(stream)
					
			return streams
					
		except urllib2.URLError:
			print >> sys.stderr, "Can't get resource : "+url
			return None

	def get_stream_uri(self, video):
		'''Return stream URI for selected stream (index) in Navigator results list'''

		embed_url  = self.get_embed_url(video['url'])
		if embed_url :
			video_url = self.get_video_url(embed_url)
		return video_url

