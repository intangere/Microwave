import json
class dump():
	def __init__(self, *args):
		self.parent = args[0][0]
		self.args = args[0][1]
		self.name = "dump"
		self.command = "dump"
		self.description = "Dump the current IRCD structure to the console"
	def run(self):
        	print "---Users---"
	        print json.dumps(self.parent.users, sort_keys=False, indent=4, default=str)
        	print "---Channels---"
        	print json.dumps(self.parent.channels, sort_keys=False, indent=4)
