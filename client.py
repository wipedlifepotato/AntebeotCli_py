import requests, hashlib, json

class AntebeotClient():
    # print a debug info
    def pDebug(self, msg):
        if self.dFlag:
            print("DEBUG: " + str(msg) )

    # InitAlize an antebeot client
    def __init__(self, RestApiURL='https://antebeot.world/', CaptchaPath='/var/www/html/captchas', captchaWebsitePath='byyesxdjlrywth252dcplh46ypyvurpbjudr5koswiu27ywecz3q.b32.i2p/captchas/', debugMode=True):
        self.mUCookiesSessions = {} # user_part : req.cookies, TODO: user_part is very big sometimes. Maybe we would to use hash of them user_part.
        self.RestApiURL = RestApiURL
        self.CaptchaPath = CaptchaPath
        self.captchaWebsitePath = captchaWebsitePath
        self.dFlag = debugMode
        pass
    # Check if user session thing is exists.
    def isUSessionExists(self, user_part, what):
     try:
      if self.mUCookiesSessions[user_part] is None or  self.mUCookiesSessions[user_part][what] is None: return False
      return True
     except Exception:
      return False
    # return fname,captcha_id


    # get a captcha
    def getCaptcha(self, user_part):
      captcha_req = requests.get(self.RestApiURL + '/restapi/captcha?w=get')
      cData = captcha_req.content
      if not captcha_req.cookies['captcha_id'] is None:

       # drop files in the dir though cron/...
       # TODO: instead collision add user part to captchaFileName

       captchaFileName = hashlib.md5( bytes(captcha_req.cookies['captcha_id'], "UTF-8") ).hexdigest()[2:8]
       captchaFPath = "%s/%s.png" % (self.CaptchaPath, captchaFileName)
       self.pDebug(captchaFPath)
       with open( captchaFPath , "wb" ) as f:
        f.write(cData)
        f.close()
        #await irc.wMsg(to, "path to your file: %s/%s.png" % (self.captchaWebsitePath ,captchaFileName))

        try:
            if self.mUCookiesSessions[user_part] is None: self.mUCookiesSessions[user_part] = {}   #captcha_req.cookies # add cookies. not rewrite it! todo:!
        except Exception as e:  self.mUCookiesSessions[user_part] = {}

        self.mUCookiesSessions[user_part]['captcha_id'] = captcha_req.cookies['captcha_id']

        self.pDebug("uCookieSession now is")
        self.pDebug(self.mUCookiesSessions[user_part])
        return (captchaFileName, self.mUCookiesSessions[user_part])
    # return a dashboard info from a deprecated long pool server (TODO: poolserver)
    def getDashboard(self):
        r = requests.get('%s/restapi/dashboard' % self.RestApiURL)
        decoded = r.content.decode("utf-8")
        return decoded

    # return values - err, answ
    def checkCaptcha(self, user_part, answ):
      self.pDebug("uCookieSession now is (#2)")
      self.pDebug(self.mUCookiesSessions[user_part])
      try:
          if self.mUCookiesSessions[user_part] is None or  self.mUCookiesSessions[user_part]['captcha_id'] is None:
           #await irc.wMsg(to, "You are not ask captcha before! (#1)")
           return (True, "you are not ask captcha before! (#1)")
          self.pDebug(answ)
          captcha_answ = requests.get( '%s/restapi/captcha?w=answerTest&a=%s' % (self.RestApiURL,answ), cookies={ 'captcha_id': self.mUCookiesSessions[user_part]['captcha_id'] } )
          return (False, json.loads(captcha_answ.content) )
      except Exception as e:
           return (True, "You are not ask captcha before! (#2)" + str(e)) # string indices must be integers, not 'str'

           pass
