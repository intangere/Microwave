class exts():
    def __init__(self, *args):
        self.name = 'exts'
        self.command = 'exts'
        self.description = 'List loaded extensions'
        self.parent = args[0][0]
        self.args = args[0][1]
    def run(self):
        self.parent.sendLine(self.parent.buildNotice('300', self.parent.nick, 'Currently loaded extensions:'))
        self.parent.sendLine(self.parent.buildNotice('300', self.parent.nick, str(self.parent.extensions.keys())))


