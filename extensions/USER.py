from config import server_name

class USER():
    def __init__(self, *args):
	self.args = args[0]
	self.name = 'USER'
	self.command = 'USER'
	self.description = 'Handle USER Packet'
	self.parent = args[0][0]
    def run(self):
	packet = self.args[1]
        info = packet[1].split(' ')
	print info
        self.parent.handleUserPacket(packet, info)
        if hasattr(self.parent, 'nick') and self.parent.connected == False:
            self.parent.sendLine(self.parent.buildNotice('001', self.parent.nick, 'Welcome to %s' % server_name))
            self.parent.buildMotd()

