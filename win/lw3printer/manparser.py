import re
import random


class ManParser:

    """ Backus-Naur formula parser for LW3 protocol. This class tries to parse the manual string and generates the possible values. If too many different possible values are present,
        it generates only a few and set a flag (self.covered) to false. """

    def __init__(self):
        self.covered = True
        self.unknownExpression = False
        self.expressions = {
            'text':         ['abc', '', 'QWERTY', 'impossible length string maybe causes buffer overflow somewhere if the software is not carefully designed', '-1', '0', '+'],
            'name':         ['abc', '', 'QWERTY', 'impossible length string maybe causes buffer overflow somewhere if the software is not carefully designed', '-1', '0', '+'],
            'entry':        ['abc', '', 'QWERTY', 'impossible length string maybe causes buffer overflow somewhere if the software is not carefully designed', '-1', '0', '+'],
            'label':        ['abc', '', 'QWERTY', 'impossible length string maybe causes buffer overflow somewhere if the software is not carefully designed', '-1', '0', '+'],
            'layer_id':     range(0, 6),
            'number':       range(-1, 4),
            # obsoleted, but some erroneous manual uses it
            'bool':         ['true', 'false'],
            '2_hex_octet':  ['00', 'AA', 'FF'],
            '2_octet_hex':  ['00', 'AA', 'FF'],
            'ip_address':   ['192.168.0.1', '192.168.2.11', '255.255.255.0'],
            'port_id': ['P' + str(i) for i in range(1, 6)],
            'pin_id': ['P' + str(i) for i in range(1, 6)],
            'edid_id': ['E1', 'E100', 'E0', 'D1', 'D100', 'D0', 'F1', 'F100', 'F0', 'U1', 'U0', 'U100'],
        }

    def addExpression(self, expression, values):
        """ Adds a new expression - possible values pair to the list. Eg. addExpression('port', ['P1','P2','P3']) """
        self.expressions[expression] = values

    def _estimateExpression(self, txt):
        """ Private function, for give some estimate for available values for a given expression """
        self.covered = False
        for expr, values in self.expressions.items():
            if (txt.find(expr) != -1):
                return values
        self.unknownExpression = True
        return ['0', '1', '2']

    def _closingBracket(self, text, ch='()'):
        """ Internal helper function: it helps the position of the closing bracket.
            Example: _closingBracket('(a(a)a)a(a)') = 6 """
        if (len(text) == 0):
            return -1
        if text[0] != ch[0]:
            return -1
        bracket = 0
        slen = 0
        for i in text:
            if i == ch[0]:
                bracket = bracket + 1
            if i == ch[1]:
                bracket = bracket - 1
            if bracket == 0:
                break
            slen = slen + 1
        return slen

    def _buildVariations(self, n, txt):
        """ Recursive helper function for building repetitive combinations """
        for v in self.subvalues:
            tmp = txt + str(v)
            if n == 1:
                self.ret.append(tmp)
            else:
                self._buildVariations(n - 1, str(tmp))

    def _parseManual(self, manual, pre=""):
        """ Private function for manual parsing """
        bracket1 = 0
        bracket2 = 0
        bracket3 = 0
        quote = False
        manual = manual.strip()
        manual = manual.replace("| ", "|")
        manual = manual.replace(" |", "|")
        manual = manual.replace(">\"", "> \"")
        manual = manual.replace("\"<", "\" <")
        # print(pre+"Parsed manual: -"+str(manual)+"-")
        if (len(manual) < 1):
            return []

        """ is it a number? """
        if manual.isdigit():
            try:
                n = int(manual)
                return [str(n)]
            except ValueError:
                pass

        """ is it a string literal? """
        if (manual[0] == "\"") and (manual[-1] == "\"") and (manual[1:-1].find("\"") == -1):
            return [manual[1:-1]]

        """ is it an expression in brackets? Eg. (something)? """
        if (manual[0] == "(") and (manual[-1] == ")"):
            if self._closingBracket(manual, '()') == len(manual) - 1:
                return self._parseManual(manual[1:-1], pre + " ")

        """ is it an expression in curly brackets? Eg. {something}? """
        if (manual[0] == "{") and (manual[-1] == "}"):
            if self._closingBracket(manual, '{}') == len(manual) - 1:
                return self._parseManual(manual[1:-1], pre + " ")

        """ is it an optional element? """
        if (manual[0] == "[") and (manual[-1] == "]"):
            if self._closingBracket(manual, '[]') == len(manual) - 1:
                ret = self._parseManual(manual[1:-1], pre + " ")
                ret.append('')
                return ret

        """ is it an expresson? """
        if (manual[0] == "<") and (manual[-1] == ">"):
            self.covered = False
            return self._estimateExpression(manual[1:-1])

        """ is it a multiplication? Like <repetitions>*{<expressions>} """
        regex = re.search('^([0-9]+)\*\{([\x00-\x7F]*)\}$', manual)  # todo:  "1*{something} 2*{thing}"  - this may be lead to a match now.
        if (regex is not None):
            ret = []
            self.subvalues = self._parseManual(regex.group(2), pre + " ")
            if len(self.subvalues) == 0:
                return []
            variations = len(self.subvalues) ** int(regex.group(1))
            if (variations < 33):
                # variation number is not too high, we have to generate all
                # combinations
                self.ret = []
                self._buildVariations(int(regex.group(1)), '')
                return self.ret
            else:
                # too many variations, we will get only 32 random choice
                self.covered = False
                for i in range(1, 32):
                    tmp = ""
                    for j in range(0, int(regex.group(1))):
                        tmp = tmp + random.choice(self.subvalues)
                    ret.append(tmp)
                return ret

        """ is it an optional repetition? Like *[something]"""

        # todo:  "*[something] [thing]"  - this may be lead to a match now.
        regex = re.search('^\*\[([\x00-\x7F]*)\]$', manual)
        if (regex is not None):
            self.covered = False
            ret = ['']
            self.subvalues = self._parseManual(regex.group(1), pre + " ")
            if len(self.subvalues) == 0:
                return ret
            if len(self.subvalues) ** 3 > 17:
                self.covered = False
                for i in range(1, 4):
                    for k in range(0, 2):
                        tmp = ""
                        for j in range(0, i):
                            tmp = tmp + random.choice(self.subvalues)
                        ret.append(tmp)
                return ret
            else:
                self.ret = ['']
                for i in range(1, 3):
                    self._buildVariations(i, '')
                return self.ret

        """ is it an optional repetition with minimum occurency number? Like 2*[something]"""

        # todo:  "2*[something] [thing]"  - this may be lead to a match now.
        regex = re.search('^([0-9]+)\*\[([\x00-\x7F]*)\]$', manual)
        if (regex != None):
            self.covered = False
            ret = []
            self.subvalues = self._parseManual(regex.group(2), pre + " ")
            if len(self.subvalues) == 0:
                return ret
            minval = int(regex.group(1))
            if len(self.subvalues) ** (minval + 3) > 17:
                self.covered = False
                for i in range(minval, minval + 3):
                    for k in range(0, 2):
                        tmp = ""
                        for j in range(0, i):
                            tmp = tmp + str(random.choice(self.subvalues))
                        ret.append(tmp)
                return ret
            else:
                self.ret = ['']
                for i in range(minval, minval + 3):
                    self._buildVariations(i, '')
                return self.ret

        # is it an OR-ed connection or concatenation?
        slen = 0
        for ch in manual:
            slen = slen + 1
            if ch == "[":
                bracket1 = bracket1 + 1
            if ch == "]":
                bracket1 = bracket1 - 1
            if ch == "{":
                bracket2 = bracket2 + 1
            if ch == "}":
                bracket2 = bracket2 - 1
            if ch == "(":
                bracket3 = bracket3 + 1
            if ch == ")":
                bracket3 = bracket3 - 1
            if ch == "\"":
                quote = not quote
            if (bracket1 == 0) and (bracket2 == 0) and (bracket3 == 0) and (not quote):
                if ch == "|":
                    return self._parseManual(manual[:slen - 1], pre + " ") + self._parseManual(manual[slen:], pre + " ")
                if ch == " ":
                    set1 = self._parseManual(manual[:slen - 1], pre + " ")
                    set2 = self._parseManual(manual[slen:], pre + " ")
                    ret = []
                    for a in set1:
                        for b in set2:
                            ret.append(str(a) + str(b))
                        if (len(ret) > 10):
                            self.covered = False                            
                            return ret
                    return ret

        """Ahh.. give up, whatever is it"""
        self.covered = False
        return []

    def parseManual(self, manual):
        """ Generates the possible values based on the given manual.
            Example:        parseManual('[2*{("true" | "false") ";" ] two boolean value')
            Will return     {'covered': True, 'values': ['true;true;','true;false;','false;true;','false;false;']  """
        self.covered = True
        self.unknownExpression = False
        slen = self._closingBracket(manual, '[]')
        manual = manual[1:slen]
        ret = self._parseManual(manual)
        self.values = ret
        return {'covered': self.covered, 'values': ret}
