from config import server_name

class NICK():
    def __init__(self, *args):
	self.parent = args[0][0]
	self.name = 'NICK'
	self.command = 'NICK'
	self.description = 'Handle NICK Packet'
	self.args = args[0]
    def run(self):
	packet = self.args[1]
        if self.parent.connected == True:
            if not self.parent.users.has_key(packet[1]):
                self.parent.sendLine(self.parent.buildPacket([':%s!%s@%s' % (self.parent.nick, self.parent.username, self.parent.hostname), 'NICK :%s' % packet[1]]))
                for chan in self.parent.joined_channels:
                    for user in self.parent.channels[chan]['users']:
                        self.parent.users[user].sendLine(self.parent.buildPacket([':%s!%s@%s' % (self.parent.nick, self.parent.username, self.parent.hostname), 'NICK :%s' % packet[1]]))
                    self.parent.channels[chan]['users'].append(packet[1])
                    self.parent.channels[chan]['users'].remove(self.parent.nick)
                del self.parent.users[self.parent.nick]
                self.parent.nick = packet[1]
                self.parent.users[packet[1]] = self.parent
        elif not self.parent.users.has_key(packet[1]):
            self.parent.nick = packet[1]
            self.parent.users[self.parent.nick] = self.parent
            if hasattr(self.parent, 'realname') and self.parent.connected == False:
                self.parent.sendLine(self.parent.buildNotice('001', self.parent.nick, 'Welcome to %s' % server_name))
                self.parent.buildMotd()
        else:
            self.parent.sendLine(self.parent.buildNoticeNoColon('433', '*', packet[1]))

