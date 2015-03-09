# -*- coding: utf-8 -*-

# xbmc modules
import xbmc
import xbmcplugin
import xbmcgui
import xbmcaddon
# os and lib modules
import os
import sys 
import urllib
import urllib2
import re
import time
import cPickle as pickle
import zipfile
import simplejson as json
import ast
# print_exc
from traceback import print_exc
# parseDOM
import CommonFunctions
common = CommonFunctions
common.plugin = "plugin.video.FranceTVPluzz"


__addonID__         = "plugin.video.FranceTVPluzz"
__author__          = "JUL1EN094"
__date__            = "01-03-2013"
__version__         = "1.0.7"
__credits__         = ""
__addon__           = xbmcaddon.Addon( __addonID__ )
__settings__        = __addon__
__language__        = __addon__.getLocalizedString
__addonDir__        = __settings__.getAddonInfo( "path" )

   

# Global Variable
ROOTDIR             = __settings__.getAddonInfo('path')
BASE_RESOURCE_PATH  = os.path.join( ROOTDIR, "resources" )
MEDIA_PATH          = os.path.join( BASE_RESOURCE_PATH, "media" )
ADDON_DATA          = xbmc.translatePath( "special://profile/addon_data/%s/" % __addonID__ )
CACHEDIR            = os.path.join( ADDON_DATA, "cache")
THUMB_CACHE_PATH    = os.path.join( xbmc.translatePath( "special://profile/" ), "Thumbnails", "Video" )
FANART_PATH         = os.path.join( ROOTDIR, "fanart.jpg" )
# Web variable
USERAGENT           = "Mozilla/5.0 (Windows NT 5.1; rv:15.0) Gecko/20100101 Firefox/15.0.1"
# List of directories to check at startup
dirCheckList        = (CACHEDIR,)
# Catalogue
CATALOG_PATH        = os.path.join(CACHEDIR,'PluzzMobileCatalog.zip')
jsonmobilecatalog   = "http://webservices.francetelevisions.fr/catchup/flux/flux_main.zip"
catalogconffilename = "message_FT.json"
catalogcatfilename  = "categories.json"

if not os.path.exists(CACHEDIR) :
    os.makedirs(CACHEDIR, mode=0777)

