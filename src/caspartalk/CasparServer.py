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
log_level = Enum('trace', 'debug', 'info', 'warning', 'error')

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

# <stretch>fill [none|fill|uniform|uniform_to_fill]</stretch>
stretch = Enum('none', 'fill', 'uniform', 'uniform_to_fill')

# <vcodec>libx264 [libx264|qtrle]</vcodec>
vcodec = Enum('libx264', 'qtrle')


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
        self.channel_grid = False  # <channel-grid>    false [true|false]</channel-grid>

        # <mixer>
        self.mixer = {'blend_modes': False,  # <blend-modes>false [true|false]</blend-modes>
                      'straight_alpha': False,  # <straight-alpha>false [true|false]</straight-alpha>
                      'chroma_key': False,  # <chroma-key>false [true|false]</chroma-key>
                      'mipmapping_default_on': False}  # <mipmapping_default_on>false [true|false]</mipmapping_default_on>
        # </mixer>

        self.auto_deinterlace = True  # <auto-deinterlace>true  [true|false]</auto-deinterlace>
        self.auto_transcode = True  # <auto-transcode>  true  [true|false]</auto-transcode>
        self.pipeline_tokens = 2  # <pipeline-tokens> 2     [1..]       </pipeline-tokens>

        # <template-hosts>
        #     <template-host>
        #         <video-mode/>
        #         <filename/>
        #         <width/>
        #         <height/>
        #     </template-host>
        # </template-hosts>
        #

        self.template_hosts = {}  # TODO: Create TemplateHost objects

        # <flash>
        self.flash = {'buffer_depth': 'auto'}  # <buffer-depth>auto [auto|1..]</buffer-depth>
        # </flash>

        # <thumbnails>
        self.thumbnails = {'generate_thumbnails': True,  # <generate-thumbnails>true [true|false]</generate-thumbnails>
                           'width': 256,  # <width>256</width>
                           'height': 144,  # <height>144</height>
                           'video_grid': 2,  # <video-grid>2</video-grid>
                           'scan_interval_millis': 5000,  # <scan-interval-millis>5000</scan-interval-millis>
                           'generate-delay-millis': 2000,  # <generate-delay-millis>2000</generate-delay-millis>
                           'video-mode': video_mode.720p2500,  # <video-mode>720p2500</video-mode>
                           'mipmap': False}  # <mipmap>false</mipmap>
        # </thumbnails>

        self.channels = []  # TODO: Create Channels object
        self.osc = {}  # TODO: Create OSC object
        self.audio = {}  # TODO: Create ChannelAudio object

        raise NotImplementedError

class Channel:
    def __init__(self):
        # <channel>
        self.video_mode = video_mode.PAL  # <video-mode> PAL [PAL|NTSC|576p2500|720p2398|720p2400|... ]</video-mode>
        self.channel_layout = channel_layout.stereo  # <channel-layout>stereo [mono|stereo|dts|... ]</channel-layout>
        self.straight_alpha_output = False  # <straight-alpha-output>false [true|false]</straight-alpha-output>
        self.consumers = []
        # </channel>


class Consumer:
    def __init__(self):
        pass

class ConsumerDecklink(Consumer):
    def __init__(self):
        Consumer.__init__(self)

        # <decklink>
        self.device = 1  # <device>[1..]</device>
        self.key_device =self.device + 1  # <key-device>device + 1 [1..]</key-device>
        self.embedded_audio = False  # <embedded-audio>false [true|false]</embedded-audio>
        self.channel_layout = channel_layout.stereo
        self.latency = latency.normal  # <latency>normal [normal|low|default]</latency>
        self.keyer = keyer.external  # <keyer>external [external|external_separate_device|internal|default]</keyer>
        self.key_only = False  # <key-only>false [true|false]</key-only>
        self.buffer_depth = 3  # <buffer-depth>3 [1..]</buffer-depth>
        self.custom_allocator = True  # <custom-allocator>true [true|false]</custom-allocator>
        # </decklink>

class ConsumerBluefish(Consumer):
    def __init__(self):
        Consumer.__init__(self)

        # <bluefish>
        self.device = 1  # <device>[1..]</device>
        self.embedded_audio = False  # <embedded-audio>false [true|false]</embedded-audio>
        self.channel_layout = channel_layout.stereo  # <channel-layout>stereo [mono|stereo|... ]</channel-layout>
        self.key_only = False  # <key-only>false [true|false]</key-only>
        # </bluefish>

class ConsumerSystemAudio(Consumer):
    def __init__(self):
        Consumer.__init__(self)

class ConsumerScreen(Consumer):
    def __init__(self):
        Consumer.__init__(self)

        # <screen>
        self.device = 0  # <device>[0..]</device>
        self.aspect_ratio = aspect_ratio.default  # <aspect-ratio>default [default|4:3|16:9]</aspect-ratio>
        self.stretch = stretch.fill  # <stretch>fill [none|fill|uniform|uniform_to_fill]</stretch>
        self.windowed = False  # <windowed>false [true|false]</windowed>
        self.key_only = False  # <key-only>false [true|false]</key-only>
        self.auto_deinterlace = True  # <auto-deinterlace>true [true|false]</auto-deinterlace>
        self.vsync = False  # <vsync>false [true|false]</vsync>
        self.name = "Screen Consumer"  # <name>[Screen Consumer]</name>
        self.borderless = False  # <borderless>false [true|false]</borderless>
        # </screen>

class ConsumerNewtekIVGA(Consumer):
    def __init__(self):
        Consumer.__init__()

        # <newtek-ivga>
        self.channel_layout = channel_layout.stereo  # <channel-layout>stereo [mono|stereo|... ]</channel-layout>
        self.provide_sync = True  # <provide-sync>true [true|false]</provide-sync>
        # </newtek-ivga>

class ConsumerFile(Consumer):
    def __init__(self):
        Consumer.__init__()

        # <file>
        self.path = ""  # <path></path>
        self.vcodec = vcodec.libx264  # <vcodec>libx264 [libx264|qtrle]</vcodec>
        self.separate_key = False  # <separate-key>false [true|false]</separate-key>
        # </file>

class ConsumerStream(Consumer):
    def __init__(self):
        Consumer.__init__(self)

        # <stream>
        self.path = ""  # <path></path>
        self.args = ""  # <args></args>
        # </stream>