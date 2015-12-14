import socket
import AMCP
import ResponseInterpreter


class CasparServer:
    """
    :param str server_ip: The IP address of the CasparCG server that we want to communicate with.
    :param int port: The port that the CasparCG server at *server_ip* is listening for AMCP commands on.

    Represents a Caspar Server instance.

    CasparServer sorts out all of the network-related stuff that's involved in interfacing with CasparCG.

    Upon connection, it will access the CasparCG server and find as much information as possible about it, and store it
    here. The idea is that the user should never have to think about the physical CasparCG server, and that this
    should be a perfect analogue.

    Example:

        >>> my_caspar_server = CasparServer("192.168.1.50", 5250)
        >>> AMCP.cg_info(my_casper_server) # Or whatever, etc...

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

        # Set the list of media files available
        self.media = []

    def connect(self, server_ip="localhost", port=5250):
        """
        This will open and connect to a TCP socket in order to communicate with a CasparCG server, using the provided \
        IP or hostname and port.

        :param server_ip: The IP or hostname of the CasparCG server that you're connecting to.
        :param port: The port of the CasparCG server at the IP or hostname *server_ip*.

        """
        self.server_ip = server_ip
        self.server_port = port
        self.socket.connect((self.server_ip, self.server_port))

        self.media = self.get_media_on_server()
        self.templates = self.get_templates_on_server()

    def disconnect(self):
        """
        Disconnects from the CasparCG server that we are connected to.
        """
        self.socket.close()

    def send_string(self, command_string):
        """
        Sends a string to CasparCG, using the socket created using :py:meth:`~caspartalk.CasparServer.connect`.

        :param str command_string: The AMCP command string to send to CasparCG.

        """
        self.socket.sendall(command_string)

    def read_until(self, delimiter):
        """
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

    def send_amcp_command(self, amcp_command):
        """
        Sends a string containing an AMCP command to a specified CasparCG server.

        :param str amcp_command: The AMCP command string that will be sent to the CasparCG server.
        :return: Any response from the CasparCG server will be returned. If there is no response other than the \
        command status string, ``None`` will be returned. This might change in the future...

        """

        print "Sending command:", amcp_command
        if not amcp_command.endswith("\r\n"): amcp_command += "\r\n"
        self.send_string(amcp_command)

        response = self.read_until("\r\n")

        # ResponseInterpreter lets us know how to proceed - Caspar's way of sending information
        # is a bit vague.
        to_do = ResponseInterpreter.interpret_response(response)
        if to_do[1]:
            return self.read_until(to_do[2])
        else:
            return None

    def get_media_on_server(self):
        # TODO: Implement CasparServer.get_media_on_server
        # Use CasparObjects.Media
        raise NotImplementedError

    def get_templates_on_server(self):
        # TODO: Implement CasparServer.get_media_on_server
        # Use CasparObjects.Template
        raise NotImplementedError
