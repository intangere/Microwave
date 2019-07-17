from config import *

class reload_exts():
    def __init__(self, *args):
	self.name = 'reload_exts'
	self.command = 'reload_exts'
	self.description = 'Reload/load IRCD Extensions' 
	self.parent = args[0][0]
	self.args = args[0][1]
    def run(self):
	self.parent.loadPlugins(extension_folder)
	self.parent.buildExtList()
	self.parent.sendLine(self.parent.buildNotice('300', self.parent.nick, 'Reloaded extensions'))

