# -*- coding: utf-8 -*-

__addonID__      = "plugin.video.tf1replay"
__author__       = "vilain_mamuth"
__url__          = "http://vm.damota.net"
__credits__      = "Merci aux auteurs du plugin Pluzz pour leur inspiration :)"
__date__         = "05-11-2012"
__version__      = "0.4.3"

import xbmcplugin
import xbmcgui
import xbmcaddon

import urllib
import urllib2

import sys
import os
import re
import time
import md5

try:
    import json
except ImportError:
    import simplejson as json
    
import pprint

from traceback import print_exc
from BeautifulSoup import BeautifulSoup

addon	= xbmcaddon.Addon(__addonID__)	
ROOTDIR            = addon.getAddonInfo('path')
BASE_RESOURCE_PATH = os.path.join( ROOTDIR, "resources" )
MEDIA_PATH = os.path.join( BASE_RESOURCE_PATH, "media" )

__settings__ = xbmcaddon.Addon(__addonID__)
__language__ = __settings__.getLocalizedString
DEBUG = __settings__.getSetting( "debug" ) == "true"

WEBSITE = "http://videos.tf1.fr"
WATSITE = "http://www.wat.fr"


TYPES = {'categories' :{
        "JT":"/programmes-tv-info/video-integrale/",
        "Magazines":"/magazine/video-integrale/",
        "Séries - Fictions":"/series-tv/video-integrale/",
        "Jeux":"/jeux-tv/video-integrale/",
        "Jeunesse":"/programmes-tv-jeunesse/video-integrale/",
        "Divertissement":"/emissions-tv/video-integrale/",
        "Téléfilms":"/telefilms/video-integrale/",
        "Sports":"/sport/video-integrale/"
        }}

PROGRAMMES = "/liste-videos/"

#entre xbmc et curl, pas le même user agent, ça génère des erreurs 403, on va forcer toutes les connections avec le même
USERAGENT = "Mozilla/5.0 (Ubuntu; X11; Linux x86_64; rv:8.0) Gecko/20100101 Firefox/8.0"

class Episode:
    imageUrl = ""
    pageUrl = ""
    prog = ""
    titre = ""
    
    

def get_content_for_type(type):
    content_list = list()
    for title,(path) in TYPES[type].items():
        content_list.append({'link' : path, 'title' : title})
    return content_list

def jsonPrettyPrint(jsonObject):
    pprint.pprint(jsonObject)

def get_category_episodes(url):
    print url
    html = urllib.urlopen(WEBSITE + url ).read()
    
    #Ce qui est génial avec le site de tf1 c'est qu'il n'est pas fait pareil partout....
    
    soup = BeautifulSoup(html)
    
    #Astuce pourrie pour éviter de récupérer les .teaser de la colonne de droite (pub, etc...)
    teasers = soup.find('li',{'class': re.compile(r'\bteaser\b')}).parent.findAll('li')
    
    if DEBUG:
        print "HTML teasers Block"
        print teasers
    
    if len(teasers)>0:
        episodes = list()
        for teaser in teasers:
            if DEBUG:
                print 'HTML teaser list item'
                print teaser
            ep = Episode()
            ep.imageUrl = teaser.find('img')['src']
            detail = teaser.find(re.compile("^h"), {'class': re.compile(r'\btitre\b') })
            ep.titre = detail.find('a').renderContents()
            ep.pageUrl = detail.find('a')['href']
            programme = teaser.find('div', {'class': re.compile(r'\bprog\b') })
            if programme:
                ep.prog = programme.strong.renderContents()
            if DEBUG:
                print "episode infos"
                print "image " + ep.imageUrl
                print "programme" + ep.prog
                print "titre" + ep.titre
                print "url" + ep.pageUrl
                

            episodes.append(ep)
    
    
