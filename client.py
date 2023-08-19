import requests, hashlib, json

class AntebeotClient():
    # print a debug info
    def pDebug(self, msg):
        if self.dFlag:
            print("DEBUG: " + str(msg) )

    # InitAlize an antebeot client
    def __init__(self, RestApiURL='https://antebeot.world/restapi/', CaptchaPath='/var/www/html/captchas', captchaWebsitePath='byyesxdjlrywth252dcplh46ypyvurpbjudr5koswiu27ywecz3q.b32.i2p/captchas/', defLang = 'ru_RU', debugMode=True):
        self.mUCookiesSessions = {} # user_part : req.cookies, TODO: user_part is very big sometimes. Maybe we would to use hash of them user_part.
        self.RestApiURL = RestApiURL
        self.CaptchaPath = CaptchaPath
        self.captchaWebsitePath = captchaWebsitePath
        self.dFlag = debugMode
        self.defLang = defLang
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
      captcha_req = requests.get(self.RestApiURL + '/captcha?w=get')
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
        r = requests.get('%s/dashboard' % self.RestApiURL)
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
          captcha_answ = requests.get( '%s/captcha?w=answerTest&a=%s' % (self.RestApiURL,answ), cookies={ 'captcha_id': self.mUCookiesSessions[user_part]['captcha_id'] } )
          return (False, json.loads(captcha_answ.content) )
      except Exception as e:
           return (True, "You are not ask captcha before! (#2)" + str(e)) # string indices must be integers, not 'str'

           pass
    # Пример функции для авторизации пользователя
    # code by GPT4. This used template from https://github.com/AntebeotProject/VapsePool/blob/main/HTTPServer/js/functions.js
    def do_auth(self, user_part, username, password, captcha_text):
        if not self.isUSessionExists(user_part, "captcha_id"):
            return "Вы не запросили капчу ранее!"

        # Здесь используется параметр captcha_id из сохраненных данных о пользователе
        data = {
            'workname': username,
            'workpass': password,
            'captchaText': captcha_text,
            'lang': self.defLang,  # Пример языка; вы можете изменить его в соответствии с вашими требованиями
            'otpcode': '',  # Если у вас есть OTP-код, укажите его здесь. # TODO: OTP supports
        }
        response = requests.get(self.RestApiURL + '/signin', 
                                params=data, 
                                cookies={'captcha_id': self.mUCookiesSessions[user_part]['captcha_id']})
        if response.text and response.status_code == 200: 
            try :
             self.mUCookiesSessions[user_part]['usession'] = response.cookies['usession']
            except KeyError as _: pass 
            return response.json()
        else: return {'error': "Ошибка со стороны API {}".format(response.status_code)}

    # Пример функции для регистрации пользователя
    def do_registration(self, user_part, username, password, password2, captcha_text):
        if not self.isUSessionExists(user_part, "captcha_id"):
            return "Вы не запросили капчу ранее!"

        # Здесь используется параметр captcha_id из сохраненных данных о пользователе
        data = {
            'workname': username,
            'workpass': password,
            'workpass2': password2,
            'captchaText': captcha_text,
            'lang': self.defLang,  # Пример языка; вы можете изменить его в соответствии с вашими требованиями
        }
        #print(data)
        response = requests.get(self.RestApiURL + '/registration', params=data, cookies={'captcha_id': self.mUCookiesSessions[user_part]['captcha_id']})
        #
        if response.status_code == 200 and response.text:
         print (response.cookies)
         try :
          self.mUCookiesSessions[user_part]['usession'] = response.cookies['usession']
         except KeyError as _: pass 
         return response.json()
        else:
         return {'error': 'Ошибка на сервере: код состояния {} и пустой текст'.format(response.status_code)}


    # Добавьте другие методы, которые вы хотите использовать
    def wrapperData(w, base_url = '/'):
     base_url = self.RestApiURL + base_url 
     cook = {'usession': self.mUCookiesSessions} if not self.mUCookiesSessions is None else {}
     response = requests.get(base_url, params=w, cookies=cook)
     if response.status_code == 200:
        return response.json()
     else: return {'error': "Ошибка со стороны API {}".format(response.status_code)}
# user API part        
    # GPT was rewrite my code.
    def user_data(w):
     return wrapperData(w, base_url)

    def gen_new_address(cryptocoin):
     return user_data({'w': "genAddress", 'cryptocoin': cryptocoin})

    def update_session():
     return user_data({'w': "updateSession"})

    def change_password(last_pass, new_pass):
     return user_data({'w': "changePassword", 'last_pass': last_pass, 'new_pass': new_pass})

    def get_own_input(cryptocoin):
     return user_data({'w': "getowninput", 'cryptocoin': cryptocoin})

    def user_have_2fa():
     return user_data({"w": "checkOTP"})

    user_have_otp = user_have_2fa

    def get_user_info(w=None):
     if w is None:
        w = {}
     return user_data(w)
# /api/ part
    def api_data(w):
        return wrapperData(w, base_url = '/api/')

    def get_allow_coins():
     return api_data({'w': "getallowcoins"})

    def output_money(login, password, output_address, count_of_money, coin_name, captcha_data, ulang):
     return api_data({
        'w': "output",
        'acc': login,
        'pass': password,
        'oAdr': output_address,
        'cMoney': count_of_money,
        'coinname': coin_name,
        'captchaText': captcha_data,
        'lang': ulang
    })
# /exchange/ part
    def exchange_data(w):
        return wrapperData (w, base_url = '/exchange/')
    def add_order_to_sell_coin2coin(sell_namecoin, buy_namecoin, price, volume_start, volume_max):
     return exchange_data({
        'w': 'addOrderToSellCoin2Coin',
        'toGiveName': sell_namecoin,
        'toGetName': buy_namecoin,
        'Price': price,
        'VolumeStart': volume_start,
        'VolumeMax': volume_max,
    })

    def get_my_done_trade():
        return exchange_data({'w': 'getMyDoneTrade'})
    
    def get_own_orders():
        return exchange_data({'w': 'getOwnOrders'})
    
    def get_reviews_by_about(who):
        return exchange_data({'w': 'getReviewsByAbout', 'who': who})
    
    def get_reviews_by_reviewer(who):
        return exchange_data({'w': 'getReviewsByReviewer', 'who': who})
    
    def get_my_reviews():
        return exchange_data({'w': 'getMyReviews'})
    
    def add_review(id_, text):
        return exchange_data({'w': 'addReview', 'id': id_, 'text': text})
    
    def get_orders(active=True, offset=0, lim=25):
        return exchange_data({'w': 'getOrders', 'a': active, 'offset': offset, 'lim': lim})
    
    def get_order_by_name(who, offset=0, lim=25):
        return exchange_data({'w': 'getOrderByName', 'who': who, 'offset': offset, 'lim': lim})
    
    def get_trader_stats( who ):
        return exchange_data({'w': 'getTraderStats', 'who': who})
    
    def rem_order(id_):
        return exchange_data({'w': 'removeMyOrderByID', 'id': id_})
    
    def change_active_order(id_, s=True):
        return exchange_data( {'w': 'changeActiveOrder', 'id': id_, 's': s} )
    
    def do_trade(id_, count=1):
        return exchange_data({'w': 'doTrade', 'count': count, 'id': id_})