class FranceTVPluzz:
    """
    main plugin class
    """
    debug_mode = False #self.debug_mode
    
    def __init__( self, *args, **kwargs ):
        print "==============================="
        print "  FranceTV Pluzz - Version: %s"%__version__
        print "==============================="
        print
        self.set_debug_mode()
        if self.debug_mode:
            print "Python version:"
            print sys.version_info
            print "ROOTDIR: %s"%ROOTDIR
            print "ADDON_DATA: %s"%ADDON_DATA
            print "CACHEDIR: %s"%CACHEDIR 
            print "FANART_PATH: %s"%FANART_PATH 
        params     = self.get_params()
        url        = None
        name       = None
        mode       = None
        iconimage  = None   
        cat        = ''        
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
        try:
            iconimage=urllib.unquote_plus(params["iconimage"])
        except:
            pass
        try:
            cat=urllib.unquote_plus(params["cat"])
        except:
            pass
                               
        if self.debug_mode:
            print "Mode: "+str(mode)
            print "URL: "+str(url)
            print "Name: "+str(name)
            print "Iconimage: "+str(iconimage)
            print "Catégorie : "+str(cat)
 
        # Check if directories in user data exist
        for i in range(len(dirCheckList)):
            self.checkfolder(dirCheckList[i]) 
    
        if mode==None or url==None or len(url)<1:
            self.download_catalog()
            self.addDir("Replays", "message_FT.json",1,os.path.join(MEDIA_PATH,'replay.png'),'')
            self.addDir("Directs", "message_FT.json",100,os.path.join(MEDIA_PATH,'live.png'),'')
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__ ( 30000 ) )
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
        
        elif mode==1:
            self.addDir("France 1ère", "catch_up_france1.json",2,os.path.join(MEDIA_PATH,'france1.png'),'')
            self.addDir("France 2", "catch_up_france2.json",2,os.path.join(MEDIA_PATH,'france2.png'),'')
            self.addDir("France 3", "catch_up_france3.json",2,os.path.join(MEDIA_PATH,'france3.png'),'')
            self.addDir("France 4", "catch_up_france4.json",2,os.path.join(MEDIA_PATH,'france4.png'),'')
            self.addDir("France 5", "catch_up_france5.json",2,os.path.join(MEDIA_PATH,'france5.png'),'')
            self.addDir("France Ô", "catch_up_franceo.json",2,os.path.join(MEDIA_PATH,'franceO.png'),'')
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__ ( 30000 ) )
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            
        elif mode==2:        
            zf          = zipfile.ZipFile(CATALOG_PATH)
            data        = zf.read(catalogcatfilename)
            jsoncat     = json.loads(data.decode('iso-8859-1'))
            categories  = jsoncat['categories']
            for cat in categories :
                cat_name          = cat['titre'].encode('utf-8')
                cat_infos         = {}
                cat_infos['Plot'] = cat['accroche'].encode('utf-8')
                self.addDir(str(cat_name),url,3,'','',cat_infos,cat_name)            
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__ ( 30000 ) )
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
         
        elif mode==3:
            xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
            zf          = zipfile.ZipFile(CATALOG_PATH)
            data        = zf.read(url)
            jsoncatalog = json.loads(data.decode('iso-8859-1'))
            if self.debug_mode :
                print "JSON :"
                print json.dumps(jsoncatalog, sort_keys=True, indent=4, separators=(',', ': '))
            programmes  = jsoncatalog['programmes']
            prog_list = []
            for programme in programmes :
                video_cat = programme['rubrique'].encode('utf-8')
                if video_cat == cat:
                    video_name  = programme['titre'].encode('utf-8')
                    if video_name not in prog_list :
                        video_url   = url
                        video_image = self.get_catalog_configuration(catalogconffilename)[1]+programme['url_image_racine'].encode('utf-8')+'.'+programme['extension_image'].encode("utf-8")
                        video_infos = {}
                        if programme['accroche'] :
                            video_infos['Plot']  = programme['accroche'].encode('utf-8')
                        if programme['realisateurs'] :
                        #    video_infos['Cast']      = programme['acteurs'].encode('utf-8')
			     actz = []
                             for acteur in programme['acteurs'].encode('utf-8').split(", ") :
				actz.append([acteur, ""])
			     video_infos['Cast'] = actz 
                        if programme['realisateurs'] :
                            video_infos['Director']  = programme['realisateurs'].encode('utf-8')
                        if programme['format'] :
                            video_infos['Genre']     = programme['format'].encode('utf-8')
                        if self.debug_mode :
                            print 'Programme Name       : '+video_name
                            print 'Programme video URL  : '+video_url
                            print 'Programme image_url  : '+video_image
                            print '------------------------------------------'
                        self.addDir(video_name,video_url,4,video_image,video_image,video_infos,cat)
                        prog_list.append(video_name)
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__ ( 30000 ) )
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )

        elif mode==4:
            xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
            zf          = zipfile.ZipFile(CATALOG_PATH)
            data        = zf.read(url)
            jsoncatalog = json.loads(data)
            if self.debug_mode :
                print "JSON :"
                print json.dumps(jsoncatalog, sort_keys=True, indent=4, separators=(',', ': '))
            programmes  = jsoncatalog['programmes']
            for programme in programmes :
                video_cat = programme['rubrique'].encode("utf-8")
                if video_cat == cat:
                    video_name  = programme['titre'].encode("utf-8")
                    if video_name == name : 
                        if programme['sous_titre'] != "" :
                            video_name  = video_name +' : '+programme['sous_titre'].encode("utf-8") 
                        video_url   = self.get_catalog_configuration(catalogconffilename)[0]+programme['url_video'].encode("utf-8")
                        video_image = self.get_catalog_configuration(catalogconffilename)[1]+programme['url_image_racine'].encode("utf-8")+'.'+programme['extension_image'].encode("utf-8")
                        video_infos = {}
                        if programme['accroche'] :
                            video_infos['Plot']      = programme['accroche'].encode("utf-8")
                        if programme['realisateurs'] :
                        #    video_infos['Cast']      = programme['acteurs'].encode("utf-8")
                             actz = []
			     for acteur in programme['acteurs'].encode('utf-8').split(", ") :
				actz.append([acteur, ""])
                             video_infos['Cast']      = actz
			if programme['realisateurs'] :
                            video_infos['Director']  = programme['realisateurs'].encode("utf-8")
                        video_infos['Genre'] = cat
                        if programme['format'] != '' :
                            video_infos['Genre']     = video_infos['Genre']+' - '+programme['format'].encode("utf-8")
                        if programme['genre_simplifie'] != '' :
                            video_infos['Genre']     = video_infos['Genre']+' - '+programme['genre_simplifie'].encode("utf-8")
                        if programme['duree'] :
                            video_infos['Duration']  = programme['duree'].encode("utf-8")
                        if programme['date'] :
                            video_infos['Year']      = int(programme['date'].split('-')[0].encode("utf-8"))
                            video_infos['Date']      = str(programme['date'].split('-')[2])+'-'+str(programme['date'].split('-')[1])+'-'+str(programme['date'].split('-')[0])
                            video_infos['Premiered'] = video_infos['Date'] 
                            video_name               = video_name+" : "+video_infos['Date']
                        if self.debug_mode :
                            print 'Programme Name       : '+video_name
                            print 'Programme video URL  : '+video_url
                            print 'Programme image_url  : '+video_image
                            print '------------------------------------------'
                        self.addLink(video_name,video_url,5,video_image,video_image,video_infos)
                        print "ADDLINK"
            self.clean_thumbnail(str(url))
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__ ( 30000 ) )
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )

        elif mode==5:
            item = xbmcgui.ListItem(path=url)
            xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=item)
                
        elif mode==100 :
            zf            = zipfile.ZipFile(CATALOG_PATH)
            data          = zf.read(url)
            jsoncatalog   = json.loads(data)
            if self.debug_mode :
                print "JSON :"
                print json.dumps(jsoncatalog, sort_keys=True, indent=4, separators=(',', ': '))
            configuration = jsoncatalog['configuration'] 
            directs       = configuration['directs']
            for direct in directs :
                direct_name    = direct['nom'].encode('utf-8')
                direct_video   = direct['video_ipad'].encode('utf-8')
                direct_image   = os.path.join(MEDIA_PATH, direct_name+'.png')
                infos          = {}
                infos['Title'] ='Direct :'+direct_name
                infos['Plot']  = ''
                self.addLink(direct_name,direct_video,5,direct_image,'',infos)
            xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=__language__ ( 30000 ) )
            xbmcplugin.endOfDirectory(int(sys.argv[1]))
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_LABEL )
            xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_DATE )
        
            
