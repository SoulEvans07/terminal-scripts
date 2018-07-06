import sys


class LogMixin():
    def log_init(self, name, description):
        self.logenable = False
        self.name = name
        self.description = description

        if 'pyna.log' in sys.modules:
            self.logenable = True
            self.send_proto_info()

    def send_proto_info(self):

        protoname = self.__class__.__name__

        # Check if running from pyte, because the connection will be different.
        # if no pyte, then get mediuminfo from the communication class.
        try:
            m, mp, d = sys.modules['pyna.pyte']._remoteControl.GetConnectionInfo(self.name)
        except:
            m = mp = d = None

        medium = self.comm.conn_type if m is None else m
        medium_prop = self.comm.get_conn_info() if mp is None else mp
        self.description = self.description if d is None else d

        self.log_conn_id = sys.modules['pyna.log'].addConnection(self.name, medium,
                                                                 medium_prop=medium_prop,
                                                                 protoname=protoname,
                                                                 description=self.description)

    def log_in(self, data):
        if self.logenable:
            sys.modules['pyna.log'].logCommunication(self.log_conn_id, 'In', data)

    def log_out(self, data):
        if self.logenable:
            sys.modules['pyna.log'].logCommunication(self.log_conn_id, 'Out', data)

    def log_normal(self, message):
        if self.logenable:
            sys.modules['pyna.log'].log(message)

    def log_warning(self, message):
        if self.logenable:
            sys.modules['pyna.log'].warning(message)

    def log_fail(self, message):
        if self.logenable:
            sys.modules['pyna.log'].fail(message)
