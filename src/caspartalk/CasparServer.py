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

    # TODO #14: Add some sort of heartbeat to show that the connection is still alive?

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
        # TODO #15: Implement CasparServer.get_media_on_server
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
# Annoyingly, attributes can't start with integers, so every mode has been prefixed with 'vm_'.
video_mode = Enum('vm_PAL', 'vm_NTSC', 'vm_576p2500', 'vm_720p2398', 'vm_720p2400', 'vm_720p2500', 'vm_720p5000',
                  'vm_720p2997', 'vm_720p5994',
                  'vm_720p3000', 'vm_720p6000', 'vm_1080p2398', 'vm_1080p2400', 'vm_1080i5000', 'vm_1080i5994',
                  'vm_1080i6000', 'vm_1080p2500',
                  'vm_1080p2997', 'vm_1080p3000', 'vm_1080p5000', 'vm_1080p5994', 'vm_1080p6000', 'vm_1556p2398',
                  'vm_1556p2400',
                  'vm_1556p2500', 'vm_dci1080p2398', 'vm_dci1080p2400', 'vm_dci1080p2500', 'vm_2160p2398',
                  'vm_2160p2400', 'vm_2160p2500',
                  'vm_2160p2997', 'vm_2160p3000', 'vm_dci2160p2398', 'vm_dci2160p2400', 'vm_dci2160p2500')

# <channel-layout>stereo [mono|stereo|dts|dolbye|dolbydigital|smpte|passthru]</channel-layout>
# A list of all the AudioChannelLayouts
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

tcp_protocol = Enum('AMCP', 'LOG')


class ServerConfig:
    def __init__(self):
        # This is set up with the default values from the config.
        # Upon initialization, we'll populate these with any values that have been manually overridden.

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

        self.template_hosts = []

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
                           'video-mode': video_mode.vm_720p2500,  # <video-mode>720p2500</video-mode>
                           'mipmap': False}  # <mipmap>false</mipmap>
        # </thumbnails>

        self.channels = []
        self.osc = []
        self.controllers = []
        self.audio_configs = AudioConfig(True)


class Channel:
    def __init__(self, ch_video_mode=video_mode.vm_PAL, ch_channel_layout=channel_layout.stereo,
                 ch_straight_alpha_output=False,
                 ch_consumers=[]):
        # <channel>
        if ch_video_mode not in video_mode:
            raise ValueError(
                    "{mode} is not a valid video mode:\r\n{modes}".format(mode=str(ch_video_mode),
                                                                          modes=list(video_mode)))
        self.video_mode = ch_video_mode

        if ch_channel_layout not in channel_layout:
            raise ValueError("{ch_lo} is not a valid channel layout:\r\n{los}".format(ch_lo=str(ch_channel_layout),
                                                                                      los=list(channel_layout)))
        self.channel_layout = ch_channel_layout

        if not isinstance(ch_straight_alpha_output, bool):
            raise ValueError(
                    "Expected a boolean for ch_straight_alpha_output, got {t}".format(t=type(ch_straight_alpha_output)))

        self.straight_alpha_output = ch_straight_alpha_output

        if not isinstance(ch_consumers, (list, tuple)):
            raise ValueError("Expected a list of Consumers for ch_consumers, got {t}".format(t=type(ch_consumers)))
        self.consumers = ch_consumers
        # </channel>


class Consumer:
    def __init__(self):
        pass


class ConsumerDecklink(Consumer):
    def __init__(self):
        Consumer.__init__(self)

        # <decklink>
        self.device = 1  # <device>[1..]</device>
        self.key_device = self.device + 1  # <key-device>device + 1 [1..]</key-device>
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


class TemplateHost:
    def __init__(self, th_video_mode=None, th_filename=None, th_width=None, th_height=None):
        # <template-hosts>
        #    <template-host>
        #        <video-mode/>
        #        <filename/>
        #        <width/>
        #        <height/>
        #    </template-host>
        # </template-hosts>
        self.video_mode = th_video_mode | video_mode.vm_PAL
        self.filename = th_filename | ""
        self.width = th_width | 0
        self.height = th_height | 0


class OSC:
    def __init__(self, default_port=None):
        self.default_port = 6250
        self.predefined_clients = []

        if isinstance(default_port, int):
            self.default_port = default_port
        elif default_port:
            # default_port is supplied, but is not an int
            raise TypeError("Expected int for default_port, got {wrong_t}".format(wrong_t=type(default_port)))


class OSCPredefinedClient:
    def __init__(self, address="localhost", port=5253):
        self.address = self.port = None

        if isinstance(address, str):
            self.address = address
        else:
            raise TypeError("Expected string for address, got {wrong_t}".format(wrong_t=type(address)))

        if isinstance(port, int):
            self.port = port
        else:
            raise TypeError("Expected int for port, got {wrong_t}".format(wrong_t=type(port)))


