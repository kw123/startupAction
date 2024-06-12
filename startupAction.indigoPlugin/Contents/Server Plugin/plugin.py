#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# 
# Developed by Karl Wachs
# karlwachs@me.com

import os, sys, subprocess, pwd, time
from checkIndigoPluginName import checkIndigoPluginName 
import logging
import platform

try:
	unicode("x")
except:
	unicode = str

'''
PURPOSE:	execute specific actions at startup of indigo, defined in plugin config , ... 
then do nothing else

'''


################################################################################
class Plugin(indigo.PluginBase):

	########################################
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)

		self.pluginShortName			= "startupAction"
 ###############  common for all plugins ############
		self.getInstallFolderPath		= indigo.server.getInstallFolderPath()+"/"
		self.indigoPath					= indigo.server.getInstallFolderPath()+"/"
		self.indigoRootPath 			= indigo.server.getInstallFolderPath().split("Indigo")[0]
		self.pathToPlugin 				= self.completePath(os.getcwd())

		major, minor, release 			= map(int, indigo.server.version.split("."))
		self.indigoVersion 				= float(major)+float(minor)/10.
		self.indigoRelease 				= release

		self.pluginVersion				= pluginVersion
		self.pluginId					= pluginId
		self.pluginName					= pluginId.split(".")[-1]
		self.myPID						= os.getpid()
		self.pluginState				= "init"

		self.myPID 						= os.getpid()
		self.MACuserName				= pwd.getpwuid(os.getuid())[0]

		self.MAChome					= os.path.expanduser("~")
		self.userIndigoDir				= self.MAChome + "/indigo/"
		self.indigoPreferencesPluginDir = self.getInstallFolderPath+"Preferences/Plugins/"+self.pluginId+"/"
		self.indigoPluginDirOld			= self.userIndigoDir + self.pluginShortName+"/"
		self.PluginLogFile				= indigo.server.getLogsFolderPath(pluginId=self.pluginId) +"/plugin.log"

		formats=	{   logging.THREADDEBUG: "%(asctime)s %(msg)s",
						logging.DEBUG:		"%(asctime)s %(msg)s",
						logging.INFO:		"%(asctime)s %(msg)s",
						logging.WARNING:	"%(asctime)s %(msg)s",
						logging.ERROR:		"%(asctime)s.%(msecs)03d\t%(levelname)-12s\t%(name)s.%(funcName)-25s %(msg)s",
						logging.CRITICAL:	"%(asctime)s.%(msecs)03d\t%(levelname)-12s\t%(name)s.%(funcName)-25s %(msg)s" }

		date_Format = { logging.THREADDEBUG: "%Y-%m-%d %H:%M:%S",		# 5
						logging.DEBUG:		"%Y-%m-%d %H:%M:%S",		# 10
						logging.INFO:		"%Y-%m-%d %H:%M:%S",		# 20
						logging.WARNING:	"%Y-%m-%d %H:%M:%S",		# 30
						logging.ERROR:		"%Y-%m-%d %H:%M:%S",		# 40
						logging.CRITICAL:	"%Y-%m-%d %H:%M:%S" }		# 50
		formatter = LevelFormatter(fmt="%(msg)s", datefmt="%Y-%m-%d %H:%M:%S", level_fmts=formats, level_date=date_Format)

		self.plugin_file_handler.setFormatter(formatter)
		self.indiLOG = logging.getLogger("Plugin")  
		self.indiLOG.setLevel(logging.THREADDEBUG)

		self.indigo_log_handler.setLevel(logging.INFO)

		self.indiLOG.log(20,"initializing  ... ")
		self.indiLOG.log(10,"path To files:          =================")
		self.indiLOG.log(10,"indigo                  {}".format(self.indigoRootPath))
		self.indiLOG.log(10,"installFolder           {}".format(self.indigoPath))
		self.indiLOG.log(10,"plugin.py               {}".format(self.pathToPlugin))
		self.indiLOG.log(10,"indigo                  {}".format(self.indigoRootPath))
		self.indiLOG.log(20,"detailed logging        {}".format(self.PluginLogFile))
		self.indiLOG.log(10,"Plugin short Name       {}".format(self.pluginShortName))
		self.indiLOG.log(10,"my PID                  {}".format(self.myPID))	 
		self.indiLOG.log(10,"Achitecture             {}".format(platform.platform()))	 
		self.indiLOG.log(10,"OS                      {}".format(platform.mac_ver()[0]))	 
		self.indiLOG.log(10,"indigo V                {}".format(indigo.server.version))	 




	########################################
	def __del__(self):
		indigo.PluginBase.__del__(self)
	
	########################################
	def startup(self):


		if not checkIndigoPluginName(self, indigo): 
			exit() 

		self.restart =  False
		self.maxCPUtimeUsed = 10
		self.startUpAction = {}
		self.startUpActionName = {}
		self.startUpActionDelay = {}

		return

