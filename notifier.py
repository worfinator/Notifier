#!/usr/bin/python

# Notifier
# by Mark Baldwin
#
# Python script to create a message gateway
# using JSON objects to send either an email 
# or push notification. Can be used as a module 
# or a CLI script.

import ConfigParser, sys, getopt, logging, smtplib, datetime, pycurl, json, os.path
from StringIO import StringIO

# Config file
config_file = '/etc/notifier.conf'
config = False

# Current date time stamp
myDateTime = datetime.datetime.now()


def getConfig(config_file):
    # lets get the config
    config = ConfigParser.ConfigParser()

    # loadconfig file if it exists
    if os.path.exists(config_file):
        config.read(config_file)
        return config
    else:
        print "Error: "+ config_file + " file not found"
        sys.exit()

def sendEmail( emailObj ):

  msg = 'Sending Email'
  print(msg)
  logging.debug(msg)

  # try send the email
  try:
    header = 'To:' + emailObj['receiver'] + '\n' + 'From: ' + emailObj['sender'] + '\n' + 'Subject:' + emailObj['subject'] + '\n'
    emailObj['message'] = header + '\n' + emailObj['date'] + '\n\n' + emailObj['message']

    # Build SMPT object
    smtpObj = smtplib.SMTP(emailObj['server'])
    smtpObj.starttls()
     # use login and password if required
    if len(emailObj['login']) and len(emailObj['password']):
      smtpObj.login(emailObj['login'], emailObj['password'])
    smtpObj.sendmail(emailObj['sender'], emailObj['receiver'], emailObj['message'])
    smtpObj.quit()

    msg = 'Successfully sent Email \n' + emailObj['message']
    print msg
    logging.info(msg)
    return

  # Show error
  except smtplib.SMTPException as error:
    msg = 'Error: unable to send Email \n' + error
    print msg
    logging.warning(msg)
    return

def sendPushNotification( pushObj ):
    print "Sending Push Notification"
    
    # use StringIO to capture the response from our push API call
    reponse = StringIO()

    # use Curl to post to the Instapush API
    request = pycurl.Curl()

    # set Instapush API URL
    request.setopt(request.URL, 'https://api.instapush.im/v1/post')

    # setup custom headers for authentication variables and content type
    request.setopt(request.HTTPHEADER, ['x-instapush-appid: ' + pushObj['appID'],
    'x-instapush-appsecret: ' + pushObj['appSecret'],
    'Content-Type: application/json'])

    # create a dictionary structure for the JSON data to post to Instapush
    json_fields = {}

    # setup JSON values
    json_fields['event']=pushObj['event']
    json_fields['trackers'] = {}
    json_fields['trackers']['message']=pushObj['message']

    postfields = json.dumps(json_fields)

    # make sure to send the JSON with post
    request.setopt(request.POSTFIELDS, postfields)

    # set this so we can capture the resposne in our reponse
    request.setopt(request.WRITEFUNCTION, reponse.write)

    # log the post
    logging.info(request.setopt(request.VERBOSE, True))

    # send the request
    request.perform()

    # capture the response from the server
    body = reponse.getvalue()

    # log the response
    logging.info(body)

    # reset the reponse
    reponse.truncate(0)
    reponse.seek(0)

    # cleanup
    request.close()

def getArgs(argv, emailObj):
  try:
    opts, args = getopt.getopt(argv, "ms", ["message=","subject="])
  except getopt.GetoptError:
    print 'Error: no arguments passed'

  # get the options
  for opt, arg in opts:
    if opt in ("-m", "--message"):
      emailObj['message'] = arg
      print arg
    if opt in ("-s", "--subject"):
      emailObj['subject'] = arg 
  print opts
  return emailObj

def sendMessage():
  # check if we need to send an email
  if config.get('notifier','email'):
    sendEmail( emailObj )

  # check if we need to send an instapush
  if config.get('notifier','instapush'):
    sendPushNotification( pushObj )

def setConfig(newConfig):
  config = newConfig

def setMessage(message):
  emailObj['message']=message
  pushObj['message']=message

def setEvent(event):
  pushObj['event']=event

def setSubject(subject):
  emailObj['subject']=subject

def getConfig(config_file):
    # lets get the config
    config = ConfigParser.ConfigParser()

    # loadconfig file if it exists
    if os.path.exists(config_file):
        config.read(config_file)
        return config
    else:
        print "Error: "+ config_file + " file not found"
        sys.exit()

# load the config if not passed in
if not config:
  config = getConfig(config_file)

# Email settings
emailObj = { 'date': myDateTime.strftime('%d/%m/%y - %H:%M:%S'), 'server': config.get('email','server'), 'sender': config.get('email','sender'), 'receiver': config.get('email','receiver'), 'login': config.get('email','login'), 'password': config.get('email','password'), 'message': config.get('email','message'), 'subject': config.get('email','subject') }

# InstaPush settings
pushObj = { 'appID': config.get('instapush','app_id'), 'appSecret': config.get('instapush','app_secret'), 'event': config.get('instapush','event'), 'message': config.get('instapush','message')}

# Enable Logging
logging.basicConfig(filename=config.get('notifier','log_file'), level=logging.DEBUG)

# If executed as a script
if __name__ == '__main__':
  emailObj = getArgs( sys.argv[1:], emailObj )
  sendMessage()
