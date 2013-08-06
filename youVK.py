# youVK. Copyright: sadolit, 2013


#~/usr/bin/env python

# -*- coding: utf-8 -*-

import vkontakte
import vk_auth
import requests
import argparse

from pafy import Pafy
import os
from subprocess import check_call

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

""" Download and converts youtube video """

class Downloader():
    
    def __init__(self, url, out, author=u"", title=u""):
        self.url = url
        self.out = out
        self.filename = u""
        self.tmp = u"tmp.mp3"
        self.author = author 
        self.title = title
    
    def __createVideo(self):
        self.video = Pafy(self.url)

    def __download(self):
        best = self.video.getbest(preftype="mp4")
        self.filename = u"out." + best.extension
        best.download(progress=True, filepath=self.filename.encode('utf-8'))
    
    """ Converts video to mp3 using ffmpeg and 
    adds tags if they were given"""

    def __convert(self):
        try:
            print "\n\t\t\tExtracting audio...\n"

            check_call([u'ffmpeg', u'-v', u'0', u'-i',
            self.filename, u'-b', u'320K', self.tmp])
            
            print "\n\t\t\tAdding tags...\n"
            
            check_call([u'ffmpeg', u'-v', u'0', u'-i', self.tmp, u'-b', u'320K',
            u'-id3v2_version', '3',  
            u'-metadata', u'title=' + self.title, 
            u'-metadata', u'artist=' + self.author, self.out])
        except OSError as e:
            print '\nError converting file!\n'
            self.clean()
            raise e

    """ Removes video and mp3 file """
    
    def clean(self):
        try:
            os.remove(self.filename)
        except:
            print "\nError cleaning!\n"
        try:
            os.remove(self.tmp)
        except:
            print "\nError cleaning!\n"
        try:
            os.remove(self.out)
        except OSError as e:
            print "\nError cleaning!\n"
            raise e
   
    def process(self):
        self.__createVideo()
        self.__download()
        self.__convert()

""" Authorizes using given email and password. Returns vk.API object """

def authorize(email, password):
    (token,user_id) = vk_auth.auth(email, password,'2438578', 'audio')
    return vkontakte.API(token=token)
    
""" Returns audio upload URL """

def getUploadURL(vk):
    return vk.get('audio.getUploadServer')['upload_url']

""" Uploads given file to the server url. Returns response in text form """

def uploadAudio(URL, audioFile):
    try:
        files = {'file': open(audioFile, 'rb')}
    except IOError as e:
        raise e
    response = requests.post(URL, files=files).text
    return response

""" Helper function : returns content of string bettwen two of its substrings """

def getBetween(string, start, end):
    index = string.find(start)
    return string[index + start.__len__() : string.find(end, index)]

""" Parses given text of response and returns dictionary in form of {'server' : server, 'audio' : audio, 'hash' : hash} """

def parseOutput(response):
   server = getBetween(response, "server=", "&audio")
   audio = getBetween(response, "audio=", "&hash")
   hash = getBetween(response, "hash=", "\"")
   return {'server' : server, 'audio' : audio, 'hash' : hash}

""" Finally, saves file on the server. fmt_response should be in form of parseOutput return """

def save(vk, fmt_resp):
    vk.get('audio.save', server = fmt_resp['server'], audio = fmt_resp['audio'], hash = fmt_resp['hash'])

""" Parse command line arguments """

def parseArgs():  
    parser = argparse.ArgumentParser(description='youVK. author:sadolit')
    parser.add_argument("-l", "--link", help = "Youtube video link", required = True)
    parser.add_argument('-e', '--email', help = "User email", required = True)
    parser.add_argument('-p', '--password', help = "Password", required =  True)
    parser.add_argument("-a", "--author", help = "Author to be added to ID3 tag of the audio", required=False)
    parser.add_argument("-t", "--title", help = "Title to be added to ID3 tag of the audio", required=False)
    arg_list = parser.parse_args()
    return arg_list

def main(args):
    filename = "out.mp3"
    try:
        print "\n\t\t\tAuthorizing to vk...\n"
        vk = authorize(args.email, args.password)
    except RuntimeError:
        print "\nAuthorization error!"
        return
    print "\n\t\t\tDone!\n"
    try:
        downloader = Downloader(args.link, filename, args.author, args.title)
        downloader.process()
    except KeyError:
        print "\nError downloading video!"
        return
    try:
        print "\n\t\t\tUploading to vk...\n"        
        save(vk, parseOutput(uploadAudio(getUploadURL(vk), filename)))
    except Exception:
        print "\nError uploading to vk!\n"
        return
    print "\n\t\t\tDone!\n"
    print "\n\t\t\tCleaning...\n"
    downloader.clean()
    print "\n\t\t\tDone!\n"

if __name__ == "__main__" :
    args = parseArgs()
    main(args)