####-----------------  set the geneeral config parameters---------
	def getParameters(self, prefs, oldPrefs, init=False):

		restart = False
		self.startUpAction = {}
		self.startUpActionName = {}
		self.startUpActionDelay = {}

		self.maxCPUtimeUsed = int(prefs.get("maxCPUtimeUsed", 10))
		if not init:
			if prefs.get("maxCPUtimeUsed",0) 	!= oldPrefs.get("maxCPUtimeUsed",0): 								restart = True

		for nn in range(1,4):
			try:	self.startUpAction[nn] = int(prefs.get("startUpAction"+str(nn),0))
			except: self.startUpAction[nn] = 0

			self.startUpActionName[nn]  = ""
			if self.startUpAction[nn] > 0: self.startUpActionName[nn] = indigo.actionGroups[self.startUpAction[nn]].name

			try:	self.startUpActionDelay[nn] = int(prefs.get("startUpActionDelay"+str(nn),-1))
			except: self.startUpActionDelay[nn] = -1

			if not init and not restart:
				if prefs.get("startUpAction"+str(nn),0) 		!= oldPrefs.get("startUpAction"+str(nn),0): 		restart = True
				if prefs.get("startUpActionDelay"+str(nn),0) 	!= oldPrefs.get("startUpActionDelay"+str(nn),0): 	restart = True

		

		for nn in range(1,4):
			enabled = True
			if self.startUpActionName[nn] == "": 	enabled = False
			if self.startUpAction[nn] == 0:  		enabled = False
			if self.startUpActionDelay[nn] < 0:  	enabled = False
			self.indiLOG.log(20,'Parameters: Action#:{:1}, Name:"{:}",{:} ID:{:<11}, delay launch by:{:3} secs,  enabled:{}'.format(nn, self.startUpActionName[nn], "".ljust(max(0,25-len(self.startUpActionName[nn]))," ") , self.startUpAction[nn], self.startUpActionDelay[nn], enabled))

		if restart: return True

		return False




####-----------------  set the geneeral config parameters---------
	def validatePrefsConfigUi(self, valuesDict):

		self.restart = self.getParameters(valuesDict, self.pluginPrefs, init=False)

		return True, valuesDict


####-----------------  startup action		   ---------
	def filterActions(self, valuesDict=None, typeId=""):
		xlist = []
		for item in indigo.actionGroups:
			xlist.append((item.id,item.name))
		xlist.append((0,"-none"))
		return xlist

	########################################
	def procUPtime(self,process):

		CPUtime, err = self.readPopen("ps -ef | grep '"+process+"' | grep -v grep | awk '{print $7}'")
		#501   672   655   0 12:04PM ??         1:27.53 /Library/Application Support/Perceptive Automation/Indigo 6/IndigoPluginHost.app/Contents/MacOS/IndigoPluginHost -p1176 -fSQL Logger.indigoPlugin
		if len(CPUtime) < 4 or len(CPUtime) > 10: return -1 # not found
		else:
			temp=CPUtime.strip("\n").split(":")
			try:
				if len(temp) ==3: CPUtime = float(temp[0])*60*60 + float(temp[1])*60 +float(temp[2]) # hours:minutes:seconds.milsecs
				if len(temp) ==2: CPUtime =                        float(temp[0])*60 +float(temp[1]) # minutes:seconds.milsecs
				if len(temp) ==1: CPUtime =                                           float(temp[0]) # seconds:milsecs
			except:
				CPUtime = 0.
			## cputime in seconds.. require 100 seconds cpu consumption to be up long enough
		self.indiLOG.log(20,"{} has used {} secs CPU so far".format(process, CPUtime))
		return CPUtime

