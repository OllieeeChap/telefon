import os
from os.path import exists
import queue
import threading
import pygame		# use for audio
import signal
import sys, time
import RPi.GPIO as GPIO

from threading import Timer
from modules.RotaryDial import RotaryDial
from modules.Ringtone import Ringtone

callback_queue = queue.Queue()

class TelephoneDaemon:
	# Number to be dialed
	dial_number = ""

	# On/off hook state
	offHook = False

	# Off hook timeout
	offHookTimeoutTimer = None

	RotaryDial = None
	Ringtone = None
	SipClient = None
	WebServer = None

	config = None

	# Allow the audio to play even if ON HOOK appear after a bounce 
	playBounceHook = False

	def __init__(self):
		print ("[STARTUP]")

		signal.signal(signal.SIGINT, self.OnSignal)

		pygame.mixer.init(buffer=1024)			# init mixer for audio

		#Ring tone
		self.Ringtone = Ringtone()

		# Rotary dial
		self.RotaryDial = RotaryDial()
		self.RotaryDial.RegisterCallback(NumberCallback = self.GotDigit, OffHookCallback = self.OffHook, OnHookCallback = self.OnHook, OnVerifyHook = self.OnVerifyHook)

		input("Waiting.\n")

	def OnHook(self):
		print ("[PHONE] On hook")
		self.offHook = False
		# Reset current number when on hook
		self.dial_number = ""
		if not self.playBounceHook:
			pygame.mixer.music.stop()
			pygame.mixer.music.unload()

	def OffHook(self):
		print ("[PHONE] Off hook")
		self.offHook = True
		# Reset current number when off hook
		self.dial_number = ""
		self.Ringtone.unring()
		time.sleep(0.8)
		isPlaying = pygame.mixer.music.get_busy()
		
		if not self.playBounceHook and not isPlaying:
			pygame.mixer.music.load('audio/numeroter.wav')
			pygame.mixer.music.play()
		elif not isPlaying:
			pygame.mixer.music.play()
			pygame.mixer.music.queue('audio/occupe.wav')
			self.playBounceHook = False

	def OnVerifyHook(self, state):
		if not state:
			self.offHook = False

	def OnOffHookTimeout(self):
		print ("[OFFHOOK TIMEOUT]")

	def GotDigit(self, digit):
		print ("[DIGIT] Got digit: %s" % digit)
		#self.Ringtone.stophandset()
		self.dial_number += str(digit)
		print ("[NUMBER] We have: %s" % self.dial_number)

		# Shutdown command, since our filesystem isn't read only (yet?)
		# This hopefully prevents dataloss.
		# TODO: stop rebooting..
		if self.dial_number == "0666":
			#self.Ringtone.playfile(self.config["soundfiles"]["shutdown"])
			os.system("halt")

		if self.dial_number == "1312":
			if self.offHook == False:
				print ("EXPLOSION")
				self.loadAudio("audio/explosion.mp3")
				self.playBounceHook = True
				self.dial_number = ""
				self.Ringtone.ring()

		if self.dial_number != "131":
			if len(self.dial_number) == 3:
				if self.offHook == False:
					print ("[PHONE] Dialing number: %s" % self.dial_number)
					self.createPath(self.dial_number)
					self.playBounceHook = True
					self.dial_number = ""
					self.Ringtone.ring()

	def createPath(self, numberStr):
		filePath = "audio/" + numberStr + ".mp3"
		if exists(filePath):
			print("File exists !")
			self.loadAudio(filePath)
		else:
			print("Use default file...")
			self.loadAudio("audio/default.mp3")

	def loadAudio(self, path):
		pygame.mixer.music.load(path)

	def OnSignal(self, signal, frame):
		print ("[SIGNAL] Shutting down on %s" % signal)
		GPIO.cleanup()
		self.RotaryDial.StopVerifyHook()
		sys.exit(0)

def main():
	TDaemon = TelephoneDaemon()

if __name__ == "__main__":
	main()
