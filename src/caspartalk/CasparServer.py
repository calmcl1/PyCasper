import socket
import AMCP
import ResponseInterpreter
from enum import Enum


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

        # self.media = self.get_media_on_server()
        self.templates = self.get_templates_on_server()

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
        template_fn_list = AMCP.tls(self)
        template_list = []
        for t in template_fn_list:
            tmpl = AMCP.info_template(self, t)
            if tmpl:
                template_list.append(tmpl)

        return template_list


# <log-level>       trace [trace|debug|info|warning|error]</log-level>
log_level = Enum('trace',
                 'debug',
                 'info',
                 'warning',
                 'error')

# <video-mode> PAL [PAL|NTSC|576p2500|720p2398|720p2400|720p2500|720p5000|720p2997|720p5994|720p3000|720p6000|
# 1080p2398|1080p2400|1080i5000|1080i5994|1080i6000|1080p2500|1080p2997|1080p3000|1080p5000|1080p5994|1080p6000|
# 1556p2398|1556p2400|1556p2500|dci1080p2398|dci1080p2400|dci1080p2500|2160p2398|2160p2400|2160p2500|2160p2997|
# 2160p3000|dci2160p2398|dci2160p2400|dci2160p2500] </video-mode>
video_mode = Enum('PAL', 'NTSC', '576p2500', '720p2398', '720p2400', '720p2500', '720p5000', '720p2997', '720p5994',
                  '720p3000', '720p6000', '1080p2398', '1080p2400', '1080i5000', '1080i5994', '1080i6000', '1080p2500',
                  '1080p2997', '1080p3000', '1080p5000', '1080p5994', '1080p6000', '1556p2398', '1556p2400',
                  '1556p2500', 'dci1080p2398', 'dci1080p2400', 'dci1080p2500', '2160p2398', '2160p2400', '2160p2500',
                  '2160p2997', '2160p3000', 'dci2160p2398', 'dci2160p2400', 'dci2160p2500')

# <channel-layout>stereo [mono|stereo|dts|dolbye|dolbydigital|smpte|passthru]</channel-layout>
channel_layout = Enum('mono', 'stereo', 'dts', 'dolbye', 'dolbydigital', 'smpte', 'passthru')

# <latency>normal [normal|low|default]</latency>
latency = Enum('normal', 'low', 'default')

# <keyer>external [external|external_separate_device|internal|default]</keyer>
keyer = Enum('external', 'external_separate_device', 'internal', 'default')

# <aspect-ratio>default [default|4:3|16:9]</aspect-ratio>
aspect_ratio = Enum('default', '4:3', '16:9')

# <vcodec>libx264 [libx264|qtrle]</vcodec>
vcodec = Enum('libx264', 'qtrle')


