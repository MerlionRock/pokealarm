#Setup Logging
import logging
log = logging.getLogger(__name__)

#Python modules

#Local modules
from ..alarm import Alarm
from ..utils import *

#External modules
from twilio.rest import TwilioRestClient

class Twilio_Alarm(Alarm):

	_defaults = {
		'pokemon':{
			#'from_number': Required
			#'to_number': Required
			'message': "A wild <pkmn> has appeared! <gmaps> Available until <24h_time> (<time_left>).",
		},
		'pokestop':{
			#'from_number': Required
			#'to_number': Required
			'message': "Someone has placed a lure on a Pokestop! <gmaps> Lure will expire at <24h_time> (<time_left>).",
		}
	}
	
	#Gather settings and create alarm
	def __init__(self, settings):
		#Service Info
		self.account_sid = settings['account_sid']
		self.auth_token = settings['auth_token']
		
		self.from_number = settings.get('from_number')
		self.to_number = settings.get('to_number')
		self.startup_message = settings.get('startup_message', "True")
		
		#Set Alerts
		self.pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
		self.pokestop = self.set_alert(settings.get('pokestop', {}), self._defaults['pokestop'])
		#Connect and send startup message
		self.connect()
		if parse_boolean(self.startup_message):
		    self.send_sms(
				to_num=self.pokemon['to_number'],
				from_num=self.pokemon['from_number'],
				msg="PokeAlarm has been activated! We will text this number about pokemon.")
		log.info("Twilio Alarm intialized.")
		
	#(Re)establishes Telegram connection
	def connect(self):
		self.client = TwilioRestClient(self.account_sid, self.auth_token) 
		
	#Set the appropriate settings for each alert
	def set_alert(self, settings, default):
		alert = {}
		alert['to_number'] = settings.get('to_number', self.to_number)
		alert['from_number'] = settings.get('from_number', self.from_number)
		
		alert['message'] = settings.get('message', default['message'])
		
		return alert
	
	#Send Pokemon Info
	def send_alert(self, alert, info):
		args = { 
			'to_num':alert['to_number'],
			'from_num':alert['from_number'],
			'msg':replace(alert['message'], info)
		}
		try_sending(log, self.connect, "Twilio", self.send_sms, args)
		
	#Trigger an alert based on Pokemon info
	def pokemon_alert(self, pokemon_info):
		self.send_alert(self.pokemon, pokemon_info)
		
	#Trigger an alert based on Pokestop info
	def pokestop_alert(self, pokestop_info):
		self.send_alert(self.pokestop, pokestop_info)
		
	#Send message through Twilio
	def send_sms(self, to_num, from_num, msg):
		message = self.client.messages.create(body=msg, to=to_num, from_=from_num)