#   "id_diffusion":"76737822",
#   "code_programme":"chante",
#   "id_programme":"6663",
#   "titre":"Chante !",
#   "sous_titre":"Disgr\u00e2ce",
#   "accroche":"Tina, Audrey et Stan entrent dans l'\u00e2ge adulte...",
#   "url_image_racine":"\/staticftv\/ref_emissions\/2013-02-03\/COL_277040_csa1",
#   "extension_image":"jpg",
#   "datemodif_image":"1359792017",
#   "chaine":"france2",
#   "date":"2013-02-03",
#   "heure":"06:05",
#   "duree":"25",
#   "csa_code":"TP",
#   "csa_nom_long":"Tous publics",
#   "nb_vues":"",
#   "indice_selection_ftv_chaine":"72",
#   "indice_selection_ftv_home":"",
#   "rubrique":"S\u00e9rie & Fiction",
#   "format":"S\u00e9rie",
#   "genre_simplifie":"S\u00e9rie ",
#   "cible_publicitaire":"",
#   "production":"",
#   "nationalite":"fran\u00e7aise",
#   "presentateurs":"",
#   "invites":"",

    def get_catalog_configuration(self,filename) :
        zf              = zipfile.ZipFile(CATALOG_PATH)
        data            = zf.read(filename)
        catalog         = ast.literal_eval(data)
        configuration   = catalog['configuration']
        url_base_videos = configuration['url_base_videos']
        url_base_images = configuration['url_base_images']
        return url_base_videos, url_base_images        
    
    def download_catalog(self):
        if os.path.exists(CATALOG_PATH):
            os.remove(CATALOG_PATH)
        urllib.urlretrieve(jsonmobilecatalog,CATALOG_PATH)       
    
    def set_debug_mode(self):
        self.debug_mode=__settings__.getSetting('debug')
        if self.debug_mode== 'true':
            self.debug_mode = True
        else:
            self.debug_mode = False
        print "FranceTV Pluzz:self.debug_mode Mode:"
        print self.debug_mode        
        
    def addLink(self,name,url,mode,iconimage,fanart,infos={}):
        u  =sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)
        ok =True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        infos['Title'] = name
        liz.setInfo( type="Video", infoLabels=infos )
        liz.setProperty('IsPlayable', 'true')
        liz.setProperty('Fanart_Image', fanart )
        ok =xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz)
        return ok         

    def addDir(self,name,url,mode,iconimage,fanart,infos={},cat=''):
        u  =sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)+"&iconimage="+urllib.quote_plus(iconimage)+"&cat="+urllib.quote_plus(cat)
        ok =True
        liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        infos['Title'] = name
        liz.setInfo( type="Video", infoLabels=infos )
        if fanart != '' :
            liz.setProperty('Fanart_Image',fanart)
        else :
            liz.setProperty('Fanart_Image',FANART_PATH)
        ok =xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok
    
    def get_params(self):
        param      =[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
            params         =sys.argv[2]
            cleanedparams  =params.replace('?','')
            if (params[len(params)-1]=='/'):
                params     =params[0:len(params)-2]
            pairsofparams  =cleanedparams.split('&')
            param={}
            for i in range(len(pairsofparams)):
                splitparams={}
                splitparams=pairsofparams[i].split('=')
                if (len(splitparams))==2:
                    param[splitparams[0]]=splitparams[1]
        return param

    def get_soup(self,url,referer):
        req  = urllib2.Request(url)
        req.add_header('User-Agent',USERAGENT)           
        req.add_header('Referer',referer)
        soup = urllib2.urlopen(req).read()
        if (self.debug_mode):
            print "get_soup : " + url
            print "referer  : " + referer
            print str(soup)
        return soup

    def checkfolder(self,folder):
        try:
            if not os.path.exists(folder):
                print "checkfolder Impossible to find the directory - trying to create the directory: "+folder
                os.makedirs(folder)
        except Exception, e:
            print "Exception while creating folder "+folder
            print str(e)

    def clean_thumbnail(self,video_url):
        try:
            filename = xbmc.getCacheThumbName(video_url)
            filepath = xbmc.translatePath(os.path.join(THUMB_CACHE_PATH,filename[0],filename))
            if os.path.isfile(filepath):
                os.remove(filepath)
                if self.debug_mode:
                    print "Deleted %s thumb matching to %s video"%(filepath,video_url)
            elif self.debug_mode:
                print "No thumb found %s thumb matching to %s video"%(filepath,video_url)
            return True
        except:
            print "Error: clean_thumbnail()"
            print_exc()
            return False  

#######################################################################################################################    
# BEGIN !
#######################################################################################################################

if ( __name__ == "__main__" ):
    try:
        FranceTVPluzz()
    except:
        print_exc()