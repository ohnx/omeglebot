from pyomegle import OmegleClient
import socket
import re
 
network = 'irc.freenode.net'
hasConvo = False
port = 6667

irc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
irc.connect((network, port))
print irc.recv(4096)
irc.send('NICK ohnxomegle\r\n')
irc.send("USER ohmegle ohmegle ohmegle :ohnx's omegle bot\r\n")
irc.send('JOIN ##ohnx\r\n')

def sendmsg(chan, msg):
    irc.send('PRIVMSG %s :%s\r\n' % (chan, msg))

def sendme(chan, msg):
    irc.send('PRIVMSG %s :\001ACTION %s\001\r\n' % (chan, msg))

class OmegleHandler(object):
    """ Abstract class for defining Omegle event handlers """

    RECAPTCHA_CHALLENGE_URL = 'http://www.google.com/recaptcha/api/challenge?k=%s'
    RECAPTCHA_IMAGE_URL = 'http://www.google.com/recaptcha/api/image?c=%s'
    # recaptcha_challenge_regex = re.compile(r"challenge\s*:\s*'(.+)'")

    def __init__(self, loop=False):
        self.loop = loop
    
    def _setup(self, omegle):
        """ Called by the Omegle class for initial additional settings """
        self.omegle = omegle
    
    def waiting(self):
        """ Called when we are waiting for a stranger to connect """
        sendme('##ohnx', 'Looking for someone you can chat with...')

    def connected(self):
        """ Called when we are connected with a stranger """
        sendme('##ohnx', 'You\'re now chatting with a random stranger. Hope they\'re not a bot!')
        global hasConvo
        hasConvo = True

    def typing(self):
        """ Called when the user is typing a message """
        sendme('##ohnx', 'Stranger is typing...')

    def stopped_typing(self):
        """ Called when the user stop typing a message """
        sendme('##ohnx', 'Stranger has stopped typing.')
    
    def message(self, message):
        """ Called when a message is received from the connected stranger """
        sendmsg('##ohnx', message)

    def common_likes(self, likes):
        """ Called when you and stranger likes the same thing """
        sendme('##ohnx', 'You both like %s.' % ', '.join(likes))
        global hasConvo
        hasConvo = True

    def disconnected(self):
        """ Called when a stranger disconnects """
        sendme('##ohnx', 'Stranger has disconnected. Type !new to start a new session.')
        global hasConvo
        hasConvo = False

    def captcha_required(self):
        """ Called when the server asks for captcha """
        url = RECAPTCHA_CHALLENGE_URL % challenge
        source = self.browser.open(url).read()
        challenge = recaptcha_challenge_regex.search(source).groups()[0]
        url = RECAPTCHA_IMAGE_URL % challenge

        sendme('##ohnx', 'Fuck... need captcha lol %s' % url)
        print ('Recaptcha required: %s' % url)
        # response = raw_input('Response: ')

        # self.omegle.recaptcha(challenge, response)

    def captcha_rejected(self):
        """ Called when server reject captcha """
        pass

    def server_message(self, message):
        """ Called when the server report a message """
        # print (message)

    def status_info(self, status):
        """ Status info received from server """
        pass

    def ident_digest(self, digests):
        """ Identity digest received from server """
        pass

h = OmegleHandler(loop=False)           # session loop
c = OmegleClient(h, wpm=47, lang='en', topics=['ohnxxx'])  # 47 words per minute
c.start()

lulz = ''

while True:
   data = irc.recv(4096)
   if data.find('PING') != -1:
      irc.send('PONG ' + data.split() [ 1 ] + '\r\n')
   if data.find('!new') != -1 and hasConvo == False:
      sendme('##ohnx', 'Starting new conversation...')
      c.next()
      hasConvo = True
   if data.find('!end') != -1 and hasConvo == True:
      sendme('##ohnx', 'Disconnected!')
      hasConvo = False
      c.disconnect()
   if data.find('KICK') != -1:
      irc.send('JOIN ##ohnx\r\n')
   if data.find('PRIVMSG') != -1:
      lulz = data.split(':', 3)
      sender = lulz[1]
      msg = lulz[2]
      
      if msg.find('< ') != -1:
          c.send(msg[2:-1])
      if sender.find('@unaffiliated/ohnx') != -1 and msg.find('ohnxomegle quit now!') != -1:
          sendmsg('##ohnx', 'I thought you loved me! D:')
          irc.send('QUIT\r\n')
          c.disconnect()
          break

   print data


