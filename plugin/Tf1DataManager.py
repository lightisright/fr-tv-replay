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
# Thanks to XBMC TF1 Replay plugin staff
# http://kodi-passion.fr/addons/?Page=View&ID=plugin.video.tf1replay
# ======================================================================

import urllib, urllib2, sys
#import parsedom
import re
import json
from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
import time, md5

#common = parsedom


# KODI PLUGIN SETTINGS : BEGIN

DEBUG = True
PREFERHD = True

WEBSITE = "http://videos.tf1.fr"
WATSITE = "http://www.wat.tv"

PROGRAMMES = "/liste-videos/"

#TYPES = {'categories' :{
#        "JT":"/programmes-tv-info/video-integrale/",
#        "Magazines":"/magazine/video-integrale/",
#        "Series - Fictions":"/series-tv/video-integrale/",
#        "Jeux":"/jeux-tv/video-integrale/",
#        "Jeunesse":"/programmes-tv-jeunesse/video-integrale/",
#        "Divertissement":"/emissions-tv/video-integrale/",
#        "Telefilms":"/telefilms/video-integrale/",
#        "Sports":"/sport/video-integrale/"
#        }}

TYPES = {'categories' :{
        "integralites":"/videos-en-integralite/video-integrale/",
        "series-etrangeres":"/series-etrangeres/video-integrale/",
        "Series - Fictions":"/fictions-francaises/video-integrale/",
        "telerealite":"/telerealites/video-integrale/",
        "magazine":"/magazine/video-integrale/",
        "divertissement":"/divertissement/video-integrale/",
        "telefilms":"/telefilms/video-integrale/",
        "sport":"/sport/",
        "jeux":"/jeux-tv/video-integrale/",
        "jeunesse":"/programmes-tv-jeunesse/video-integrale/",
        "info":"/programmes-tv-info/video-integrale/"
        }}

class Episode:
    imageUrl = ""
    pageUrl = ""
    prog = ""
    titre = ""

# KODI PLUGIN SETTINGS : END


