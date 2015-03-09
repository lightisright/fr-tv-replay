#!/usr/bin/python2

########################################################################
#						   PLAYERS									#
########################################################################
# You can add your favorite player at the beginning of the PLAYERS tuple
# The command must read data from stdin
# The order is significant: the first player available is used
PLAYERS = (
		'vlc',
		'mplayer -really-quiet -',
		'xine stdin:/',
		'/usr/bin/totem --enqueue fd://0', # you could use absolute path for the command too
		)


########################################################################
# DO NOT MODIFY below this line unless you know what you are doing	 #
########################################################################

import os, sys, inspect
try:
	from BeautifulSoup import BeautifulSoup, BeautifulStoneSoup
except ImportError:
	print >> sys.stderr, 'Error: you need the BeautifulSoup(v3) python module'
	sys.exit(1)
	
# Add "./res" to include path
cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"res")))
if cmd_subfolder not in sys.path:
	sys.path.insert(0, cmd_subfolder)
	
import urllib2
from urllib import unquote
import urlparse
import json
import os
import re
import subprocess
from optparse import OptionParser
from cmd import Cmd

import tty
import termios

VERSION = '0.2'
DEFAULT_LANG = 'fr'
QUALITY = ('sd', 'hd')
DEFAULT_QUALITY = 'hd'
DEFAULT_DLDIR = os.getcwd()

VIDEO_PER_PAGE = 25

SEARCH = {'fr': 'recherche', 'de':'suche', 'en': 'search'}
LANG = SEARCH.keys()
HIST_CMD = ('channels', 'programs', 'get', 'add')

BOLD   = '[1m'
NC	 = '[0m'	# no color


# PLUZZ: http://webservices.francetelevisions.fr/catchup/flux/flux_main.zip
#		 cf. https://gitorious.org/grilo/grilo-lua-sources/commit/f9f0c7d7d40561a49ba56a35c2748fd02759fd81
#		 cf. https://github.com/mikebzh44/France-TV-Pluzz-for-XBMC/blob/master/plugin.video.FranceTVPluzz/default.py

# C+ : https://github.com/pelrol/xbmc-my-canal/blob/master/resources/lib/scraper.py
#		 cf. https://github.com/pelrol/xbmc-my-canal/blob/master/addon.py

class StdVideo(object):
	def __init__(self, title, desc, date, url, fmt):
		print "coucou"

class Navigator(object):
	def __init__(self, options):
		self.options = options
		self.more = False
		self.last_cmd = ''
		self.page = 0

		# holds last search result from any command (list, program, search)
		self.results = []

	def __getitem__(self, key):
		indx = int(key)-1
		return self.results[indx/VIDEO_PER_PAGE][indx % VIDEO_PER_PAGE]
		
	def __get_plugin__(self, channel):
		try:
			# import module & find requested class
			cdm = __import__(channel+"DataManager")
			cdmclass = getattr(cdm, channel+"DataManager")
			# create channel & retrieve streams
			return cdmclass(self)
		except ImportError:
			print >> sys.stderr, 'Error: DataManager for channel "%s" could not be found.' % channel
			return None

	def extra_help(self):
		if len(self.results) == 0:
			print >> sys.stderr, 'You need to run either a list, channels or programs command first'

	def get_channel_content(self, channel, program, search):
		'''Select channel Data Manager and get Program content'''
		self.channel = self.__get_plugin__(channel)
		if self.channel is not None:
			self.channel.retrieve_streams(program, search)
		else:
			print >> sys.stderr, "Error: Channel content could not be found."



