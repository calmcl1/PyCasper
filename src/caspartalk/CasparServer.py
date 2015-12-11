import socket

from twisted.lore.tree import _LocalEntityResolver


class CasparServer:
    """
    .. py:class:: CasparTalker(server_ip, [port])

    :param str server_ip: The IP address of the CasparCG server that we want to communicate with (optional).
    :param int port: The port that the CasparCG server at *server_ip* is listening for AMCP commands on (optional).

    Represents a Caspar Server instance.

    CasparServer sorts out all of the network-related stuff that's involved in interfacing with CasparCG.
    This initiates the socket connection, holds the IP and port data, and suchlike.
    The idea is that the CasparServer represents a connection to a given Caspar server.
    The user should instantiate a CasparServer to connect to Caspar, then when a CasperTalker
    needs to communicate with a Caspar server, that CasparServer instance is passed to it.

    Only the CasparServer should deal with socket operations, nobody else.

    Example:

        >>> my_caspar_server = CasparServer("192.168.1.50", 5250)
        >>> ctalk = CasparTalker()
        >>> ctalk.cg_info(my_casper_server) # Or whatever, etc...

    If the *server_ip* parameter is given, the method will also call :py:meth:`~caspartalk.CasparServer.connect`, also \
    using the *port* if provided.

    """

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
        .. py:method:: caspartalk.CasparServer.connect(server, [port=5250])

        This will open and connect to a TCP socket in order to communicate with a CasparCG server, using the provided \
        IP or hostname and port.

        :param server_ip: The IP or hostname of the CasparCG server that you're connecting to (Optional).
        :param port: The port of the CasparCG server at the IP or hostname *server_ip*.

        """
        self.server_ip = server_ip
        self.server_port = port
        self.socket.connect((self.server_ip, self.server_port))

    def disconnect(self):
        """
        .. py:method:: disconnect

        Disconnects from the CasparCG server that we are connected to.

        """
        self.socket.close()

    def send_command(self, amcp_command):
        """
        .. py:method:: send_command(amcp_command)

        Sends an AMCP string to CasparCG, using the socket created using :py:meth:`~caspartalk.CasparServer.connect`.

        :param str amcp_command: The AMCP command string to send to CasparCG.

        """
        self.socket.sendall(amcp_command)

    def read_until(self, delimiter):
        """
        .. py:method:: read_until(delimiter)

        Reads the output from a CasparCG server over the socket created using \
        :py:meth:`~caspartalk.CasparServer.connect`. Continues reading until the *delimiter* character sequence is \
        found in the stream. This is useful when we know what character sequence will terminate a message from CasparCG.

        :param str delimiter: The character sequence that signifies the end of a message.
        :rtype: str
        :return: The string that CasparCG has sent, until the first instance of *delimiter*

        """
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
