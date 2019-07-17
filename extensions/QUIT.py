class QUIT():
    def __init__(self, *args):
	self.name = 'QUIT'
	self.command = 'QUIT'
	self.description = 'Handle QUIT Packet'
	self.parent = args[0][0]
	self.args = args[0]
    def run(self):
        for channel in self.parent.joined_channels:
            for user in self.parent.channels[channel]['users']:
                if user != self.parent.nick:
                    self.parent.users[user].sendLine(self.parent.buildPacket([':%s!%s@%s' % (self.parent.nick, self.parent.username, self.parent.hostname), 'QUIT : Connection closed']))
                    try:
                        self.parent.channels[channel]['users'].remove(self.parent.nick)
	#    del(self.parent.users[self.parent.nick])
	            except Exception as e:
	                pass
        #        self.parent.transport.loseConnection()


