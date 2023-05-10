"""
MC Phone Art project

This file is the main daemon for the project. There's still some bug due to the cheap relay we used. I tried to manage those GPIO
interferences by adding delay, debouncing and sleep but some weird issues can still occurs. That's why a restart procedure is implemented 
by simply dial 0 on the phone.

This project is based on hnseland project. See readme file for more.
"""

"""
	Import packages
"""
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

	# Dial, hook and ring objects
	RotaryDial = None
	Ringtone = None

	# Allow the audio to play even if ON HOOK appear after a bounce 
	playBounceHook = False

	def __init__(self):
		print ("[STARTUP]")

		signal.signal(signal.SIGINT, self.OnSignal)		 	# Clean exit when CTRL-C

		pygame.mixer.init(buffer=1024)						# init mixer for audio

		#Ring tone init
		self.Ringtone = Ringtone()

		# Ring at startup
		for i in range(5):
			self.Ringtone.ring()
			time.sleep(0.2)
			self.Ringtone.unring()
			time.sleep(0.2)

		# Rotary dial
		self.RotaryDial = RotaryDial()
		self.RotaryDial.RegisterCallback(NumberCallback = self.GotDigit, OffHookCallback = self.OffHook, OnHookCallback = self.OnHook, OnVerifyHook = self.OnVerifyHook)
		
		input("Waiting.\n")

	def OnHook(self):
		"""
			This function is executed whenever the user take the phone in his hands
		"""
		print ("[PHONE] On hook")
		self.offHook = False

		# Reset current number when on hook
		self.dial_number = ""

		# Only execute when an audio is playing --> Stop and unload song from memory
		if not self.playBounceHook:	
			pygame.mixer.music.stop()
			pygame.mixer.music.unload()

	def OffHook(self):
		"""
			This function is executed whenever the phone is on its base
		"""
		print ("[PHONE] Off hook")
		self.offHook = True
		# Reset current number when off hook
		self.dial_number = ""

		# Stop ringtone
		self.Ringtone.unring()
		time.sleep(0.8)

		# Ask if something is playing
		isPlaying = pygame.mixer.music.get_busy()
		
		# Only execute if the user didn't dial
		if not self.playBounceHook and not isPlaying:
			pygame.mixer.music.load('audio/numeroter.wav')
			pygame.mixer.music.play()

		# Execute if the user dial at least 3 number
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
		"""
			This function is called whenever the user dial a number. It calls audio, easter egg or restart function.
		"""
		# Print received digit and number in memory
		print ("[DIGIT] Got digit: %s" % digit)
		self.dial_number += str(digit)
		print ("[NUMBER] We have: %s" % self.dial_number)

		# Reboot sequence if somethin happens
		# just dial 0
		if self.dial_number == "0":
			GPIO.cleanup()
			os.execv(sys.executable, ['python'] + sys.argv)

		# Easter egg hihihihihi MOUAHAHAHAHAHAH
		if self.dial_number == "1312":
			if self.offHook == False:
				print ("EXPLOSION")
				self.loadAudio("audio/explosion.mp3")
				self.playBounceHook = True
				self.dial_number = ""
				self.Ringtone.ring()

		# Check if not an easter egg, and then stops when user dialed 3 number. Will check if file exists or not, and then load the correct file (or default) in pygame mixer
		if self.dial_number != "131":
			if len(self.dial_number) == 3:
				if self.offHook == False:
					print ("[PHONE] Dialing number: %s" % self.dial_number)
					self.createPath(self.dial_number)
					self.playBounceHook = True
					self.dial_number = ""
					self.Ringtone.ring()

	def createPath(self, numberStr):
		"""
			This function creates correct path and load file in mixer
		"""
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
		"""
			On user shutdown CTRL-C
		"""
		print ("[SIGNAL] Shutting down on %s" % signal)
		GPIO.cleanup()
		self.RotaryDial.StopVerifyHook()
		sys.exit(0)

def main():
	TDaemon = TelephoneDaemon()

if __name__ == "__main__":
	main()