class MyCmd(Cmd):
	def __init__(self, options, nav=None):
		Cmd.__init__(self)
		self.prompt = 'fr-replay> '
		self.intro = '\nType "help" to see available commands.'
		if nav is None:
			self.nav = Navigator(options)
		else:
			self.nav = nav

	def postcmd(self, stop, line):
		if line.startswith(HIST_CMD):
			self.nav.last_cmd = line
		return stop


	def do_add(self, arg):
		'''add channel[:program] to results ...
	display available videos or search for given videos(s)'''
		channel = ''
		program = ''
		search = ''
		if arg != '':
			# Split search parameter (after %)
			args1 = arg.split("%",2)
			if ( len(args1) == 2 ):
				search = args1[1]
			# Split channel:program parameter (separated by :)
			args2 = args1[0].split(":",2)
			channel = args2[0]
			if ( len(args2) == 2 ):
				program = args2[1]
				
		self.nav.get_channel_content(channel, program, search)
		try:
			print_results(self.nav.results[self.nav.page], True, page=self.nav.page)
		except IndexError:
			print >> sys.stderr, 'Error: unknown channel'
		except ValueError:
			print >> sys.stderr, 'Error: wrong argument; must be an integer'

	def do_previous(self, arg):
		if self.nav.last_cmd.startswith(HIST_CMD) and self.nav.page > 0:
			self.nav.page -= 1
			print_results(self.nav.results[self.nav.page], page=self.nav.page)
		return False

	def do_next(self, arg):
		if self.nav.last_cmd.startswith(HIST_CMD):
			self.nav.page += 1
			if self.nav.page > len(self.nav.results)-1:
				self.nav.more = True
				self.onecmd(self.nav.last_cmd)
				self.nav.more = False
			else:
				print_results(self.nav.results[self.nav.page], page=self.nav.page)
		return False

	def do_url(self, arg):
		'''url NUMBER [NUMBER] ...
	show the url of the chosen videos'''
		print ':: Display video(s) url: ' + ', '.join('#%s' % i for i in arg.split())
		playlist = []
		for i in arg.split():
			try:
				video = self.nav.results[0][int(i)-1]
				print video['title']+" : "+video['url']
			except ValueError:
				print >> sys.stderr, '"%s": wrong argument, must be an integer' % i
				return
			except IndexError:
				print >> sys.stderr, 'Error: no video with this number: %s' % i
				self.nav.extra_help()
				return

	#~ def do_player_url(self, arg):
		#~ '''player_url NUMBER
	#~ show the Flash player url of the chosen video'''
		#~ try:
			#~ video = self.nav[arg]
			#~ if 'player_url' not in video:
				#~ get_video_player_info(video, self.nav.options)
			#~ print video['player_url']
		#~ except ValueError:
			#~ print >> sys.stderr, 'Error: wrong argument (must be an integer)'
		#~ except IndexError:
			#~ print >> sys.stderr, 'Error: no video with this number'
			#~ self.nav.extra_help()

	def do_info(self, arg):
		'''info NUMBER
		display details about chosen video'''
		try:
			video = self.nav[arg]
			if 'info' not in video:
				get_video_player_info(video, self.nav.options)
			print '%s== %s ==%s'% (BOLD, video['title'], NC)
			print video['info']
		except ValueError:
			print >> sys.stderr, 'Error: wrong argument (must be an integer)'
		except IndexError:
			print >> sys.stderr, 'Error: no video with this number'
			self.nav.extra_help()

	def do_play(self, arg):
		'''play NUMBER [NUMBER] ...
	play the chosen videos'''
		playlist = []
		for i in arg.split():
			try:
				playlist.append(self.nav.results[0][int(i)-1])
			except ValueError:
				print >> sys.stderr, '"%s": wrong argument, must be an integer' % i
				return
			except IndexError:
				print >> sys.stderr, 'Error: no video with this number: %s' % i
				self.nav.extra_help()
				return
		print ':: Playing video(s): ' + ', '.join('#%s' % i for i in arg.split())
		for v in playlist:
			play(self.nav.channel.get_stream_uri(v), self.nav.options)

	def do_record(self, arg):
		'''record NUMBER [NUMBER] ...
	record the chosen videos to a local file'''
		playlist = []
		for i in arg.split():
			try:
				playlist.append(self.nav[i])
			except ValueError:
				print >> sys.stderr, '"%s": wrong argument, must be an integer' % i
				return
			except IndexError:
				print >> sys.stderr, 'Error: no video with this number: %s' % i
				self.nav.extra_help()
				return
		print ':: Recording video(s): ' + ', '.join('#%s' % i for i in arg.split())
		# TODO: do that in parallel ?
		for v in playlist:
			record(v, self.nav.options)

	def complete_lang(self, text, line, begidx, endidx):
		if text == '':
			return LANG
		elif text.startswith('d'):
			return ('de',)
		elif text.startswith('f'):
			return('fr',)
		elif text.startswith('e'):
			return('en',)

	def do_lang(self, arg):
		'''lang [fr|de|en]
	display or switch to a different language'''
		if arg == '':
			print self.nav.options.lang
		elif arg in LANG:
			self.nav.options.lang = arg
			self.nav.clear_info()
		else:
			print >> sys.stderr, 'Error: lang could be %s' % ','.join(LANG)

	def complete_quality(self, text, line, begidx, endidx):
		if text == '':
			return QUALITY
		elif text.startswith('s'):
			return ('sd',)
		elif text.startswith('h'):
			return('hd',)

	def do_quality(self, arg):
		'''quality [sd|hd]
	display or switch to a different quality'''
		if arg == '':
			print self.nav.options.quality
		elif arg in QUALITY:
			self.nav.options.quality = arg
			self.nav.clear_info()
		else:
			print >> sys.stderr, 'Error: quality could be %s' % ','.join(QUALITY)
			
	def do_programs(self, arg):
		'''programs channel...
	display available programs for channel'''
		channel = self.nav.__get_plugin__(arg)
		if channel is not None:
			channel.list_programs()

	def do_channels(self, arg):
		'''channels...
	display available programs for channel'''
		print ':: Available channels'
		print ':: CanalPlus'
		print ':: Arte'
		print ':: Pluzz'

	def do_get(self, arg):
		'''get channel[:program] results ...
	display available videos or search for given videos(s)'''
		del self.nav.results[:]
		self.do_add(arg)


	def do_dldir(self,arg):
		'''dldir [PATH] ...
	display or change download directory'''
		if arg == '':
			print self.nav.options.dldir
			return
		arg = expand_path(arg) # resolve environment variables and '~'s
		if not os.path.exists(arg):
			print >> sys.stderr, 'Error: wrong argument; must be a valid path'
		else:
			self.nav.options.dldir = arg

	def do_help(self, arg):
		'''print the help'''
		if arg == '':
			print '''COMMANDS:
	channels                   get available channels list for channel
	programs channel           get programs list for channel

	get    channel[:program]   get videos provided by channel[:program]
	add    channel[:program]   add videos provided by channel[:program] to list
	search STRING	           filter videos list with STRING
	
	next			 list videos of the next page
	previous		 list videos of previous page

	url NUMBER	   show url of video
	play NUMBERS	 play chosen videos
	record NUMBERS   download and save videos to a local file
	info NUMBER	  display details about given video

	dldir [PATH]	 display or change download directory
	lang [fr|de|en]  display or switch to a different language
	quality [sd|hd]  display or switch to a different video quality

	help			 show this help
	quit			 quit the cli
	exit			 exit the cli'''
		else:
			try:
				print getattr(self, 'do_'+arg).__doc__
			except AttributeError:
				print >> sys.stderr, 'Error: no help for command %s' % arg

	def do_quit(self, arg):
		'''quit the command line interpreter'''
		return True

	def do_exit(self, arg):
		'''exit the command line interpreter'''
		return True

	def do_EOF(self, arg):
		'''exit the command line interpreter'''
		print
		return True

	def default(self, arg):
		print >> sys.stderr, 'Error: don\'t know how to %s' % arg

	def emptyline(self):
		pass

