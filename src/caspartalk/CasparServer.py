import telnetlib


class CasparServer:
    # CasparServer sorts out all of the network-related stuff that's involved in interfacing with CasparCG.
    # This initiates the Telnet connection, holds the IP and port data, and suchlike.
    # The idea is that the CasparServer represents a connection to a given Caspar server.
    # The user should instantiate a CasparServer to connect to Caspar, then when a CasperTalker/Listener
    # needs to communicate with a Caspar server, that CasparServer instance is passed to it.
    #
    # Ex:
    # my_caspar_server = CasparServer()
    # my_caspar_server.connect("192.168.1.50", 5250)
    # ctalk = CasparTalker()
    # ctalk.cg_info(my_casper_server) # Or whatever, etc...

    def __init__(self):
        self.server_ip = self.server_port = None
        self.telnet = telnetlib.Telnet()

    def connect(self, server_ip="localhost", port=5250):
        self.server_ip = server_ip
        self.server_port = port
        self.telnet.open(self.server_ip, self.server_port)

    def send_command(self, amcp_command):
        self.telnet.write(amcp_command)