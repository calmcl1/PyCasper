import socket

from twisted.lore.tree import _LocalEntityResolver


class CasparServer:
    """
    .. py:class CasparTalker

    :param str server_ip: The IP address of the CasparCG server that we want to communicate with.
    :param int port: The port that the CasparCG server at *server_ip* is listening for AMCP commands on.

    Represents a Caspar Server instance.

    CasparServer sorts out all of the network-related stuff that's involved in interfacing with CasparCG.
    This initiates the socket connection, holds the IP and port data, and suchlike.
    The idea is that the CasparServer represents a connection to a given Caspar server.
    The user should instantiate a CasparServer to connect to Caspar, then when a CasperTalker/Listener
    needs to communicate with a Caspar server, that CasparServer instance is passed to it.

    Only the CasparServer should deal with socket operations, nobody else.

    Ex:

        >>> my_caspar_server = CasparServer("192.168.1.50", 5250)
        >>> ctalk = CasparTalker()
        >>> ctalk.cg_info(my_casper_server) # Or whatever, etc...

    """
    #

    def __init__(self, server_ip=None, port=5250):
        # Set up a connection a socket to connect with
        self.server_ip = self.server_port = None
        self.buffer_size = 4096
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if server_ip: self.connect(server_ip, port)

        # Set the paths relevant to the server
        self.paths = {"media": "",
                      "log": "",
                      "data": "",
                      "template": "",
                      "thumbnails": "",
                      "initial": ""}

        # Set the list of templates available
        self.templates = []

    def connect(self, server_ip="localhost", port=5250):
        """
        .. py:method connect([server [,port ]])
        
        :param server_ip:
        :param port:
        :return:
        """
        self.server_ip = server_ip
        self.server_port = port
        self.socket.connect((self.server_ip, self.server_port))

    def disconnect(self):
        self.socket.close()

    def send_command(self, amcp_command):
        self.socket.sendall(amcp_command)

    def read_until(self, delimiter):
        s = ""
        while not s.endswith(delimiter):
            s += self.socket.recv(1)

        lines = s.splitlines()
        ret = []

        # Sometimes Caspar spits out some extraneous empty lines, which can throw us.
        # Let's get rid of them.

        for l in lines:
            if len(l): ret.append(l)

        return ret
