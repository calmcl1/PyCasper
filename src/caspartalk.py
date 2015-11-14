import telnetlib
import json


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


class CasparTalker:
    # CasparTalker is pretty much just responsible for two things:
    # Firstly, interpreting user commands and generating the right AMCP string
    # Secondly, sending the AMCP string to the CasparCG server.
    def __init__(self):
        pass

    def send_command_to_caspar(self, server, amcp_command):
        print "Sending command:", amcp_command
        if not amcp_command.endswith("\r\n"): amcp_command += "\r\n"
        server.send_command(amcp_command)

    # Data commands - create and manipulate datasets

    def data_store(self, server, name, data):
        # DATA STORE [name:string] [data:string]
        # Stores the dataset data under the name name.
        # Directories will be created if they do not exist.

        data = json.dumps(data) # Escape quotes, etc.
        amcp_string = "DATA STORE {name} {data}".format(name=name, data=data)

        self.send_command_to_caspar(server, amcp_string)

    def data_retrieve(self, server, name):
        # DATA RETRIEVE [name:string]
        # Returns the data saved under the name name.
        raise NotImplementedError

    def data_list(self, server):
        # DATA LIST
        # Returns a list of all stored datasets.
        raise NotImplementedError

    def data_remove(self, server, name):
        # DATA REMOVE [name:string]
        # Removes the dataset saved under the name name.
        raise NotImplementedError

    # CG Commands - manipulate Flash templates in Caspar
    def cg_add(self, server, template, channel=1, layer=10, cg_layer=0, play_on_load=0, data=None):
        # CG [video_channel:int]{-[layer:int]|-9999} ADD [cg_layer:int] [template:string] [play-on-load:0,1] {[data]}
        # Prepares a template for displaying.
        # It won't show until you call CG PLAY (unless you supply the play-on-load flag, 1 for true).
        # Data is either inline XML or a reference to a saved dataset.

        data = json.dumps(data) # Escape quotes, etc.
        amcp_string = "CG {video_channel}-{layer} ADD {cg_layer} {template} {play_on_load} {data}".format(
            video_channel=channel, layer=layer, cg_layer=cg_layer, template=template, play_on_load=play_on_load,
            data=data)

        self.send_command_to_caspar(server, amcp_string)

    def cg_play(self, server, channel=1, layer=10, cg_layer=0):
        # CG [video_channel:int]{-[layer:int]|-9999} PLAY [cg_layer:int]
        # Plays and displays the template in the specified layer.

        amcp_string = "CG {video_channel}-{layer} PLAY {cg_layer}".format(video_channel=channel,
                                                                          layer=layer, cg_layer=cg_layer)

        self.send_command_to_caspar(server, amcp_string)

    def cg_stop(self, server, channel=1, layer=10, cg_layer=0):
        # CG [video_channel:int]{-[layer:int]|-9999} STOP [cg_layer:int]
        # Stops and removes the template from the specified layer.
        # This is different from REMOVE in that the template gets a chance to
        # animate out when it is stopped.

        amcp_string = "CG {video_channel}-{layer} STOP [cg_layer]".format(video_channel=channel, layer=layer,
                                                                          cg_layer=cg_layer)

        self.send_command_to_caspar(server, amcp_string)

    def cg_next(self, server, channel=1, layer=10, cg_layer=0):
        # CG [video_channel:int]{-[layer:int]|-9999} NEXT [cg_layer:int]
        # Triggers a "continue" in the template on the specified layer.
        # This is used to control animations that has multiple discreet steps.

        amcp_string = "CG {video_channel}-{layer} NEXT {cg_layer}".format(video_channel=channel, layer=layer,
                                                                          cg_layer=cg_layer)

        self.send_command_to_caspar(server, amcp_string)

    def cg_remove(self, server, channel=1, layer=10, cg_layer=0):
        # CG [video_channel:int]{-[layer:int]|-9999} REMOVE [cg_layer:int]
        # Removes the template from the specified layer.

        amcp_string = "CG {video_channel}-{layer} REMOVE {cg_layer}".format(video_channel=channel, layer=layer,
                                                                            cg_layer=cg_layer)

        self.send_command_to_caspar(server, amcp_string)

    def cg_clear(self, server, channel=1, layer=10):
        # CG [video_channel:int]{-[layer:int]|-9999} CLEAR
        # Removes all templates on a video layer. The entire cg producer will be removed.

        amcp_string = "CG {video_channel}-{layer} CLEAR".format(video_channel=channel, layer=layer)

        self.send_command_to_caspar(server, amcp_string)

    def cg_update(self, server, channel=1, layer=10, data=None):
        # CG [video_channel:int]{-[layer:int]|-9999} UPDATE [cg_layer:int] [data:string]
        # Sends new data to the template on specified layer.
        # Data is either inline XML or a reference to a saved dataset.

        data = json.dumps(data) # Escape quotes, etc.
        amcp_string = "CG {video_channel}-{layer} UPDATE {cg_layer} {data}".format(video_channel=channel,
                                                                                   layer=layer, data=data)

        self.send_command_to_caspar(server, amcp_string)

    def cg_invoke(self, server, method, channel=1, layer=0, cg_layer=1):
        # CG [video_channel:int]{-[layer:int]|-9999} INVOKE [cg_layer:int] [method:string]
        # Invokes the given method on the template on the specified layer.
        # Can be used to jump the playhead to a specific label.

        amcp_string = "CG {video_channel}-{layer} INVOKE {cg_layer} {method}".format(video_channel=channel, layer=layer,
                                                                                     cg_layer=cg_layer, method=method)

        self.send_command_to_caspar(server, amcp_string)

    def cg_info(self, server, channel=1, layer=10, cg_layer=1):
        # CG [video_channel:int]{-[layer:int]|-9999} INFO {[cg_layer:int]}
        # Retrieves information about the template on the specified layer.
        # If cg_layer is not given, information about the template host is given instead.

        amcp_string = "CG {video_channel}-{layer} INFO {cg_layer}".format(video_channel=channel, layer=layer,
                                                                          cg_layer=cg_layer)

        self.send_command_to_caspar(server, amcp_string)


class CasparListener:
    def __init__(self):
        pass

    def parse_caspar_stdout(self, caspar_output):
        pass

    # 100s: Information
    def parse_100(self):
        # 100 [action] - Information about an event.
        pass

    def parse_101(self):
        # 101 [action] - Information about an event. A line of data is being returned.
        pass

    # 200s: Successful
    def parse_200(self):
        # 200 [command] OK	- The command has been executed and several lines of data
        # (seperated by \r\n) are being returned (terminated with an additional \r\n)
        pass

    def parse_201(self):
        # 201 [command] OK	- The command has been executed and data (terminated by \r\n)
        # is being returned.
        pass

    def parse_202(self):
        # 202 [command] OK	- The command has been executed.
        pass

    # 400s: Client Error
    def parse_400(self):
        # 400 ERROR	- Command not understood
        pass

    def parse_401(self):
        # 401 [command] ERROR	- Illegal video_channel
        pass

    def parse_402(self):
        # 402 [command] ERROR	- Parameter missing
        pass

    def parse_403(self):
        # 403 [command] ERROR	- Illegal parameter
        pass

    def parse_404(self):
        # 404 [command] ERROR	- Media file not found
        pass

    # 500s: Server Error
    def parse_500(self):
        # 500 FAILED	- Internal server error
        pass

    def parse_501(self):
        # 501 [command] FAILED	- Internal server error
        pass

    def parse_502(self):
        # 502 [command] FAILED	- Media file unreadable
        pass


def get_template_fields():
    pass
