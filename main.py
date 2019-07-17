from twisted.internet.protocol import Factory
from twisted.internet.task import LoopingCall
from twisted.protocols.basic import LineReceiver
from twisted.internet import reactor
from config import *
import json
import os
import time

packets = {
    'NICK' : {
            'nick' : 1,
            },
    'USER' : {
            'username' : 0,
            'servername' : 1,
            'hostname' : 2,
            'realname' : 3,
            },
    'PRIVMSG' : {
            'dest' : 1,
            'msg' : 1,
            },
    'PING' : {
            'hashkey' : 1
            },
    'QUIT' : {
            'reason' : 1
            },
    'MODE' : {
            'mode' : 1
            },
    'TOPIC' : {
            'chan' : 1,
            'topic' : 2
            }

    }

class Chat(LineReceiver):


    def __init__(self, users, channels):
        self.users = users
        self.channels = channels
        self.joined_channels = []
        self.extensions = {}
        self.loadPlugins(extension_folder)
        self.buildExtList()
        self.pongTime = 0

    def connectionMade(self):
        self.state = "unauthenticated"
        self.connected = False
        self.lc = LoopingCall(self.ping)
        self.lc.start(60)
        print "Ping template started"

    def connectionLost(self, reason):
        print reason
        try:
            if self.nick in self.users:
                for channel in self.joined_channels:
                    self.channels[channel]['users'].remove(self.nick)
                    for user in self.channels[channel]['users']:
                        if user != self.nick:
                            self.users[user].sendLine(self.buildPacket([':%s!%s@%s' % (self.nick, self.username, self.hostname), 'QUIT : Connection closed']))
                self.transport.loseConnection()
                del self.users[self.nick]
        except Exception as e:
            pass
        self.transport.loseConnection()
        self.lc.stop()
        if self.nick in self.users.keys():
            del self.users[self.nick]
    def log(self, info, msg):
        print "[%s]: %s" % (info, msg)

    def lineReceived(self, line):
        line = line.replace('\r\n', '') 
        self.packetHandler(line)

    def ping(self):
        now = time.time()
        print now
        print self.pongTime
        if self.pongTime != 0 and now - self.pongTime > 61:
            print "Ping timed out"
            self.transport.loseConnection()
            print "Lost connection"
        else:
           print "Trying ping"
           self.sendLine('PING anon.ircd')
           print "Sent ping"
           self.pingTime = time.time()

    def packetHandler(self, message):
        packet = message
        if ' ' in packet:
            packet = message.split(' ', 1)
        else:
            packet = [packet, None]
        typ = packet[0]
        self.log("%s" % typ, str(packet[1]))
        if packet[0] == "JOIN":
            if packet[1].startswith('#') and packet[1].count('#') == 1:
                if packet[1] not in self.joined_channels:
                    channel = packet[1].lower()
                    if channel not in self.channels:
                        self.createChannel(channel)
                    else:
                        self.channels[channel]['users'].append(self.nick)
                        for user in self.channels[channel]['users']:
                            self.users[user].sendLine(self.buildPacket([':%s!%s@%s' % (self.nick, self.username, self.hostname), 'JOIN', channel]))
                        self.sendLine(self.buildNotice('332', '%s %s' % (self.nick, channel), self.channels[channel]['topic']))
                    self.sendLine(self.buildUserList(channel))
                    self.sendLine(self.buildNotice('366', '%s %s' % (self.nick, channel), 'End of /NAMES list.'))
                    self.joined_channels.append(channel)
        elif packet[0] == "PART":
            channel = packet[1].lower()
            if ' ' in channel:
                channel = channel.split(' ')[0]
            if channel in self.joined_channels:
                for user in self.channels[channel]['users']:
                    self.users[user].sendLine(self.buildPacket([':%s!%s@%s' % (self.nick, self.username, self.hostname), 'PART', channel]))
                self.channels[channel]['users'].remove(self.nick)
                self.joined_channels.remove(channel)
        elif packet[0] == "PRIVMSG":
            print packet[1]
            dest, message = packet[1].split(' ', 1) 
            if '#' in dest:
                if dest in self.joined_channels:
                    for user in self.channels[dest]['users']:
                        if user != self.nick:
                            self.users[user].sendLine(self.buildPacket([':%s!%s@%s' % (self.nick, self.username, self.hostname), 'PRIVMSG %s %s' % (dest, message)]))
            else:
                if dest in self.users.keys():
                    self.users[dest].sendLine(self.buildPacket([':%s!%s@%s' % (self.nick, self.username, self.hostname), 'PRIVMSG %s %s' % (dest, message)]))
        elif packet[0] == "TOPIC":
            topic = packet[1].split(' :', 1)[1]
            chan = packet[1].split(' :', 1)[0]
            if chan in self.joined_channels:
                for user in self.channels[chan]['users']:
                    self.users[user].sendLine(self.buildNotice('332',  '%s %s' % (self.nick, chan), topic))
                self.channels[chan]['topic'] = topic
        elif packet[0] == "LIST":
            self.sendLine(self.buildNotice('321', self.nick, ''))
            for channel in self.channels.keys():
                if self.channels[channel]['priv'] != True:
                    self.sendLine(self.buildNotice('322', self.nick, '%s %s :%s' % (channel, len(self.channels[channel]['users']), self.channels[channel]['topic'])))
                else:
                    self.sendLine(self.buildNotice('322', self.nick, '* * :*'))
            self.sendLine(self.buildNotice('323', self.nick, '/LIST: End of channel list'))
        elif packet[0] == "PONG":
            self.pongTime = time.time()
        #elif packet[0] == "DUMP":
        #        self.dumpMicrowave()
        else:
            if packet[0] in self.extensions:
                msg = self.extensions[packet[0]]([self, packet]).run()
            #self.close()
            pass

    def handleUserPacket(self, packet, info):
        for part in packets["USER"].keys():
            print part, info[packets["USER"][part]]
            setattr(self, part, info[packets["USER"][part]])
            self.realname = packet[1].split(':', 1)[1]
            self.hostname = 'microwave.user'

    def buildNotice(self, opcode, nick, msg):
        self.log('NOTICE SENT', ':%s %s %s :%s' % (server_host, opcode, nick, msg))
        return ':%s %s %s :%s' % (server_host, opcode, nick, msg)

    def buildNoticeNoColon(self, opcode, nick, msg):
        self.log('NOTICE SENT', ':%s %s %s %s' % (server_host, opcode, nick, msg))
        return ':%s %s %s :%s' % (server_host, opcode, nick, msg)

    def buildModePacket(self, mode):
        self.sendLine(':%s MODE %s :%s' % (self.nick, self.nick, mode))

    def buildMotd(self):
        f = open('motd', 'r')
        motd = f.readlines()
        self.sendLine(self.buildNoticeNoColon('005', self.nick, 'WALLCHOPS WATCH=128 WATCHOPTS=A SILENCE=15 MODES=12 CHANTYPES=# PREFIX=(qaohv)~&@%+ CHANMODES=beI,kfL,lj,psmntirRcOAQKVCuzNSMTGZ NETWORK=Microwave CASEMAPPING=ascii EXTBAN=~,qjncrRa ELIST=MNUCT STATUSMSG=~&@%+ :are supported by this server'))
        for line in motd:
            self.sendLine(self.buildNotice('372', self.nick, line.strip()))
        self.sendLine(self.buildNotice('372', self.nick, 'END of /MOTD command'))
        self.connected = True

    def buildUserList(self, channel):
        return self.buildNotice('353', '%s = %s' % (self.nick, channel), ' '.join(user for user in self.channels[channel]['users']))

    def buildPacket(self, params):
        packet = ' '.join(param for param in params)
        self.log('SENT', packet)
        return '%s' % packet

    def createChannel(self, channel):
        self.channels[channel] = {
                                     'topic': 'Channel %s has been created by %s' % (channel, self.nick),
                                     'users': [self.nick],
                                     'priv' : False,
                                     'owner': None,
                                     'modes' : None
                                 }
        self.sendLine(self.buildPacket([':%s!%s@%s' % (self.nick, self.username, self.hostname), 'JOIN', channel]))
        self.sendLine(self.buildNotice('332',  '%s %s' % (self.nick, channel), self.channels[channel]['topic']))

    def changeChanMode(self, chan, op, mode):
        mode = mode.replace(op, '')
        if len(chan) > 1:
            user_ = chan[1]
            chan = chan[0]
            for user in self.channels[chan]['users']:
                self.users[user].sendLine(self.buildPacket([':%s!%s@%s MODE %s' % (self.nick, self.username, self.hostname, chan), '%s%s %s' % (op, mode, user_)]))
        else:
            print("CHANNNNNNNNNNNNNNNN %s" % chan)
            if mode == 'p':
                print op
                if op == '+':
                    self.channels[chan]['priv'] = True
                else:
                    self.channels[chan]['priv'] = False
                for user in self.channels[chan]['users']:
                    self.users[user].sendLine(self.buildPacket([':%s!%s@%s MODE %s' % (self.nick, self.username, self.hostname, chan), '%s%s' % (op, mode)]))

    def loadPlugins(self, folder):
        self.plugins_folder = folder
        res = {}
        lst = os.listdir(folder)
        dir = []
        if "__init__.py" in lst:
                for d in [p for p in lst if p.endswith(".py")]:
                        dir.append(d[:-3])
        for d in dir:
                if d != "__init__":
                        res[d] = __import__(folder + "." + d, fromlist = ["*"])
        self.plugins = res
        return res

    def buildExtList(self):
        for name in self.plugins:
            command = "%s" %  name
            self.extensions[command] = self.getClassByName(self.plugins[name], "%s.%s.%s" % (extension_folder, name, name))
        print self.extensions

    def getClassByName(self, module, className):
        if not module:
                if className.startswith(".%s" % extension_folder):
                        className = className.split(".%s" % extension_folder)[1]
                l = className.split(".")
                m = __services__[l[0]]
                return getClassByName(m, ".".join(l[1:]))
        elif "." in className:
                l = className.split(".")
                m = getattr(module, l[2])
                return m
        else:
                return getattr(module, className)

class ChatFactory(Factory):
    def __init__(self):
        self.users = {} #Store users
        self.channels = {} #Store channels

    def buildProtocol(self, addr):
        return Chat(self.users, self.channels)

reactor.listenTCP(server_port, ChatFactory())
reactor.run()
