import telnetlib
import socket


class CasparServer:
    # CasparServer sorts out all of the network-related stuff that's involved in interfacing with CasparCG.
    # This initiates the socket connection, holds the IP and port data, and suchlike.
    # The idea is that the CasparServer represents a connection to a given Caspar server.
    # The user should instantiate a CasparServer to connect to Caspar, then when a CasperTalker/Listener
    # needs to communicate with a Caspar server, that CasparServer instance is passed to it.
    #
    # Ex:
    # my_caspar_server = CasparServer()
    # my_caspar_server.connect("192.168.1.50", 5250)
    # ctalk = CasparTalker()
    # ctalk.cg_info(my_casper_server) # Or whatever, etc...

    def __init__(self, server_ip=None, port=5250):
        self.server_ip = self.server_port = None
        self.buffer_size = 4096
        #self.telnet = telnetlib.Telnet()

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if server_ip: self.connect(server_ip, port)

    def connect(self, server_ip="localhost", port=5250):
        self.server_ip = server_ip
        self.server_port = port
        self.socket.connect((self.server_ip, self.server_port))
        #self.telnet.open(self.server_ip, self.server_port)

    def disconnect(self):
        #self.telnet.close()
        self.socket.close()

    def send_command(self, amcp_command):
        #self.telnet.write(amcp_command)
        self.socket.sendall(amcp_command)

        #print self.socket.recv(self.buffer_size)

    def read_until(self, delimiter):
        s = ""
        while not s.endswith(delimiter):
            s += self.socket.recv(1)

        return s.splitlines()