def die(msg):
	print >> sys.stderr, 'Error: %s. See %s --help' % (msg, sys.argv[0])
	sys.exit(1)

def print_results(results, verbose=True, page=1):
	'''print list of video:
	title in bold with a number followed by teaser'''
	resume = False
	for i in range(len(results)):
		print '%s(%d) %s'% (BOLD, i+1+VIDEO_PER_PAGE*page, results[i]['title'] + NC)
		if verbose:
			print '	1st diffusion : '+ results[i]['date'] + ' ' + results[i]['time'] + ', duration : ' + results[i]['duration']
			print '	'+ results[i]['desc']
		# wait user action to display items or resume
		if not(resume) and (i+1) % VIDEO_PER_PAGE == 0:
			print 
			attr = termios.tcgetattr(sys.stdin)
			while True:
				try:
					print "> Waiting for %d items - Continue [Y/n] or [r]esume ? " % (len(results) - (i+1))
					tty.setcbreak(sys.stdin.fileno())
					kbinput = ord(sys.stdin.read(1))
				finally:
					termios.tcsetattr(sys.stdin, termios.TCSADRAIN, attr)
				if kbinput in [ 10, 32, 78, 110, 89, 121, 82, 114 ]:    # SPACE, CRLF, 'n', 'N', 'y', 'Y', 'r', 'R' allowed
					break
			if kbinput == 82 or kbinput == 114:    # r ou R
				resume = True
			elif kbinput == 78 or kbinput == 110:    # n ou N
				break
			# else: 89 ou 121 ou 10 ou 32 >> y, Y, ' ', CRLF

	#~ print ':: Display page %d' % page
	if len(results) == 0:
		print ':: the search returned nothing'

