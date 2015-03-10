fr-tv-replay
=============

Debug in progress, no release for now.....

Search &amp; play several French Television Replay streams (Pluzz, Arte, Canal+) - Python / CLI

This application will list & play streams available on several French TV channels :
 * Pluzz
 * Arte
 * Canal+

*Warning for all users*

 * All streams are **copyrighted by France Televisions, ARTE and Canal+**. 
 * You are **NOT** free to *share*, *sell* or *modify* those videos !

*Reasons why i wrote this app'*

This command-line software was written in Python as an alternative solution to avoid use of Flash Player which is not optimized for Linux-based OS. This may also help you if like me your internet connexion bandwith is too small to watch HD live streams.

This is my first app with Python, so please be clement... 

It was originally based on *solsticedhiver/arteVIDEOS* project, i made some tests & updates on it to make it work again then i made some adaptations for other channels.

How-to
------

Type :

    $ ./fr-replay.py 

Then you will be invited to get some more help :

    Type "help" to see available commands.
    fr-replay> help
  
Here is the help message :

    COMMANDS:
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
  	cache			 display programs in cache
  	clearcache		 clear programs in cache
  
  	# Simple commands
  	play NUMBERS	 play chosen videos
  	record NUMBERS   download and save videos to a local file
  	url NUMBER	   show url of video
  	info NUMBER	  display details about given video
  
  	# Configuration [DEPRECATED FOR NOW]
  	lang [fr|de|en]  display or switch to a different language
  	quality [sd|hd]  display or switch to a different video quality
  
  	help			 show this help
  	quit			 quit the cli
  	exit			 exit the cli

Sources
-------
Here are the sources which helped me a lot for this project, thanks to all their contributors.
 * https://github.com/solsticedhiver/arteVIDEOS (*fr-tv-replay* started from this project sources)
 * https://github.com/pelrol/xbmc-my-canal/
 * https://github.com/mikebzh44/France-TV-Pluzz-for-XBMC/
 * http://sourceforge.net/projects/artefetcher/
 * https://gitorious.org/grilo/grilo-lua-sources/

