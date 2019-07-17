modes = {
            'p' : 'Private channel',
            'o' : 'Operator user mode',
            'q' : 'Channel Founder',
            'a' : 'Protected',
            'v' : 'Voice',
            'h' : 'Halfop'
        }

class MODE():
    def __init__(self, *args):
	self.name = 'MODE'
	self.command = 'MODE'
	self.description = 'Handle MODE Packet'
	self.args = args[0]
	self.parent = args[0][0]
    def run(self):
	packet = self.args[1]
        params = packet[1].split(' ')
	print(packet, params)
        if ' ' in params:
            params = packet[1].split(' ')
        if len(params) > 2:
            chan = [params[0], params[2]]
            mode = params[1]
            op = mode[:-1]
            if modes.has_key(mode.replace('+','').replace('-','')):
                self.parent.changeChanMode(chan, op, mode)
        else:
            #mode = params[1]
            #op = mode[:-1]
            #chan = params[0]
            #if modes.has_key(mode.replace('+','').replace('-','')):
            #    self.parent.changeChanMode(chan, op, mode)
            print 'Unimplemented'