#    pattern = """<li class="teaser.*</li>"""
#    pattern1 = """<li class="teaser">\s+<div class="visuel">\s+<a onmousedown="" href="/fringe/saison-4/episodes/episode-16-saison-04-adam-et-eve-7543496.html" rel="nofollow">\s+<img src="http://s.tf1.fr/mmdia/i/92/7/fringe-saison-04-episode-16-10768927unwqy_1936.jpg?v=2" cp="DR" alt="Fringe - Saison 04 - Episode 16" class="shadow shadow240px">\s+</a>\s+<a onmousedown="" href="/fringe/saison-4/episodes/episode-16-saison-04-adam-et-eve-7543496.html" class="dureeR11" rel="nofollow">42min<span class="integrale bgcc">Replay</span></a>\s+</div>\s+<div class="infosIntegrale">\s+<div class="date t3 c5">\s+<span class="dateTs" style="">Le 27/09/2012</span>\s+|\s+<span><img src="http://s.tf1.fr/img/str/x.gif" alt="" class="pBulles"> 3 commentaires</span> </div> <h3 class="titre t10"> <a href="/fringe/saison-4/episodes/episode-16-saison-04-adam-et-eve-7543496.html">Episode 16 Saison 04 - Adam et Eve</a> </h3> <p class="texte t11 c4"> Un incident se produit à bord d'un avion de Vertus Air, sur un vol Paris - New York. Comme dans le monde de Peter, l'affaire est liée à un ...
# </p> <div class="fbLike"><fb:like href="http://videos.tf1.fr/fringe/saison-4/episodes/episode-16-saison-04-adam-et-eve-7543496.html" layout="box" show_faces="false" width="360px" height="40px" class="FBLike fb_edge_widget_with_comment fb_iframe_widget" tf1_conid="4434845" tf1_chaineid="2566327" tf1_rubid="4377995" tf1_tcoid="4" fb-xfbml-state="rendered"><span style="height: 35px; width: 360px; "><iframe id="f15986fb04" name="f109deca8" scrolling="no" style="border: none; overflow: hidden; height: 35px; width: 360px; " title="Like this content on Facebook." class="fb_ltr" src="http://www.facebook.com/plugins/like.php?api_key=122614660307&amp;channel_url=http%3A%2F%2Fstatic.ak.facebook.com%2Fconnect%2Fxd_arbiter.php%3Fversion%3D11%23cb%3Df3a8b296%26origin%3Dhttp%253A%252F%252Fvideos.tf1.fr%252Ff14697ec2c%26domain%3Dvideos.tf1.fr%26relation%3Dparent.parent&amp;extended_social_context=false&amp;href=http%3A%2F%2Fvideos.tf1.fr%2Ffringe%2Fsaison-4%2Fepisodes%2Fepisode-16-saison-04-adam-et-eve-7543496.html&amp;layout=standard&amp;locale=fr_FR&amp;node_type=link&amp;sdk=joey&amp;show_faces=false&amp;width=360"></iframe></span></fb:like></div> </div> </li>"""
#
    match = re.search("""<li class="precedente c4 t3"><a onmousedown="sjs\(this,'#([^']*)'\)" [^>]*><img [^>]*>""",html)
    if match:
        page_precedente = match.group(1).replace('|','/')
    else:
        page_precedente = None
        
    match = re.search("""<li class="suivante c4 t3"><a onmousedown="sjs\(this,'#([^']*)'\)" [^>]*>\s*Suivant""",html)
    if match:
        page_suivante = match.group(1).replace('|','/')
    else:
        page_suivante = None
        
    print "precedente"
    print page_precedente
    print "suivante"
    print page_suivante
    
#    patternMode = 1
#    
#    vignettes = re.findall("""<img src="([^"]+)" [^>]*></a>\s+<a [^>]*>[^<]*<span class="[^"]*">[^<]*</span></a>\s+</div>\s+<div class="description">\s+<div class="[^"]*">([^<]+)</div>\s+<div class="prog t4 c5"><strong>([^"]+)</strong></div>\s+<h3 class="titre t4"><a href="([^"]+)">([^"]+)</a>""",html)
#    if len(vignettes)<1:
#        #on essaie un autre pattern
#        patternMode = 2
#        print "2e pattern"
#       #vignettes = re.findall("""<img src="([^"]+)" [^>]*></a>\s+<a [^>]*>[^<]*<span [^>]*>[^<]*</span></a>\s+</div>\s+<div [^>]*>\s+<div [^>]*> <span [^>]*>[^<]*</span>[^<]<span><img [^>]*>[^<]</span>\s+</div>\s+<h3 [^>]*><a href="([^"]+)">([^<]*)</a></h3>""",html)
#        vignettes = re.findall("""<img src="([^"]+)" [^>]*></a>\s+<a [^>]*>[^<]*<span [^>]*>[^<]*</span></a>\s+</div>\s+<div [^>]*>\s+<div [^>]*>\s+<span [^>]*>[^<]*</span>[^<]*<span><img [^>]*>[^<]*</span>\s+</div>\s+<h3 [^>]*><a href="([^"]+)">([^<]*)""",html)
#                                 #<img src="xxxxxxx" xxxxx></a>xxx<a xxxxx>xxxxx<span xxxxx>xxxxx</span></a>xxx</div>xxx<div xxxxx>xxx<div xxxxx>---<span ----->-----</span>-----<span><img ----->_____</span> </div> <h3 class="titre t10"><a href="/les-30-histoires-les-plus-spectaculaires/emission-du-14-mai-2011-les-30-histoires-les-plus-spectaculaires-6443508.html">Emission du 14 mai 2011 - Les 30 histoires les plus spectaculaires</a></h3> <p class="texte t11 c4">Carole Rousseau et Jacques Legros vous présentent Les 30 histoires les ...</p> <div class="fbLike"><span class="inv conId145039">3751637</span><span class="inv chaineId145039">2566327</span><span class="inv rubId145039">2689740</span><span class="inv tcoId145039">4</span></div> </div> </li>
#    print "vignette "
#    print vignettes
    episode_list = list()

