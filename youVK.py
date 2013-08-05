import vkontakte
import vk_auth
import requests
import argparse

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
    parser.add_argument('-e', '--email', help = "User email", required = True)
    parser.add_argument('-p', '--password', help = "Password", required =  True)
    parser.add_argument("-f", "--file", help = "File to upload", required = True)
    return  parser.parse_args()

def main(args):
    try:
        vk = authorize(args.email, args.password)
    except RuntimeError:
        print "Authorization error!"
        return
    try:
        save(vk, parseOutput(uploadAudio(getUploadURL(vk), args.file)))
    except IOError:
        print "File not found!"
    except Exception:
        print "Eror uploading file!"
    print "Done. File " + args.file + " was sent to server!"

if __name__ == "__main__" :
    args = parseArgs()
    main(args)


