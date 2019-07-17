import json
class test():
	def __init__(self, *args):
		self.parent = args[0][0]
		self.args = args[0][1]
		self.name = "test"
		self.command = "test"
		self.description = "test"
	def run(self):
		self.parent.sendLine(self.parent.buildNotice('300', self.parent.nick, 'Test command has been run using /test'))