class Tf1DataManager(object):
	
	def __init__(self, nav):
		self.nav = nav
		self.DL_METHOD = 'WGET'

	def list_programs(self):
		programs = []
		for (key) in TYPES['categories']:
			programs.append({'id':key, 'desc':''});
		return programs
	
	# ==============================================================
	# XBMC Tf1 Replay plugin code copy
	# @see http://kodi-passion.fr/addons/?Page=View&ID=plugin.video.tf1replay
	# ==============================================================
	def get_category_episodes(self, url):

		if DEBUG:
			print "GET URL : " + url
			
		html = urllib.urlopen(WEBSITE + url ).read()
		
		soup = BeautifulSoup(html)
		teasersli = soup.find('li',{'class': re.compile(r'\bteaser\b')})
		
		episode_list = list()
			
		if teasersli is not None:
			
			teasers = teasersli.parent.findAll('li')
			
			if len(teasers)>0:
				episodes = list()
				for teaser in teasers:
					ep = Episode()
					ep.imageUrl = teaser.find('img')['src']
					detail = teaser.find(re.compile("^h"), {'class': re.compile(r'\btitre\b') })
					ep.titre = detail.find('a').renderContents()
					ep.pageUrl = detail.find('a')['href']
					programme = teaser.find('div', {'class': re.compile(r'\bprog\b') })
					if programme:
						ep.prog = programme.strong.renderContents()
					if DEBUG:
						print "Video informations : "
						print "- Image     : " + ep.imageUrl
						print "- Programme : " + ep.prog
						print "- Titre     : " + ep.titre
						print "- Url       : " + ep.pageUrl

					episodes.append(ep)
					
				for ep in episodes:
					if ep.prog != "":
						episode_list.append({'link': WEBSITE + ep.pageUrl , 'title': BeautifulSoup(ep.prog + " - " + ep.titre, convertEntities="html",fromEncoding="utf-8").prettify() , 'image':ep.imageUrl})
					else:
						episode_list.append({'link': WEBSITE + ep.pageUrl , 'title': BeautifulSoup(ep.titre, convertEntities="html",fromEncoding="utf-8").prettify() , 'image':ep.imageUrl})
					

		match = re.search("""<li class="precedente c4 t3"><a href="([^']*)" class="c2" rel="next">""",html)
		if match:
			page_precedente = match.group(1).replace('|','/')
		else:
			page_precedente = None
		match = re.search("""<li class="suivante c4 t3"><a href="([^']*)" class="c2" rel="next">""",html)
		if match:
			page_suivante = match.group(1).replace('|','/')
		else:
			page_suivante = None

		return page_precedente, page_suivante, episode_list
		
	def get_all_episodes(self, url):
		print url
		html = urllib.urlopen(WEBSITE + url ).read()
		print WEBSITE + url, html
		liens = re.findall("""<li><a href="([^"]+)" [^>]*>([^>]+)</a></li>""",html)

		if DEBUG:
			print "liens"
			print liens

		liens_list = list()

		for lien,titre in liens:
			print "titre " + titre
			print "lien " + lien
			#Certaines emissions n'ont pas de lien vers video-integrale/'
			#liens_list.append({'link': lien + "video-integrale/" , 'title':BeautifulSoup(titre, convertEntities="html",fromEncoding="utf-8").prettify()})
			liens_list.append({'link': lien , 'title':BeautifulSoup(titre, convertEntities="html",fromEncoding="utf-8").prettify()})
			
		return liens_list

	def get_episode(self, url):
		
		try:
			hasHD = False
			
			# get video id
			req = urllib2.Request(url)
			req.add_header('User-Agent', self.nav.useragent)
			response = urllib2.urlopen(req).read()
			
			# var sitepage='TFOU/videos/catchup/mini-justiciers';
			# src = 'http://www.wat.tv/embedframe/153498nIc0K1112362243#' OU <meta name="twitter:player" value="https://www.wat.tv/embedframe/153498nIc0K1112362243">
			# Renvoie vers http://www.wat.tv/images/v70/PlayerLite.swf?videoId=7cyrn 
			# Renvoie vers http://www.wat.tv/images/v70/PlayerWat.swf?videoId=7cyrn 
			# > GOTO : src+sitepage
			# chercher l'ID de la video : 12362243
			# -> &UVID=12362243&
			# -> url : "//www.wat.tv/swf2/153498nIc0K1112362243"
			# -> iphoneId : "12362243"
			# chercher le jSON de la video
			# http://www.wat.tv/interface/contentv4/12362243
			
			idstring = re.compile('www.wat.tv/embedframe/([a-zA-Z0-9]+)"').findall(response)[0]
			video_id = idstring[-8:]
			url = WATSITE + '/interface/contentv4/' + video_id
			content = urllib2.Request(url)
			jsonVideoInfos = urllib2.urlopen(content).read()

			videoInfos = json.loads(jsonVideoInfos)

			# on suppose que si la premiere partie est en HD, les autres aussi
			if videoInfos['media']['files'][0]['hasHD'] and PREFERHD == True:
				hasHD = True
						
			# recuperation de toutes les parties
			parts = []
			for vid in videoInfos['media']['files']:
				parts.append(str(vid['id']))

			parts_url = []

			for vid in parts:
				
				if DEBUG:
					print "Get video : " + vid
					
				if hasHD:
					wat_url = "/webhd/" + vid
				else:
					wat_url = "/web/" + vid
					
				# key & algorithm found in http://www.wat.tv/images/v70/PlayerWat.swf sourcecode
				# see also https://github.com/monsieurvideo/get-flash-videos/blob/master/lib/FlashVideo/Site/Wat.pm
				key = "9b673b13fa4682ed14c3cfa5af5310274b514c4133e9b3a81e6e3aba009l2564"
				#on a besoin du timestamp en hexa sans le 0x du debut
				dthex = hex(int(time.time()))[2:]
				test = time.time()
				h = md5.new()
				h.update(key + wat_url + dthex)
				token = h.hexdigest() + "/" + dthex

				if hasHD:
					url4videoPath = WATSITE + "/get/webhd/" + vid + "?token=" + token + "&domain=videos.tf1.fr&context=swfpu&country=FR&getURL=1&version=LNX%2011,1,102,55"    
				else:
					url4videoPath = WATSITE + "/get/web/" + vid + "?token=" + token + "&domain=videos.tf1.fr&context=swfpu&country=FR&getURL=1&version=LNX%2011,1,102,55"    
					
				if DEBUG:
					print "Request URL : " + url4videoPath

				#cette url envoi comme reponse la reelle adresse de la video
				url = url4videoPath
				req = urllib2.Request(url)
				req.add_header('User-Agent', self.nav.useragent)
				#req.add_header('Referer' , referer_url)
				#req.add_header('Referer' , 'http://www.wat.tv/images/v70/PlayerLite.swf?videoId=7cpbb')
				response = urllib2.urlopen(req).read()
					
				# for http://tf1vodhdscatchup-vh.akamail.net / f4m streams, following args must be added to stream URI to avoid HTTP:403 error
				# > &start=0&hdcore=2.11.3&g=GUCTHOAMDLOW
					
			return response+"&start=0&hdcore=2.11.3&g=GUCTHOAMDLOW"
			
			
			# http://tf1vodhdscatchup-vh.akamaihd.net/z/H264-384x288/16/73/12381673.h264/manifest.f4m?hdnea=st=1432198285~exp=1432200085~acl=/*~hmac=45c49892b66c3e6e83cd665ac77624d341745e09d871c2795b3179b89abd7d34&bu=WAT&login=greys-anatomy&i=109.190.35.38&u=a5b8f60d94a6ef40e395ea2dd901e229&sum=dfa7d8dc2afe7e6c96d48effa7c9ca7c&start=0&hdcore=2.11.3&g=GUCTHOAMDLOW
			# http://tf1vodhdscatchup-vh.akamaihd.net/z/H264-384x288/16/73/12381673.h264/0_5d9b77c29e8d82be_Seg1-Frag1?pvtoken=exp%3D9999999999%7Eacl%3D%252f%252a%7Edata%3DZXhwPTE0MzIyODQ2ODV+YWNsPSUyZip+ZGF0YT1wdmMsc35obWFjPTgxMzM3NTk1ZDg1Y2U1MWY3NDk1OGI2Mzk3MDgzMzRhZWZiNzI1MWE0ZDM4ZGU4OWZjYmRhZjgwMWY5YjM0MTU%3D%21dLiI/VkZ8lgyYaau3IcgVUBFrAbEk2qmwY6+VSa5O4w%3D%7Ehmac%3D2B73FC00556049AC8BE3E824FC0BBB2E8ED98669F3919C6B45678DED3C3C9876&hdntl=exp=1432284685~acl=%2f*~data=hdntl~hmac=3a90b4b5848730669e58ceae9b02204aa9930a3e8d443b986240c2521a4783e1&bu=WAT&login=greys-anatomy&i=109.190.35.38&u=a5b8f60d94a6ef40e395ea2dd901e229&sum=dfa7d8dc2afe7e6c96d48effa7c9ca7c&start=0&als=0,2,0,0,0,NaN,0,0,0,88,f,0,2472.72,f,s,GUCTHOAMDLOW,2.11.3,88&hdcore=2.11.3
			
			# ===============
			# Exemple concret
			# ===============
			# - URL source (GreysAnatomy ep18) : 
			#   > http://tf1vodhdscatchup-vh.akamaihd.net/z/HD-1280x720/16/85/12381685.hd/manifest.f4m?hdnea=st=1432201331~exp=1432203131~acl=/*~hmac=19e7817c96b2e6faaf62f782b4e5d89fd56e8365bde9919b2bc245c3a9f0c1da&bu=&login=greys-anatomy&i=109.190.35.38&u=21f5616057db231b62dfeae8e264d2d4&sum=8adcf93f46deb56410b29a5d3f8b9c1b&start=0&hdcore=2.11.3&g=GUCTHOAMDLOW
			# - F4M renvoyé :
			#   <?xml version="1.0" encoding="UTF-8"?>
			#   <manifest xmlns="http://ns.adobe.com/f4m/1.0" xmlns:akamai="uri:akamai.com/f4m/1.0">
  			#     <akamai:version>2.0</akamai:version>
  			#     <akamai:bw>5000</akamai:bw>
  			#     <id>/HD-1280x720/16/85/12381685.hd_0</id>
			#     <streamType>recorded</streamType>
			#     <akamai:streamType>vod</akamai:streamType>
			#     <duration>2470.520</duration>
			#     <streamBaseTime>0.000</streamBaseTime>
			#     <pv-2.0>ZXhwPTE0MzIyODc3MzF+YWNsPSUyZip+ZGF0YT1wdmMsc35obWFjPWZkYmRjYjc0YmY3YWQxY2RhZDdjZWU2Mzk2NWYyYTMxZmViMWI5NTYzMjE1NzJkNTMwNGFjNWEyNjlmNWI5ZDU=;hdntl=exp=1432287731~acl=%2f*~data=hdntl~hmac=425e7d0bcf12b3283d4ed07d9befba76ab0c6d0df2b20a5d8273e98533123063</pv-2.0>
			#     <bootstrapInfo profile="named" id="bootstrap_0">AAAAi2Fic3QAAAAAAAAAAQAAAAPoAAAAAAAlsngAAAAAAAAAAAAAAAAAAQAAABlhc3J0AAAAAAAAAAABAAAAAQAAAZsBAAAARmFmcnQAAAAAAAAD6AAAAAADAAAAAQAAAAAAAAAAAAAXcAAAAZsAAAAAACWJYAAAKRgAAAAAAAAAAAAAAAAAAAAAAA==</bootstrapInfo>
			#     <media bitrate="2625" url="0_5d9b77c29e8d82be_" bootstrapInfoId="bootstrap_0">
			#       <metadata>AgAKb25NZXRhRGF0YQgAAAAMAAhkdXJhdGlvbgBAo00KPXCj1wAFd2lkdGgAQJQAAAAAAAAABmhlaWdodABAhoAAAAAAAAANdmlkZW9kYXRhcmF0ZQBAo4lyxpj8xQAJZnJhbWVyYXRlAEA5AAAAAAAAAAx2aWRlb2NvZGVjaWQAQBwAAAAAAAAADWF1ZGlvZGF0YXJhdGUAQF9qd1PihLEAD2F1ZGlvc2FtcGxlcmF0ZQBA5YiAAAAAAAAPYXVkaW9zYW1wbGVzaXplAEAwAAAAAAAAAAZzdGVyZW8BAQAMYXVkaW9jb2RlY2lkAEAkAAAAAAAAAAhmaWxlc2l6ZQBByCv1B4AAAAAACQ==</metadata>
			#     </media>
			# </manifest>
			# 
			# - URL flux :
			#   > http://tf1vodhdscatchup-vh.akamaihd.net/z/HD-1280x720/16/85/12381685.hd
			#   > + 0_5d9b77c29e8d82be_Seg1-Frag1?pvtoken= (string avant Segx à définir)
			#   > + <pv-2.O> du manifest : à partir de "exp=", chaine convertie en entités HTML (%xx)
			
			
				# 2 types de reponses possibles :
				# soit on a l'url directe : http://
				# soit on a rtmpe,rtmpte://