#    if patternMode == 1:
#        for image_url,date,titre,lien,desc in vignettes:
#            print "date " + date
#            print "titre " + titre
#            print "lien " + lien
#            print "desc " + desc
#            print 'image ' + image_url
#            episode_list.append({'link': WEBSITE + lien , 'title':BeautifulSoup(titre + " - " + desc, convertEntities="html",fromEncoding="utf-8").prettify() , 'image':image_url})
    
#    if patternMode == 2:
#        for image_url,lien,titre in vignettes:
#            print "titre " + titre
#            print "lien " + lien
#            print 'image ' + image_url
#            episode_list.append({'link': WEBSITE + lien , 'title':BeautifulSoup(titre, convertEntities="html",fromEncoding="utf-8").prettify() , 'image':image_url})
    
    for ep in episodes:
        if ep.prog != "":
            episode_list.append({'link': WEBSITE + ep.pageUrl , 'title': BeautifulSoup(ep.prog + " - " + ep.titre, convertEntities="html",fromEncoding="utf-8").prettify() , 'image':ep.imageUrl})
        else:
            episode_list.append({'link': WEBSITE + ep.pageUrl , 'title': BeautifulSoup(ep.titre, convertEntities="html",fromEncoding="utf-8").prettify() , 'image':ep.imageUrl})
        
    return page_precedente, page_suivante, episode_list
    
def get_all_episodes(url):
    print url
    html = urllib.urlopen(WEBSITE + url ).read()

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
    


def get_episode(url):
    hasHD = False
    
    #get the id
    req = urllib2.Request(url)
    req.add_header('User-Agent', USERAGENT)
    response = urllib2.urlopen(req).read()
    video_id = re.compile('mediaId : (.*?),').findall(response)[0]
    print 'video_id : ' + video_id
    referer_url = re.compile('url : "(.*?)"').findall(response)[0]
    #print "referer " + referer_url
    
    content = urllib2.Request(WATSITE + '/interface/contentv3/' + video_id)
    jsonVideoInfos = urllib2.urlopen(content).read()
    
    videoInfos = json.loads(jsonVideoInfos)
    
    if DEBUG:
        jsonPrettyPrint(videoInfos)

    #on suppose que si la première partie est en HD, les autres aussi
    if videoInfos['media']['files'][0]['hasHD'] and __settings__.getSetting( "preferhd" )=="true":
        print "Hachdééééééééééé"
        hasHD = True
                
    #choppage de toutes les parties
    parts = []
    for vid in videoInfos['media']['files']:
        parts.append(str(vid['id']))
    
    parts_url = []
    
    for vid in parts:
        print "part: " + vid
        #get the episode url,
        # pour la clé, merci à https://github.com/monsieurvideo/get-flash-videos/blob/master/lib/FlashVideo/Site/Wat.pm
        # sans quoi rien n'eut été possible
        # je pourrai mourir en paix lorsque je saurai trouver ce genre de truc tout seul :))
        if hasHD:
            wat_url = "/webhd/" + vid
        else:
            wat_url = "/web/" + vid
        key = "9b673b13fa4682ed14c3cfa5af5310274b514c4133e9b3a81e6e3aba00912564"
        #on a besoin du timestamp en hexa sans le 0x du début
        dthex = hex(int(time.time()))[2:]
    
        h = md5.new()
        h.update(key + wat_url + dthex)
        token = h.hexdigest() + "/" + dthex
    
        #print "token : " + token
    
        if hasHD:
            url4videoPath = WATSITE + "/get/webhd/" + vid + "?token=" + token + "&domain=videos.tf1.fr&context=swfpu&country=FR&getURL=1&version=LNX%2011,1,102,55"    
        else:
            url4videoPath = WATSITE + "/get/web/" + vid + "?token=" + token + "&domain=videos.tf1.fr&context=swfpu&country=FR&getURL=1&version=LNX%2011,1,102,55"    
        print "url4video : " + url4videoPath
    
        #cette url envoi comme réponse la réelle adresse de la vidéo
        req = urllib2.Request(url4videoPath)
        req.add_header('User-Agent', USERAGENT)
        req.add_header('Referer' , referer_url)
        response = urllib2.urlopen(req).read()
        if DEBUG:
            print "reponse"
            print response
    
        # 2 types de réponses possibles :
        # soit on a l'url directe : http://
        # soit on a rtmpe,rtmpte://
        modeRtmp = 0
    	if response.find('rtmpe,')!=-1:
            modeRtmp = 1
            response = response[6:]
    	elif response.find('rtmp,')!=-1:
    		modeRtmp = 1
           	response = response[5:]
    
        if modeRtmp == 1:
            parts_url.append(response + ' swfUrl=http://www.wat.tv/images/v40/PlayerWat.swf swfVfy=true' )
        else:
            parts_url.append(response + '|User-Agent=' + urllib.quote(USERAGENT) + '&Cookie=' + urllib.quote('seen=' + vid))
        
    sep = " , "
    if len(parts_url)>1:
        video_url = "stack://" + sep.join(parts_url)
    else:
        video_url = parts_url[0]
        
    if DEBUG:
        print "video_url: "
        print video_url

    return video_url


