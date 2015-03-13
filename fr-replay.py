#!/usr/bin/python2

########################################################################
#						   PLAYERS									#
########################################################################
# You can add your favorite player at the beginning of the PLAYERS tuple
# The command must read data from stdin
# The order is significant: the first player available is used
PLAYERS = (
		'vlc',
		'mplayer',
		'/usr/bin/totem', # you could use absolute path for the command too
		)

RECORDERS = (
		'ffmpeg',
		'avconv'
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

import time

VERSION = '0.3'
DEFAULT_LANG = 'fr'
QUALITY = ('sd', 'hd')
DEFAULT_QUALITY = 'hd'
DEFAULT_DLDIR = os.getcwd()

VIDEO_PER_PAGE = 10

LANG = ('fr', 'de', 'en')
HIST_CMD = ('channels', 'programs', 'get', 'add')

BOLD   = '[1m'
NC	 = '[0m'	# no color

class Navigator(object):
	def __init__(self, options):
		self.options = options
		self.more = False

		# holds last search result from any command (list, program, search)
		self.results = []

		# stream download list
		self.dllist = []
		
		# cache catalogs results
		self.catalog = {}
		self.searchs = {}

	def __getitem__(self, key):
		indx = int(key)-1
		return self.results[indx]

	def get_plugin(self, channel):
		try:
			# import module & find requested class
			cdm = __import__("plugin."+channel+"DataManager", fromlist=[channel+"DataManager"])
			cdmclass = getattr(cdm, channel+"DataManager")
			return cdmclass(self)
		except ImportError:
			print >> sys.stderr, 'Error: DataManager plugin for channel "%s" could not be found.' % channel
			return None
		except TypeError:
			print >> sys.stderr, 'Error: DataManager plugin class "%s" could not be loaded.' % (channel+"DataManager")
			return None

	def extra_help(self):
		if len(self.results) == 0:
			print >> sys.stderr, 'You need to run either a %slist%s, %schannels%s or %sprograms%s command first' % (BOLD, NC, BOLD, NC, BOLD, NC)

	def get_channel_content(self, channel, program):
		'''Select channel Data Manager plugin and get Program content'''
		self.channel = self.get_plugin(channel)
		if self.channel is not None:
			return self.channel.retrieve_streams(program)
		else:
			print >> sys.stderr, "Error: Channel content could not be found."



class MyCmd(Cmd):
	def __init__(self, options, nav=None):
		Cmd.__init__(self)
		self.prompt = 'fr-replay> '
		self.intro = '\nType %shelp%s to display available commands.' %(BOLD, NC)
		if nav is None:
			self.nav = Navigator(options)
		else:
			self.nav = nav

	def do_add(self, arg):
		'''add channel[:program][%search] to results ...
	display available videos or search for given videos(s)'''
		channel = ''
		program = ''
		searchstr = ''
		if arg != '':
			# Split search parameter (after %)
			args1 = arg.split("%",2)
			if ( len(args1) == 2 ):
				searchstr = args1[1]
			# Split channel:program parameter (separated by :)
			args2 = args1[0].split(":",2)
			channel = args2[0]
			if ( len(args2) == 2 ):
				program = args2[1]
				
		# manage cache requested programs for future use (find)
		if (channel+':'+program) not in self.nav.catalog.keys() :
			streams = self.nav.get_channel_content(channel, program)
			if streams is not None:
				# set source channel in streams in order to play / record it later
				for stream in streams:
					stream['channel']=channel
				self.nav.catalog[channel+':'+program] = streams
		else:
			streams = self.nav.catalog[channel+':'+program]
		
		if streams is not None:
			# if search enabled : search streams and cache search results
			if searchstr != '':
				streams = search(streams, searchstr)
				self.nav.searchs[channel+':'+program+'%'+searchstr] = streams
			
			for stream in streams:
				self.nav.results.append(stream)

			try:
				print ":: %d streams found, type %slist%s to display results or %sfind STRING%s for whole cache search" % (len(streams), BOLD, NC, BOLD, NC)
				#print_results(streams, True)
			except IndexError:
				print >> sys.stderr, 'Error: unknown channel'
			except ValueError:
				print >> sys.stderr, 'Error: wrong argument; must be an integer'
		else:
			print >> sys.stderr, 'Error: Not stream found, please check your %schannel[:program]%s request (program may be mandatory depending on channel plugin)' % (BOLD, NC)
			print >> sys.stderr, 'To get availables programs for requested channel, execute : %sprograms %s%s' % (BOLD, channel, NC)

	def do_url(self, arg):
		'''url NUMBER [NUMBER] ...
	show the url of the chosen videos'''
		print ':: Display video(s) url: ' + ', '.join('#%s' % i for i in arg.split())
		playlist = []
		for i in arg.split():
			try:
				video = self.nav.results[int(i)-1]
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

	def do_cache(self, arg):
		'''cache
		display programs cache'''
		print ":: %d programs in cache" % len(self.nav.catalog.keys())
		for entry in self.nav.catalog.keys():
			print ">> "+entry

	def do_clearcache(self, arg):
		'''cache
		clears programs cache'''
		self.nav.catalog = {}
		self.do_cache(arg)

	def do_find(self, arg):
		'''find
		find streams in cache'''
		print ":: find streams matching with <%s> in cache" % arg
		del self.nav.results[:]
		for program in self.nav.catalog.keys():
			for stream in self.nav.catalog[program]:
				if arg.lower() in stream['title'].lower() or arg.lower() in stream['date'].lower() or arg.lower() in stream['desc'].lower():
					self.nav.results.append(stream)
		print_results(self.nav.results)

	def do_list(self, arg):
		'''list
		display last results'''
		if len(arg) > 0:
			if arg in self.nav.catalog.keys():
				print ":: display '%s' program cache" % arg
				print_results(self.nav.catalog[arg])
			else:
				print >> sys.stderr, ":: Error : list '%s' was not found in program cache" % arg
		else:
			print ":: display last results"
			print_results(self.nav.results)

	def do_add4dl(self):
		'''add4dl
		add last search results to download list'''
		print ":: add last search results to download list"
		self.nav.dllist = list(self.nav.results)
		self.do_dllist()

	def do_info(self, arg):
		'''info NUMBER
		display details about chosen video'''
		try:
			video = self.nav[arg]
			if 'info' not in video:
				get_video_player_info(video, self.nav.options)
			print '%s== %s ==%s' % (BOLD, video['title'], NC)
			print '%s== %s ==%s' % (HIGH, video['info'], NC)
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
				playlist.append(self.nav.results[int(i)-1])
			except ValueError:
				print >> sys.stderr, '"%s": wrong argument, must be an integer' % i
				return
			except IndexError:
				print >> sys.stderr, 'Error: no video with this number: %s' % i
				self.nav.extra_help()
				return
		print ':: Playing video(s): ' + ', '.join('#%s' % i for i in arg.split())
		for v in playlist:
			channel = self.nav.get_plugin(v['channel'])
			play(channel.get_stream_uri(v), self.nav.options)

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
		for v in playlist:
			channel = self.nav.get_plugin(v['channel'])
			record(v, channel.DL_METHOD, channel.get_stream_uri(v), self.nav.options)

	def do_dllist(self):
		'''dllist
	displays ready for download streams'''
		print "\n:: following items are ready for download, type 'startdl' to start download..."
		print_results(self.nav.dllist)

	def do_startdl(self):
		'''startdl
	download the chosen videos to a local file'''
		for v in self.nav.dllist:
			print ':: Recording stream(s): ' + v['title']
			channel = self.nav.get_plugin(v['channel'])
			record(v, channel.DL_METHOD, channel.get_stream_uri(v), self.nav.options)

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
		channel = self.nav.get_plugin(arg)
		if channel is not None:
			programs = channel.list_programs()
			print ':: %d programs available :' % len(programs)
			for program in programs:
				print '.... %s (%s)' % (program['id'], program['desc'])

	def do_channels(self, arg):
		'''channels...
	display available programs for channel'''
		# TODO : get channels dynamically from plugin directory
		print ':: Available channels'
		print '.. CanalPlus'
		print '.. Arte'
		print '.. Pluzz'
		print '.. FranceInter'

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
	# About channels and programs
	channels                            get available channels list for channel
	programs channel                    get programs list for channel

	# Find streams
	get    channel[:program][%search]   get videos provided by channel[:program] and filter content with [%search]
	list   [STRING]	                    display last results or [STRING] cache results if [STRING] arg set
	find   STRING                       find videos list with STRING in cache

	# Stream dl commands
	add4dl                              add current results (displayed by 'list' command) to dllist
	dllist                              display streams to download
	startdl                             start download
	dldir [PATH]                        display or change download directory

	# Cache management
	cache			                    display programs cache
	clearcache		                    clear programs cache

	# Simple commands
	play NUMBERS	                    play chosen videos
	record NUMBERS                      download and save videos to a local file
	url NUMBER	                        show url of video
	info NUMBER	                        display details about given video

	# Configuration
	lang [fr|de|en]                     display or switch to a different language
	quality [sd|hd]                     display or switch to a different video quality

	help			                    show this help
	quit			                    quit the cli
	exit			                    exit the cli'''
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

def search(results, searchstr):
	found = []
	for i in range(len(results)):
		if searchstr.lower() in results[i]['title'].lower():
			found.append(results[i])
	return found

def print_results(results, verbose=True):
	'''print list of video:
	title in bold with a number followed by teaser'''
	resume = False
	for i in range(len(results)):
		print '%s(%d) %s'% (BOLD, i+1, results[i]['title'] + NC)
		if verbose:
			print '   1st diffusion : '+ results[i]['date'] + ' ' + results[i]['time'] + ', duration : ' + results[i]['duration']
			print '   %s' % results[i]['desc']
		# wait user action to display items or resume
		if not(resume) and (i+1) % VIDEO_PER_PAGE == 0:
			print 
			attr = termios.tcgetattr(sys.stdin)
			while True:
				try:
					print "> %d items next : Continue [Y/n] or [r]esume ? " % (len(results) - (i+1))
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

def record(video, dlmethod, url, options):
	cwd = os.getcwd()
	os.chdir(options.dldir)
	
	# create dl filename
	vdate = ''
	if video['date'] != '':
		vdate = video['date']
	dldate = time.strftime('%Y%m%d-%H%M%S',time.localtime())
	filename = "%s_%s_%s" % (dldate, vdate, video['title'])
	output_file = re.sub(r'\W+', '-', filename)+'.'+urlparse.urlparse(url).path.split('.')[-1]
	log_file = output_file+'.log'
	
	if dlmethod == 'WGET':
		# wget options : continue aborted download, disploay progressbar, retry 10 times, log
		cmd = "wget --progress=bar --tries=10 -c -O %s -o %s %s" % (output_file.replace(' ', '_'), log_file.replace(' ', '_'), url.replace(' ','%20'))
	elif dlmethod == 'FFMPEG':
		recorder = find_player(RECORDERS)
		cmd = recorder+" -i %s -c copy %s%s" % (url.replace(' ','%20'), output_file.replace(' ', '_'), ".mkv")
	else:
		print >> sys.stderr, 'Error: record method <%s> not supported. Record aborted.' % dlmethod
		return
		
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
		print >> sys.stderr, 'Error: record command for %s method not found. Record aborted.' % dlmethod
	except subprocess.CalledProcessError:
		print >> sys.stderr, 'Error: download command for %s method failed. Record failed.' % dlmethod
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
	usage = '''Usage: %prog play|record channel[:program] [--find STRING] [OPTIONS] URL
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
	parser.add_option('-d', '--downloaddir', dest='dldir', type='string', default=DEFAULT_DLDIR, action='store', help='directory for downloads')
	parser.add_option('-l', '--lang', dest='lang', type='string', default=DEFAULT_LANG, action='store', help='language of the video fr, de, en (default: fr)')
	parser.add_option('-q', '--quality', dest='quality', type='string', default=DEFAULT_QUALITY, action='store', help='quality of the video sd or hd (default: hd)')
	parser.add_option('-f', '--find', dest='find', type='string', default='', action='store', help='filter results with string')

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

	# Check command
	if args[0] not in ('record', 'list'):
		die('Invalid command')

	# 2nd arg is channel[:program] id (mandatory)
	cmd = MyCmd(options)
	cmd.do_get(args[1])
	
	# Diplay results
	if options.find != '':
		cmd.do_find(options.find)
	elif args[0] == 'list':
		cmd.do_list(args[1])

	if args[0] == 'record':
		cmd.do_add4dl()
		cmd.do_startdl()
		
	sys.exit(1)


if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print '\nAborted'
