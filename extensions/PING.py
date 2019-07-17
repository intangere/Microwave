class PING():
    def __init__(self, *args):
	self.name = 'PING'
	self.command = 'PING'
	self.description = 'Handle PING packet'
	self.args = args[0]
	self.parent = args[0][0]
    def run(self):
        packet = self.args[1]
        self.parent.sendLine(self.parent.buildPacket(['PONG', packet[1]])) #packet[1] is the hashkey