def INDEX():
    #addDir('Chaines', 'chaines', 2, '')
    addDir('Categories', 'categories', 2, '')
    #addDir('Les plus vues', '/les-plus-vues', 3, '')
    addDir('Toutes les émissions', 'all', 4, '')
    
        
def SELECT_CATEGORY(type):
    categories = get_content_for_type(type)
    for category in categories:
        # pas d'icone pour le moment'
        #addDir(category['title'], category['link'], 3, icon)
        addDir(category['title'], category['link'], 3, '')

def SELECT_PROGRAM(type):
    progs = get_all_episodes(type)
    for prog in progs:
        # pas d'icone pour le moment'
        #addDir(category['title'], category['link'], 3, icon)
        addDir(prog['title'], prog['link'], 3, '')

def SELECT_EPISODE(url):
    print "SELECT_EPISODE"
    print WEBSITE + url

    page_precedente, page_suivante, episodes = get_category_episodes(url)
    
    if page_precedente != None:
        addDir('Page précédente', page_precedente, 3, '')
    
    for episode in episodes:
        print episode['title']
        addLink(episode['title'], sys.argv[0] + "?url=" + urllib.quote_plus(episode['link']) + "&mode=1&name=" + urllib.quote_plus(episode['title']), episode['image'])        

    if page_suivante != None:
        addDir('Page suivante', page_suivante, 3, os.path.join(MEDIA_PATH, "next-page.png"))
    
                    
def VIDEO(url, name):
        url = get_episode(url)


        # Play  video
        item = xbmcgui.ListItem(path=url)
	
        #if self.debug_mode:
        print "Lecture de la video %s with URL: %s"%(name, url)
        xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=item)
        
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

      
def addLink(name,url,iconimage):
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('IsPlayable', 'true')
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)
        return ok


def addDir(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
        

#######################################################################################################################    
# BEGIN !
#######################################################################################################################

if ( __name__ == "__main__" ):
    try:
        print "==============================="
        print "  TF1 Replay - Version: %s"%__version__
        print "==============================="
        print

        params=get_params()
        url=None
        name=None
        mode=None
        try:
                url=urllib.unquote_plus(params["url"])
        except:
                pass
        try:
                name=urllib.unquote_plus(params["name"])
        except:
                pass
        try:
                mode=int(params["mode"])
        except:
                pass
        print "Param HD: " + __settings__.getSetting( "preferhd" )
        print "Param Debug: " + __settings__.getSetting( "debug" )
        print "Mode: "+str(mode)
        print "URL: "+str(url)
        print "Name: "+str(name)

        if mode==None or url==None or len(url)<1:
                print "categories"
                INDEX()
        elif mode==1:
                print "index of : "+url
                VIDEO(url, name)
        elif mode==2:
                print "index of : "+url
                SELECT_CATEGORY(url)
        elif mode==3:
                print "index of : "+url
                SELECT_EPISODE(url)
        elif mode==4:
                print "all progs : "+url
                SELECT_PROGRAM(PROGRAMMES)

        #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
        xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
    except:
        print_exc()