#				modeRtmp = 0
#				if response.find('rtmpe,')!=-1:
#					modeRtmp = 1
#					response = response[6:]
#				elif response.find('rtmp,')!=-1:
#					modeRtmp = 1
#					response = response[5:]
#
#				if modeRtmp == 1:
#					parts_url.append(response + ' swfUrl=http://www.wat.tv/images/v70/PlayerWat.swf swfVfy=true' )
#				else:
#					parts_url.append(response + '|User-Agent=' + urllib.quote(self.nav.useragent) + '&Cookie=' + urllib.quote('seen=' + vid))
#				
#			sep = " , "
#			if len(parts_url)>1:
#				video_url = "stack://" + sep.join(parts_url)
#			else:
#				video_url = parts_url[0]
#				
#			if DEBUG:
#				print "video_url: "
#				print video_url
#
#			return video_url

				
		except urllib2.URLError, e:
			 print >> sys.stderr, "Can't get the ressource : wrong URL <%s>" % url
			 print >> sys.stderr, "Detail : %s" % e
		except urllib2.HTTPError, e:
			print >> sys.stderr, "Can't get the Pluzz master ressource : HTTP error <%s>" % url
			print >> sys.stderr, "Detail : %s" % e
		
		return None

	# ==============================================================
	# END XBMC Tf1 Replay plugin code copy
	# ==============================================================

	def retrieve_streams(self, program):
		'''Get requested program streams index'''
		
		if program == '':
			program = "AaZ"
		
		url = TYPES['categories'][program]
		streams = []
		
		if DEBUG:
			print url
			print TYPES['categories']

		try:
			#tmp = self.get_all_episodes(url)
			
			page_precedente, page_suivante, episodes = self.get_category_episodes(url)
			
			for video in episodes:
				stream 				= {'channel': 'Tf1', 'program': program }
				stream['title'] 	= video['title']
				stream['desc'] 		= ''
				stream['date'] 		= ''
				stream['time'] 		= ''
				stream['duration'] 	= ''
				stream['www-url'] 	= video['link']
				stream['url'] 		= video['link']
				streams.append(stream)
				
			while ( page_suivante is not None ) :
				
				page_precedente, page_suivante, episodes = self.get_category_episodes(page_suivante)
				
				for video in episodes:
					stream 				= {'channel': 'Tf1', 'program': program }
					stream['title'] 	= video['title']
					stream['desc'] 		= ''
					stream['date'] 		= ''
					stream['time'] 		= ''
					stream['duration'] 	= ''
					stream['www-url'] 	= video['link']
					stream['url'] 		= video['link']
					streams.append(stream)
			
			return streams
					
		except urllib2.URLError:
			print >> sys.stderr, "Can't get resource : "+url
			return None

	def get_stream_uri(self, video):
		'''Return stream URI for selected stream (index) in Navigator results list'''
		video_url  = self.get_episode(video['url'])
		return video_url