# Everything we could have:
# <log-level>       trace [trace|debug|info|warning|error]</log-level>
# <channel-grid>    false [true|false]</channel-grid>
# <mixer>
#     <blend-modes>          false [true|false]</blend-modes>
#     <straight-alpha>       false [true|false]</straight-alpha>
#     <chroma-key>           false [true|false]</chroma-key>
#     <mipmapping_default_on>false [true|false]</mipmapping_default_on>
# </mixer>
# <auto-deinterlace>true  [true|false]</auto-deinterlace>
# <auto-transcode>  true  [true|false]</auto-transcode>
# <pipeline-tokens> 2     [1..]       </pipeline-tokens>
# <template-hosts>
#     <template-host>
#         <video-mode/>
#         <filename/>
#         <width/>
#         <height/>
#     </template-host>
# </template-hosts>
# <flash>
#     <buffer-depth>auto [auto|1..]</buffer-depth>
# </flash>
# <thumbnails>
#     <generate-thumbnails>true [true|false]</generate-thumbnails>
#     <width>256</width>
#     <height>144</height>
#     <video-grid>2</video-grid>
#     <scan-interval-millis>5000</scan-interval-millis>
#     <generate-delay-millis>2000</generate-delay-millis>
#     <video-mode>720p2500</video-mode>
#     <mipmap>false</mipmap>
# </thumbnails>
# <channels>
#     <channel>
#         <video-mode> PAL [PAL|NTSC|576p2500|720p2398|720p2400|720p2500|720p5000|720p2997|720p5994|720p3000|720p6000|1080p2398|1080p2400|1080i5000|1080i5994|1080i6000|1080p2500|1080p2997|1080p3000|1080p5000|1080p5994|1080p6000|1556p2398|1556p2400|1556p2500|dci1080p2398|dci1080p2400|dci1080p2500|2160p2398|2160p2400|2160p2500|2160p2997|2160p3000|dci2160p2398|dci2160p2400|dci2160p2500] </video-mode>
#         <channel-layout>stereo [mono|stereo|dts|dolbye|dolbydigital|smpte|passthru]</channel-layout>
#         <straight-alpha-output>false [true|false]</straight-alpha-output>
#         <consumers>
#             <decklink>
#                 <device>[1..]</device>
#                 <key-device>device + 1 [1..]</key-device>
#                 <embedded-audio>false [true|false]</embedded-audio>
#                 <channel-layout>stereo [mono|stereo|dts|dolbye|dolbydigital|smpte|passthru]</channel-layout>
#                 <latency>normal [normal|low|default]</latency>
#                 <keyer>external [external|external_separate_device|internal|default]</keyer>
#                 <key-only>false [true|false]</key-only>
#                 <buffer-depth>3 [1..]</buffer-depth>
#                 <custom-allocator>true [true|false]</custom-allocator>
#             </decklink>
#             <bluefish>
#                 <device>[1..]</device>
#                 <embedded-audio>false [true|false]</embedded-audio>
#                 <channel-layout>stereo [mono|stereo|dts|dolbye|dolbydigital|smpte|passthru]</channel-layout>
#                 <key-only>false [true|false]</key-only>
#             </bluefish>
#             <system-audio></system-audio>
#             <screen>
#                 <device>[0..]</device>
#                 <aspect-ratio>default [default|4:3|16:9]</aspect-ratio>
#                 <stretch>fill [none|fill|uniform|uniform_to_fill]</stretch>
#                 <windowed>false [true|false]</windowed>
#                 <key-only>false [true|false]</key-only>
#                 <auto-deinterlace>true [true|false]</auto-deinterlace>
#                 <vsync>false [true|false]</vsync>
#                 <name>[Screen Consumer]</name>
#                 <borderless>false [true|false]</borderless>
#             </screen>
#             <newtek-ivga>
#               <channel-layout>stereo [mono|stereo|dts|dolbye|dolbydigital|smpte|passthru]</channel-layout>
#               <provide-sync>true [true|false]</provide-sync>
#             </newtek-ivga>
#             <file>
#                 <path></path>
#                 <vcodec>libx264 [libx264|qtrle]</vcodec>
#                 <separate-key>false [true|false]</separate-key>
#             </file>
#             <stream>
#                 <path></path>
#                 <args></args>
#             </stream>
#         </consumers>
#     </channel>
# </channels>
# <osc>
#   <default-port>6250</default-port>
#   <predefined-clients>
#     <predefined-client>
#       <address>127.0.0.1</address>
#       <port>5253</port>
#     </predefined-client>
#   </predefined-clients>
# </osc>
# <audio>
#   <channel-layouts>
#     <channel-layout>
#       <name>mono</name>
#       <type>1.0</type>
#       <num-channels>1</num-channels>
#       <channels>C</channels>
#     </channel-layout>
#     <channel-layout>
#       <name>stereo</name>
#       <type>2.0</type>
#       <num-channels>2</num-channels>
#       <channels>L R</channels>
#     </channel-layout>
#     <channel-layout>
#       <name>dts</name>
#       <type>5.1</type>
#       <num-channels>6</num-channels>
#       <channels>C L R Ls Rs LFE</channels>
#     </channel-layout>
#     <channel-layout>
#       <name>dolbye</name>
#       <type>5.1+stereomix</type>
#       <num-channels>8</num-channels>
#       <channels>L R C LFE Ls Rs Lmix Rmix</channels>
#     </channel-layout>
#     <channel-layout>
#       <name>dolbydigital</name>
#       <type>5.1</type>
#       <num-channels>6</num-channels>
#       <channels>L C R Ls Rs LFE</channels>
#     </channel-layout>
#     <channel-layout>
#       <name>smpte</name>
#       <type>5.1</type>
#       <num-channels>6</num-channels>
#       <channels>L R C LFE Ls Rs</channels>
#     </channel-layout>
#     <channel-layout>
#       <name>passthru</name>
#       <type>16ch</type>
#       <num-channels>16</num-channels>
#       <channels />
#     </channel-layout>
#   </channel-layouts>
#   <mix-configs>
#     <mix-config>
#       <from>1.0</from>
#       <to>2.0</to>
#       <mix>add</mix>
#       <mappings>
#         <mapping>C L 1.0</mapping>
#         <mapping>C R 1.0</mapping>
#       </mappings>
#     </mix-config>
#     <mix-config>
#       <from>1.0</from>
#       <to>5.1</to>
#       <mix>add</mix>
#       <mappings>
#         <mapping>C L 1.0</mapping>
#         <mapping>C R 1.0</mapping>
#       </mappings>
#     </mix-config>
#     <mix-config>
#       <from>1.0</from>
#       <to>5.1+stereomix</to>
#       <mix>add</mix>
#       <mappings>
#         <mapping>C L    1.0</mapping>
#         <mapping>C R    1.0</mapping>
#         <mapping>C Lmix 1.0</mapping>
#         <mapping>C Rmix 1.0</mapping>
#       </mappings>
#     </mix-config>
#     <mix-config>
#       <from>2.0</from>
#       <to>1.0</to>
#       <mix>add</mix>
#       <mappings>
#         <mapping>L C 1.0</mapping>
#         <mapping>R C 1.0</mapping>
#       </mappings>
#     </mix-config>
#     <mix-config>
#       <from>2.0</from>
#       <to>5.1</to>
#       <mix>add</mix>
#       <mappings>
#         <mapping>L L 1.0</mapping>
#         <mapping>R R 1.0</mapping>
#       </mappings>
#     </mix-config>
#     <mix-config>
#       <from>2.0</from>
#       <to>5.1+stereomix</to>
#       <mix>add</mix>
#       <mappings>
#         <mapping>L L    1.0</mapping>
#         <mapping>R R    1.0</mapping>
#         <mapping>L Lmix 1.0</mapping>
#         <mapping>R Rmix 1.0</mapping>
#       </mappings>
#     </mix-config>
#     <mix-config>
#       <from>5.1</from>
#       <to>1.0</to>
#       <mix>average</mix>
#       <mappings>
#         <mapping>L  C 1.0</mapping>
#         <mapping>R  C 1.0</mapping>
#         <mapping>C  C 0.707</mapping>
#         <mapping>Ls C 0.707</mapping>
#         <mapping>Rs C 0.707</mapping>
#       </mappings>
#     </mix-config>
#     <mix-config>
#       <from>5.1</from>
#       <to>2.0</to>
#       <mix>average</mix>
#       <mappings>
#         <mapping>L  L 1.0</mapping>
#         <mapping>R  R 1.0</mapping>
#         <mapping>C  L 0.707</mapping>
#         <mapping>C  R 0.707</mapping>
#         <mapping>Ls L 0.707</mapping>
#         <mapping>Rs R 0.707</mapping>
#       </mappings>
#     </mix-config>
#     <mix-config>
#       <from>5.1</from>
#       <to>5.1+stereomix</to>
#       <mix>average</mix>
#       <mappings>
#         <mapping>L   L   1.0</mapping>
#         <mapping>R   R   1.0</mapping>
#         <mapping>C   C   1.0</mapping>
#         <mapping>Ls  Ls  1.0</mapping>
#         <mapping>Rs  Rs  1.0</mapping>
#         <mapping>LFE LFE 1.0</mapping>
#
#         <mapping>L  Lmix 1.0</mapping>
#         <mapping>R  Rmix 1.0</mapping>
#         <mapping>C  Lmix 0.707</mapping>
#         <mapping>C  Rmix 0.707</mapping>
#         <mapping>Ls Lmix 0.707</mapping>
#         <mapping>Rs Rmix 0.707</mapping>
#       </mappings>
#     </mix-config>
#     <mix-config>
#       <from>5.1+stereomix</from>
#       <to>1.0</to>
#       <mix>add</mix>
#       <mappings>
#         <mapping>Lmix C 1.0</mapping>
#         <mapping>Rmix C 1.0</mapping>
#       </mappings>
#     </mix-config>
#     <mix-config>
#       <from>5.1+stereomix</from>
#       <to>2.0</to>
#       <mix>add</mix>
#       <mappings>
#         <mapping>Lmix L 1.0</mapping>
#         <mapping>Rmix R 1.0</mapping>
#       </mappings>
#     </mix-config>
#     <mix-config>
#       <from>5.1+stereomix</from>
#       <to>5.1</to>
#       <mix>add</mix>
#       <mappings>
#         <mapping>L   L   1.0</mapping>
#         <mapping>R   R   1.0</mapping>
#         <mapping>C   C   1.0</mapping>
#         <mapping>Ls  Ls  1.0</mapping>
#         <mapping>Rs  Rs  1.0</mapping>
#         <mapping>LFE LFE 1.0</mapping>
#       </mappings>
#     </mix-config>
#   </mix-configs>
# </audio>


class ServerConfig:
    def __init__(self):
        self.log_level = log_level.trace
        self.channel_grid = False
        self.mixer = {} # TODO: Create Mixer info
        self.auto_deinterlace = True
        self.auto_transcode = True
        self.pipeline_tokens = 2
        self.template_hosts = {} # TODO: Create TemplateHost objects
        self.flash = {} # TODO: Create Flash object
        self.thumbnails = {} # TODO: Create Thumbnails infp
        self.channels = [] # TODO: Create channels info
        self.osc = {} # TODO: Create OSC info
        self.audio = {} # TODO: Create ChannelAudio object

        raise NotImplementedError