####-------------------------------------------------------------------------####
	def readPopen(self, cmd):
		try:
			ret, err = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
			return ret.decode('utf_8'), err.decode('utf_8')
		except Exception as e:
			self.indiLOG.log(40,"{}line#,Module,Statement:{}".format(e, traceback.extract_tb(sys.exc_info()[2])[-1][1:]))



####-----------------  startup action		   ---------
	def checkIfthereAreStartupActions(self):

		cpuUsed = self.procUPtime("/IndigoServer.app")
		if cpuUsed > self.maxCPUtimeUsed:
				self.indiLOG.log(20,"no action to be executed as indigo has been started long time ago, cpu used:{} > {} cutoff".format(cpuUsed, self.maxCPUtimeUsed))
				return 

		startTime = time.time()
		for nn in range(1,4):
			try:	action = int(self.startUpAction[nn])
			except: 
				self.indiLOG.log(20,"action #{}, no action selected to be executed ".format(nn))
				continue
			
			if action == 0: 
				self.indiLOG.log(20,"action #{}, no action selected to be executed ".format(nn))
				continue

			if self.startUpActionDelay[nn] < 0: 
				self.indiLOG.log(20,"action #{}, no action selected to be executed, disabled though delay parameter = off".format(nn))
				continue

			for ii in range(500):
				if time.time() - startTime < self.startUpActionDelay[nn]: self.sleep(1)
		
			indigo.actionGroup.execute(action)
			self.indiLOG.log(20,'launching action: "{}"; id= {}\n'.format(self.startUpActionName[nn], self.startUpAction[nn]))

		return 
####-----------------	  END				   ---------


####-----------------	 ---------
	def completePath(self,inPath):
		if len(inPath) == 0: return ""
		if inPath == " ":	 return ""
		if inPath[-1] !="/": inPath +="/"
		return inPath

####-----------------   main loop, is dummy		   ---------
	def runConcurrentThread(self):

		self.getParameters(self.pluginPrefs, self.pluginPrefs, init=True)
		self.checkIfthereAreStartupActions()
		self.sleep(2)
		self.indiLOG.log(20,"startupAction plugin is finished with its actions")
		self.indiLOG.log(20," To change actions, edit plugin config, it will reload itself if there is any change")
		self.indiLOG.log(20," This plugin will now be idle until restarted")
		self.restart = False

		try:
			while not self.restart:
				self.sleep(2)

			if self.restart: 
				self.indiLOG.log(30,"restart of plugin due to change in parameters, ignore following error message")
				exit()

		except: pass
		return
####-----------------  valiable formatter for differnt log levels ---------
# call with: 
# formatter = LevelFormatter(fmt='<default log format>', level_fmts={logging.INFO: '<format string for info>'})
# handler.setFormatter(formatter)
class LevelFormatter(logging.Formatter):
	def __init__(self, fmt=None, datefmt=None, level_fmts={}, level_date={}):
		self._level_formatters = {}
		self._level_date_format = {}
		for level, format in level_fmts.items():
			# Could optionally support level names too
			self._level_formatters[level] = logging.Formatter(fmt=format, datefmt=level_date[level])
		# self._fmt will be the default format
		super(LevelFormatter, self).__init__(fmt=fmt, datefmt=datefmt)
		return

	def format(self, record):
		if record.levelno in self._level_formatters:
			return self._level_formatters[record.levelno].format(record)

		return super(LevelFormatter, self).format(record)