def play(video, options):
	#~ vurl = make_cmd_args(video, options, streaming=True)
	if video is False:
		print >> sys.stderr, 'Command failed.'
		return
	
	player_cmd = find_player(PLAYERS)

	if player_cmd is not None:
		print ':: Streaming from %s' % video
		p2 = subprocess.Popen(player_cmd.split(' ') + video.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		p2.wait()
	else:
		print >> sys.stderr, 'Error: no player has been found.'

def record(video, options):
	cwd = os.getcwd()
	os.chdir(options.dldir)
	#~ vurl = make_cmd_args(video, options)
	output_file = video['title']+'__'+urlparse.urlparse(video).path.split('/')[-1]
	log_file = output_file+'.log'
	cmd = "wget -r --tries=10 -o %s -O %s %s" % (output_file.replace(' ', '_'), log_file.replace(' ', '_'), video.replace(' ','%20'))
	if os.path.exists(output_file):
		print ':: Resuming download of %s' % output_file
	else:
		print ':: Downloading to %s' % output_file
	print cmd
	is_file_present = os.path.isfile(output_file)
	try:
		subprocess.check_call(cmd.split(' '))
		if os.path.isfile(log_file):
			os.unlink(log_file)
		print ':: Download complete'
	except OSError:
		print >> sys.stderr, 'Error: record command not found. Record aborted.'
	except subprocess.CalledProcessError:
		print >> sys.stderr, 'Error: download command failed. Record failed.'
		# delete file if it was not there before conversion process started
		if os.path.isfile(output_file) and not is_file_present:
			os.unlink(output_file)

	os.chdir(cwd)

def make_cmd_args(video, options, streaming=False):
	return None

def expand_path(path):
	if '~' in path:
		path = os.path.expanduser(path)
	if ('$' in path) or ('%' in path):
		path = os.path.expandvars(path)
	return path

def find_in_path(path, filename):
	'''is filename in $PATH ?'''
	for i in path.split(':'):
		if os.path.exists('/'.join([i, filename])):
			return True
	return False

def find_player(players):
	for p in players:
		cmd = p.split(' ')[0]
		if cmd.startswith('/') and os.path.isfile(cmd):
			return p
		else:
			if find_in_path(os.environ['PATH'], cmd):
				return p
	return None

def main():
	usage = '''Usage: %prog url|play|record [OPTIONS] URL
	   %prog search [OPTIONS] STRING...
	   %prog

Play or record videos from arte VIDEOS website without a mandatory browser.

In the first form, you need the url of the video page
In the second form, just enter your search term
In the last form (without any argument), you enter an interactive interpreter
(type help to get a list of available commands, once in the interpreter)

COMMANDS
	url	 show the url of the video
	play	play the video directly
	record  save the video into a local file
	search  search for a video on arte+7
			It will display a numbered list of results and enter
			a simple command line interpreter'''

	parser = OptionParser(usage=usage)
	parser.add_option('-d', '--downloaddir', dest='dldir', type='string',
			default=DEFAULT_DLDIR, action='store', help='directory for downloads')
	parser.add_option('-l', '--lang', dest='lang', type='string', default=DEFAULT_LANG,
			action='store', help='language of the video fr, de, en (default: fr)')
	parser.add_option('-q', '--quality', dest='quality', type='string', default=DEFAULT_QUALITY,
			action='store', help='quality of the video sd or hd (default: hd)')
	parser.add_option('--verbose', dest='verbose', default=False,
			action='store_true', help='show output of rtmpdump')

	options, args = parser.parse_args()

	if not os.path.exists(options.dldir):
		die('Invalid Path')
	if options.lang not in ('fr', 'de', 'en'):
		die('Invalid option')
	if options.quality not in ('sd', 'hd'):
		die('Invalid option')
	if len(args) < 2:
		MyCmd(options).cmdloop()
		sys.exit(0)
	if args[0] not in ('url', 'play', 'record', 'search'):
		die('Invalid command')

	if args[0] == 'url':
		print get_rtmp_url(args[1], quality=options.quality, lang=options.lang)[0]

	elif args[0] == 'play':
		play({'url':args[1]}, options)
		sys.exit(1)

	elif args[0] == 'record':
		record({'url':args[1]}, options)

	elif args[0] == 'search':
		term = ' '.join(args[1:])
		print ':: Searching for "%s"' % term
		nav = Navigator(options)
		nav.search(term)
		nav.last_cmd = 'search %s' % term
		if nav.results is not None:
			print_results(nav.results[0])
			MyCmd(options, nav=nav).cmdloop()

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print '\nAborted'
