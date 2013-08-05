from pafy import Pafy
import os

class Downloader():
    def __init__(self, url, out):
        self.url = url
        self.out = out
    
    def __createVideo(self):
        self.video = Pafy(self.url)

    def __download(self):
        best = self.video.getbest(preftype="mp4")
        self.filename = u"out." + best.extension
        best.download(progress=True, filepath=self.filename.encode('utf-8'))
    
    def __convert(self, title=u"", artist=u""):
        try:
            os.system(u"ffmpeg -i " + self.filename + u" " + self.out)
        except OSError as e:
            print 'Error converting file!'
            raise e
    
    def clean(self):
        try:
            os.remove(self.filename)
            os.remove(self.out)
        except OSError as e:
            print "Error cleaning!"
            raise e
   
    def process(self):
        self.__createVideo()
        self.__download()
        self.__convert()