class TCPController:
    def __init__(self, protocol, port=5250):
        self.protocol = protocol

        if isinstance(port, int):
            self.port = port
        else:
            raise TypeError("Expected int for port, got {wrong_t}".format(wrong_t=type(port)))


class AudioConfig:
    def __init__(self, use_default=True):
        self.channel_layouts = {}
        self.mix_configs = []

        if use_default:
            self.channel_layouts = {"mono": AudioChannelLayout("mono", "1.0", 1, "C"),
                                    "stereo": AudioChannelLayout("stereo", "2.0", 2, "L R"),
                                    "dts": AudioChannelLayout("dts", "5.1", 6, "C L R Ls Rs LFE"),
                                    "dolbye": AudioChannelLayout("dolbye", "5.1+stereomix", 8,
                                                                 "L R C LFE Ls Rs Lmix Rmix"),
                                    "dolbydigital": AudioChannelLayout("dolbydigital", "5.1", 6, "L C R Ls Rs LFE"),
                                    "smpte": AudioChannelLayout("smpte", "5.1", 6, "L R C LFE Ls Rs"),
                                    "passthru": AudioChannelLayout("passthru", "16ch", 16)
                                    }

            self.mix_configs = [AudioMixConfig("1.0", "2.0", "add", ("C L 1.0", "C R 1.0")),
                                AudioMixConfig("1.0", "5.1", "add", ("C L 1.0", "C R 1.0")),
                                AudioMixConfig("1.0", "5.1+stereomix", "add", ("C L 1.0",
                                                                               "C R 1.0",
                                                                               "C Lmix 1.0",
                                                                               "C Rmix 1.0")),
                                AudioMixConfig("2.0", "1.0", "add", ("L C 1.0", "R C 1.0")),
                                AudioMixConfig("2.0", "5.1", "add", ("L L 1.0", "R R 1.0")),
                                AudioMixConfig("2.0", "5.1+stereomix", "add", ("L L 1.0",
                                                                               "R R 1.0",
                                                                               "R RMix 1.0")),
                                AudioMixConfig("5.1", "1.0", "average", ("L C 1.0",
                                                                         "R C 1.0",
                                                                         "C C 0.707",
                                                                         "Ls C 0.707",
                                                                         "Rs C 0.707")),
                                AudioMixConfig("5.1", "2.0", "average", ("L L 1.0",
                                                                         "R R 1.0",
                                                                         "C L 0.707",
                                                                         "C R 0.707",
                                                                         "L Lmix 1.0",
                                                                         "Ls L 0.707",
                                                                         "Rs R 0.707")),
                                AudioMixConfig("5.1", "5.1+stereomix", "average", ("L L 1.0",
                                                                                   "R R 1.0",
                                                                                   "C C 1.0",
                                                                                   "Ls Ls 1.0",
                                                                                   "Rs Rs 1.0",
                                                                                   "LFE LFE 1.0",
                                                                                   "L Lmix 1.0",
                                                                                   "R Rmix 1.0",
                                                                                   "C Lmix 0.707",
                                                                                   "C Rmix 0.707",
                                                                                   "Ls Lmix 0.707",
                                                                                   "Rs Rmix 0.707")),
                                AudioMixConfig("5.1+stereomix", "1.0", "add", ("Lmix C 1.0",
                                                                               "Rmix C 1.0")),
                                AudioMixConfig("5.1+stereomix", "2.0", "add", ("Lmix L 1.0",
                                                                               "Rmix R 1.0")),
                                AudioMixConfig("5.1+stereomix", "5.1", "add", ("L L 1.0",
                                                                               "R R 1.0",
                                                                               "C C 1.0",
                                                                               "Ls Ls 1.0",
                                                                               "Rs Rs 1.0",
                                                                               "LFE LFE 1.0"))
                                ]


class AudioChannelLayout:
    def __init__(self, name, type_, num_channels, channels=""):
        # <channel-layout>
        self.name = name  # <name>mono</name>
        self.type = type_  # <type>1.0</type>
        self.num_channels = num_channels  # <num-channels>1</num-channels>
        self.channels = channels  # <channels>C</channels> Can be None - see 'passthru'
        # </channel-layout>


class AudioMixConfig:
    def __init__(self, from_, to, mix, mappings):
        self.from_ = from_
        self.to = to
        self.mix = mix
        self.mappings = None
        if isinstance(mappings, tuple):
            self.mappings = mappings
        else:
            raise TypeError("Expected int for default_port, got {wrong_t}".format(wrong_t=type(mappings)))
