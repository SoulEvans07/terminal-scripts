import time
import re
from protocol import LogMixin


def ver():
    return '1.0'


class Lw3List(list):

    @property
    def first(self):
        val = None
        try:
            val = self[0]["value"]
        except Exception:
            pass
        return val


class LW3(LogMixin):
    instanceCntr = 0

    def __init__(self, commif, user="root", password="admin", useCredentials=False, name='', description=''):

        self.comm = 0
        self.responses = []
        self.bracket = False
        self.indata = ""
        self.block = []
        self.signature = ""
        self.chg = ""
        self._baseSignature = (LW3.instanceCntr % 0xF) << 12
        self.outsignature = self._baseSignature
        LW3.instanceCntr += 1
        self.printstdout = 0

        self.openednodes = set()
        self.openedNodeCallbacks = {}
        self.propertycache = {}
        self.REPLY_TIMEOUT = 2

        self.comm = commif

        self.log_init(name, description)

        if useCredentials:
            n = 0
            while (n < 6):
                self.process(commif.receive())
                if (len(self.responses) == 0):
                    pass
                elif (len(self.responses[-1]['data'][0]) == 0):
                    pass
                elif (self.responses[-1]['data'][0] == 'LOGIN SUCCESSFUL'):
                    self.log_normal("Lw3: Logined")
                    return
                elif (self.responses[-1]['data'][0] == 'login:'):
                    self.send(user)
                elif (self.responses[-1]['data'][0] == 'password:'):
                    self.send(password)
                n = n + 1
                self.responses = []
            self.log_fail("Lw3: Login failed")
        return

    def process(self, string):
        for c in string:
            if ((c == '\r') or (c == '\n')):
                if (len(self.indata) == 0):
                    continue

                if (self.printstdout == 1):
                    txt = '{} << {}'.format(
                        time.strftime('%H:%M:%S'), self.indata)
                    print(txt)

                self.log_in(self.indata)

                if (self.bracket):
                    if (self.indata[0] == '}'):
                        self.bracket = False
                        self.responses.append(
                            {'signature': self.signature, 'data': self.block})
                        self.block = []
                    else:
                        self.block.append(self.indata)
                else:
                    if (self.indata[0] == '{'):
                        self.bracket = True
                        self.signature = self.indata[1:]
                    else:
                        self.responses.append(
                            {'signature': "", 'data': [self.indata]})
                        if (self.indata[0:3] == "CHG"):
                            self.processChg(self.indata[4:])
                self.indata = ""
            else:
                self.indata = self.indata + c

    def send(self, string, signaturereq=False):
        ret = 0
        if (signaturereq):
            ret = "%0.4X" % self.outsignature
            string = ret + "#" + string
            self.outsignature = self.outsignature + 1
            if self.outsignature > self._baseSignature | 0x0FFF:
                self.outsignature = self._baseSignature
        if (self.printstdout == 1):
            txt = '{} >> {}'.format(time.strftime('%H:%M:%S'), string)
            print(txt)
        self.comm.send(string + '\r\n')
        self.log_out(string)
        return ret

    def processChg(self, msg):
        msg = msg.split("=")
        chgOrigin = msg[0].split('.')[0]
        for openedNode in self.openednodes:
            if openedNode == chgOrigin:
                self.propertycache[msg[0]] = msg[1]
                if (self.openedNodeCallbacks[chgOrigin] != False):
                    self.openedNodeCallbacks[chgOrigin](msg[0], msg[1])
            elif openedNode.endswith("*"):
                wildcardNode = openedNode.rsplit('/', 1)[0]
                chgOrigin = openedNode.rsplit('/', 1)[0]
                if wildcardNode == '':
                    wildcardNode = '/'
                if chgOrigin == '':
                    chgOrigin = '/'
                if chgOrigin == wildcardNode:
                    if self.openedNodeCallbacks[wildcardNode + '/*'] != False:
                        self.openedNodeCallbacks[
                            wildcardNode + '/*'](msg[0], msg[1])
            if '*' not in self.chg:
                if self.chg == msg[0]:
                    self.chg = ""
            else:
                chg = self.chg.split('.')
                x = msg[0].split('.')
                prop = x[1]
                node = x[0].rsplit('/', 1)[0]
                if node == '':
                    node = '/'
                if prop == chg[1] and node == chg[0][:-2]:
                    self.chg = ""

    def sendAndWaitResponse(self, string):
        self.responses = []
        sig = self.send(string, True)
        starttime = time.time()
        while True:
            self.process(self.comm.receive())
            for r in self.responses:
                if (r['signature'] == sig):
                    return r['data']
            diff = time.time() - starttime
            if (diff) > self.REPLY_TIMEOUT:
                self.log_fail("%s: No response to %s" %
                              (time.strftime('%H:%M:%S'), sig))
                return ""

    def getErrorMsg(self, msg):
        try:
            if msg[1] != 'E':
                return ['', 0]
            if msg.find('%') != -1:
                p = msg.split('%')
                p = p[1].split(':')
                return [p[1], int(p[0][1:4])]
            errorNames = {'n': 'Node', 'p': 'Property',
                          'm': 'Method', 'o': 'Open', 'c': 'Close'}
            type_ = msg[0]
            if type_ in errorNames.keys():
                return ['%s error' % errorNames[type_], -1]
            else:
                return ['Unknown error type', -1]
        except:
            return ['Unknown error type', -1]

    def unescape(self, s):
        s = s.replace("\\\\", "\\")
        s = s.replace("\\(", "(")
        s = s.replace("\\)", ")")
        s = s.replace("\\}", "}")
        s = s.replace("\\{", "{")
        s = s.replace("\\#", "#")
        s = s.replace("\\r", "\r")
        s = s.replace("\\n", "\n")
        s = s.replace("\\t", "\t")
        s = s.replace("\\%", "%")
        return s

    def GET(self, node, prop, skipcache=False, manual=False, methodmanual=False):
        # check cache first
        if (skipcache is False) and (manual is False):
            if node + '.' + prop in self.propertycache:
                ret = [{'name': prop, 'value': self.propertycache[
                    node + '.' + prop], 'error':'', 'errorcode':0}]
                return ret

        # continue else
        if (manual is False):
            resp = self.sendAndWaitResponse("GET " + node + "." + prop)
        else:
            if methodmanual:
                resp = self.sendAndWaitResponse("MAN " + node + ":" + prop)
            else:
                resp = self.sendAndWaitResponse("MAN " + node + "." + prop)
        ret = Lw3List([])
        for r in resp:
            [error, errorcode] = self.getErrorMsg(r)
            if (errorcode != 0):
                r = r.split("%")[0]

            # Property or method
            if (r[0] == "p"):
                typeProperty = True
            else:
                typeProperty = False

            # Read only
            if (r[1] == "r"):
                readOnly = True
            else:
                readOnly = False

            if r[0] == "n":
                isNode = True
            else:
                isNode = False

            if manual or isNode:
                parts = ['', '']
                tmp = r.split(" ")
                parts[0] = ' '.join(tmp[:2])
                parts[1] = ' '.join(tmp[2:])
            else:
                parts = r.split("=")

            if (len(parts) == 1):
                parts.append("")
            if (parts[0].find(".") != -1):
                parts2 = parts[0].split(".")
                ret.append({'name': parts2[1], 'value': self.unescape(parts[1]), 'error': error,
                            'errorcode': errorcode, 'property': typeProperty, 'readonly': readOnly})
                if (node in self.openednodes):
                    self.propertycache[node + '.' + parts2[1]] = parts[1]
            elif (parts[0].find(":") != -1):
                parts2 = parts[0].split(":")
                ret.append({'name': ':'.join(parts2[1:]), 'value': self.unescape(parts[1]), 'error': error,
                            'errorcode': errorcode, 'property': typeProperty, 'readonly': readOnly})
            # TODO: Terrible hack, to get error messages raised by nodes.
            elif errorcode != 0:
                # I think the whole function needs some care. Someday I'll do
                # it. But if you feel the power, I'll won't complain...
                ret.append({'name': ':'.join(parts[1:]), 'value': None, 'error': error,
                            'errorcode': errorcode, 'property': typeProperty, 'readonly': readOnly})
            else:
                continue
        return ret

    def MAN(self, node, prop, skipcache=False):
        return self.GET(node, prop, skipcache, True)

    def MANMethod(self, node, prop, skipcache=False):
        return self.GET(node, prop, skipcache, True, True)

    def GETChilds(self, node):
        resp = self.sendAndWaitResponse("GET " + node)
        ret = []
        for r in resp:
            if (r[0:2] != "n-") and (r[0:2] != "ns"):
                continue
            parts = r.split(node, 1)
            if (len(parts[1]) > 0):
                if (parts[1][0] == '/'):
                    parts[1] = parts[1][1:]
                ret.append(parts[1])
        return ret

    def OPEN(self, node, callback=False):
        node = self.unifyNodeEnding(node)
        resp = self.sendAndWaitResponse("OPEN " + node)
        if resp:
            [error, errorcode] = self.getErrorMsg(resp[0])
            if (errorcode == 0):
                self.openednodes.add(node)
                self.openedNodeCallbacks[node] = callback
        else:
            error = "No response to OPEN on node %s" % node
            errorcode = -1
        return {'error': error, 'errorcode': errorcode}

    def CLOSE(self, node):
        node = self.unifyNodeEnding(node)
        resp = self.sendAndWaitResponse("CLOSE " + node)
        if resp:
            [error, errorcode] = self.getErrorMsg(resp[0])
            if (errorcode == 0):
                self.openednodes.discard(node)
                keysToRemove = []
                for key in self.propertycache.keys():
                    if key.split('.')[0] == node:
                        keysToRemove.append(key)
                for key in keysToRemove:
                    del self.propertycache[key]
                if node in self.openedNodeCallbacks:
                    del self.openedNodeCallbacks[node]
        else:
            error = "No response to CLOSE on node %s" % node
            errorcode = -1
        return {'error': error, 'errorcode': errorcode}

    def SET(self, node, prop, value):
        resp = self.sendAndWaitResponse(
            "SET " + node + "." + prop + "=" + value)
        ret = Lw3List([])
        for r in resp:
            [error, errorcode] = self.getErrorMsg(r)
            if (errorcode != 0):
                r = r.split("%")[0]
            parts = r.split("=")
            if (len(parts) == 1):
                parts.append("")
            if (parts[0].find(".") != -1):
                parts2 = parts[0].split(".")
                if (node in self.openednodes):
                    self.propertycache[node + '.' + parts2[1]] = parts[1]
                ret.append(
                    {'name': parts2[1], 'value': parts[1], 'error': error, 'errorcode': errorcode})
            else:
                ret.append(
                    {'name': prop, 'value': '', 'error': error, 'errorcode': errorcode})
                continue
        return ret

    def CALL(self, node, method, params=""):
        resp = self.sendAndWaitResponse(
            "CALL " + node + ":" + method + "(" + params + ")")
        ret = Lw3List([])
        for r in resp:
            [error, errorcode] = self.getErrorMsg(r)
            if (errorcode != 0):
                r = r.split("%")[0]
            parts = r.split("=")
            if (len(parts) == 1):
                parts.append("")
            if (parts[0].find(":") != -1):
                parts2 = parts[0].split(":")
                ret.append(
                    {'name': parts2[1], 'value': parts[1], 'error': error, 'errorcode': errorcode})
            else:
                continue
        return ret

    def BACKUP(self, node):
        tmp = self.REPLY_TIMEOUT
        self.REPLY_TIMEOUT = 10
        resp = self.sendAndWaitResponse('BACKUP ' + node + '*')
        self.REPLY_TIMEOUT = tmp
        return resp

    def waitCHG(self, node, prop, timeout=1):
        node = self.unifyNodeEnding(node)
        self.chg = node + '.' + prop
        stoptime = time.time() + timeout
        while (1):
            remaintime = stoptime - time.time()
            if (remaintime < 0):
                self.log_fail("No CHG to " + self.chg)
                self.chg = ""
                return ""
            self.process(self.comm.receive(remaintime))
            if self.chg == "":
                if node.endswith('*'):
                    return 'OK'
                path = node + '.' + prop
                if path in self.propertycache:
                    return self.propertycache[path]
                else:
                    return self.GET(node, prop, skipcache=True)[0]['value']
        return ""

    def printCache(self):
        print(self.propertycache)

    def uploadEdidFromFile(self, path, edidLoc):
        """ upload EDID from a .dat file
            usage: eg. uploadEdidFromFile('c:\Edid.dat', 'U1')
        """

        EdidStr = ''

        # Process .dat file
        if path.find('.dat') != (-1):
            f = open(path, 'r')
            EdidLines = f.readlines()
            f.close()

            Edid = []
            for line in EdidLines:
                if line.find('|') == -1:
                    continue
                line = line[line.find("|") + 1:]
                m = re.findall(r'([0-9A-F]{2})', line)
                Edid.extend(m)

            for data in Edid:
                EdidStr = EdidStr + data

        # process bin file
        elif path.find('.bin') != (-1):
            with open(path, 'rb') as f:
                while True:
                    byte = f.read(1)
                    if not byte:
                        break
                    EdidStr += '%.2x' % ord(byte)

        else:
            print('Edid file type upload not supported: %s' % path)
            return (-1)

        # Edid upload method changed.
        # Data became read only, but left here for compatibility reason.
        self.CALL('/EDID/%s/%s' % (edidLoc[0], edidLoc), 'setData', EdidStr)
        self.SET('/EDID/%s/%s' % (edidLoc[0], edidLoc), 'Data', EdidStr)
        if self.GET('/EDID/%s/%s' % (edidLoc[0], edidLoc), 'Data')[0].get('value') != EdidStr:
            return (-1)
        return 0

    def unifyNodeEnding(self, node):
        node = node.strip()
        if node.count("/") > 1 and node.endswith('/'):
            node = node[:-1]
        return node

    def GETValue(self, node, prop, skipcache=False):
        return self.GET(node, prop, skipcache, False)[0]['value']

    def GETBoolValue(self, node, prop, skipcache=False):
        resp = self.GET(node, prop, skipcache, False)[0]['value']
        if resp == 'true':
            result = True
        elif resp == 'false':
            result = False
        else:
            raise Exception('The ' + prop + ' of ' + node + prop +
                            "node can't convert to boolean. Response: " + resp)
        return result
