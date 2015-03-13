fr-tv-replay
=============

Search &amp; play several French TV Replay streams & Radio podcasts (Pluzz, Arte, Canal+, France Inter) - Python / CLI

This application will list & play streams available on several French TV channels :
 * Pluzz
 * Arte
 * Canal+
 * France Inter

**Status :** [Functionnal](README.md#first-use) but debug in progress, no release for now..... (*Tests in progress on Ubuntu 14.04*)

----

**Warning for all users**

 * All streams are **copyrighted by France Televisions, ARTE, Canal+ & France Inter**. 
 * You are **NOT** free to *share*, *sell* or *modify* those videos !

----

***Reasons why i wrote this app'***

This command-line software was written in Python as an alternative solution to avoid use of Flash Player which is not optimized for Linux-based OS. This may also help you if like me your internet connexion bandwith is too small to watch HD live streams.

It is also more efficient for me to search & play my favorite streams from a single software like i do with a Syndication (RSS/Atom) feed aggregator for news, without having to surf on several websites....

This is my first app with Python, so please be clement... It was originally based on *[arteVIDEOS](https://github.com/solsticedhiver/arteVIDEOS)* project, i made some tests & updates on it to make it work again then i made some adaptations for other channels.

----

How-to
------

**CLI Interactive mode help**

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
	get    channel[:program][%search]   get streams provided by channel[:program] and filter content with [%search]
	list   [STRING]	                    display last results or [STRING] cache results if [STRING] arg set
	find   STRING                       find streams list with STRING in cache
	getall channel                      get all streams provided by channel
	                                    WARNING : this command will make huge number of server(s) connexions depending on channel/plugin, so it could take a long time... Please use it with parsimony !

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
	licence			                    show licence
	quit			                    quit the cli
	exit			                    exit the cli

**CLI non-interactive mode help**

Type :

    $ ./fr-replay.py --help

Here is the help message :

    Usage: 
    
    List / save replay streams with interactive or non-interactive command line interface
    - You should first try interactive interface to get used to replay channels and programs
    - After that, you can use non-interactive interface to plan your favorite streams record (with crontab for example).
    
    Interactive use :     fr-replay.py [OPTIONS]
    Non-interactive use : fr-replay.py list|record channel[:program] [--find STRING] [OPTIONS]
    
    Commands:
      list	                Display channel:[program] results
      record                Save result stream(s) into local file(s)
    
    Options:
      -h, --help            show this help message and exit
      -d DLDIR, --dldir=DLDIR
                            directory for downloads
      -l LANG, --lang=LANG  language of the video fr, de, en (default: fr)
      -q QUALITY, --quality=QUALITY
                            quality of the video sd or hd (default: hd)
      -f FIND, --find=FIND  filter results with string

**Requirements to download streams :** wget + ffmpeg or avconv

First use
--------
Type :

    $ ./fr-replay.py 
    Type "help" to see available commands.
    fr-replay> help

List channels

    fr-replay> channels

List programs for Arte

    fr-replay> programs Arte

Get 'plus7' streams from Arte

    fr-replay> get Arte:plus7

List programs for Pluzz

    fr-replay> programs Pluzz

Get 'france2' streams from Pluzz

    fr-replay> get Pluzz:france2

List programs for CanalPlus

    fr-replay> programs CanalPlus

Get 'Emissions' streams from CanalPlus

    fr-replay> get CanalPlus:Emissions

Find streams which match 'X:enius' from cache

    fr-replay> find X:enius

Find streams which match '10/03/15' from cache

    fr-replay> find 10/03/15

Play 5th item

    fr-replay> play 5

Play 5th then 8th items

    fr-replay> play 5 8

Sources
-------
Here are the sources which helped me a lot for this project, thanks to all their contributors.
 * https://github.com/solsticedhiver/arteVIDEOS (*fr-tv-replay* started from this project sources)
 * https://github.com/pelrol/xbmc-my-canal/
 * https://github.com/mikebzh44/France-TV-Pluzz-for-XBMC/
 * http://sourceforge.net/projects/artefetcher/
 * https://gitorious.org/grilo/grilo-lua-sources/

