# Notifier

Notifier is a Python messaging gateway, that can be used as a Python module or standalone CLI script. Messages can be sent to either SMTP email server or the notification service [PushOver](https://pushover.net/)


## Installation 

Download and unpack [notifier.py](notifier.py) to the `/usr/local/bin` folder and copy [etc/notifier.conf](etc/notifier.conf) to the `/etc/` directory

## Configuration

Edit the [/etc/notifier.conf](etc/notifier.conf) file and add your SMTP Email and notification service settings.

## Command Line Use

You can send a message to both email and push notification via the CLI by using the following format

`python notifier.py -s Subject -m Message to send`

## Python Module

To use within Python simple place [notifier.py](notifier.py) within your project and use the following code example

```python
# Notifier
import notifier

# Config
import ConfigParser

# Use your own application based config file
config_file = '/etc/myApp.conf'

# Create your message
message = "This is the message I wish to send \n"

# Set the Config
notifier.setConfig(config)

# Set the Message
notifier.setMessage(message) 

# Send the Message to email and notification service
notifier.sendMessage()
```
