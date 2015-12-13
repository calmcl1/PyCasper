import json
import xml.etree.cElementTree as CET
import StringIO
import string
import ResponseInterpreter
import CasparExceptions


class CasparTalker:
    """
    *CasparTalker* provides a simple way to call :term:`AMCP` commands from Python. The *CasparTalker* class is
    responsible for building the AMCP command strings, sending them to a :py:class:`~caspartalk.CasparServer`, and
    handling any response from the *CasparServer*.

    However, this is **not** used to handle direct interactions with a physical CasparCG server - use
    :py:class:`~caspartalk.CasparServer` to handle the TCP connection to the server, then use *CasparTalker* to build
    the AMCP commands.

    """
    # CasparTalker is kind of a translation layer between the interface and Casper's
    # control protocol (currently AMCP).
    # It will build the correct AMCP string for a given command, tell the
    # CasparServer to send it, and handles the response.

    def __init__(self, server=None):
        """
        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that CasparTalker should use to get initial \
        data.
        """

        # TODO: Check we're using the right version of AMCP. This is currently 2.1

        # TODO: Should this really be here, or a part of CasparServer, since it changes a CasparServer property?
        if server:
            server.paths = self.info_paths(server)

    def send_amcp_command(self, server, amcp_command):
        """
        Sends an string containing an AMCP command to a specified CasparCG server.

        :param CasparServer server: the :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :param str amcp_command: The AMCP command string that will be sent to the CasparCG server.
        :return: Any response from the CasparCG server will be returned. If there is no response other than the \
        command status string, ``None`` will be returned. This might change in the future...

        """
        print "Sending command:", amcp_command
        if not amcp_command.endswith("\r\n"): amcp_command += "\r\n"
        server.send_command(amcp_command)

        response = server.read_until("\r\n")

        # ResponseInterpreter lets us know how to proceed - Caspar's way of sending information
        # is a bit vague.
        to_do = ResponseInterpreter.interpret_response(response)
        if to_do[1]:
            return server.read_until(to_do[2])
        else:
            return None

    # Query commands - return info about various things

    def tls(self, server):
        """
        Lists all template files in the templates folder.
        Use the command INFO PATHS to get the path to the templates folder.

        :param CasparServer server: the :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :rtype: List or None.
        :return: A list containing the relative path and name of all the templates in the CCG templates folder.
        """

        amcp_string = "TLS"
        templates_response = self.send_amcp_command(server, amcp_string)
        templates = []

        # The template list is returned in the following fashion (each line is an array entry):
        # "RELATIVE-PATH/TEMPLATE-NAME" SIZE-IN-BYTES TIMESTAMP
        # We'll strip the first quote and everything after (and including) the last quote

        for t in templates_response:
            if not t[0] == '"':
                break
            templates.append(t.split('"')[1])

        return templates

    def version(self, server, component=None):
        """
        Returns the version of the specified component. If *component* is None, then a list of all of the components
        available will be returned.

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :param str component: The component to query the version of.
        :rtype: List
        :return: A list containing either the version of the component queried, or of all of the components available.
        """

        # VERSION {[component:string]}
        # Returns the version of specified component.

        if component:
            amcp_string = "VERSION {0}".format(component)
        else:
            amcp_string = "VERSION"

        response = self.send_amcp_command(server, amcp_string)

        if response:
            return response[0]
        else:
            return None

    def info(self, server, channel=None, layer=None):
        """
        Get information about a channel or a specific layer on a channel.
        If layer is omitted information about the whole channel is returned.
        If both video_channel and layer are omitted, retrieves a list of the available channels.

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :param int channel: The number of the channel to query.
        :param int layer: The number of the layer on channel *channel* to query.
        :rtype: List
        :return: A list containing either a list of channels, the information about a given channel or information \
        about a given layer on a channel.
        """
        # INFO [video_channel:int]{-[layer:int]}

        if channel:
            if layer:
                amcp_string = "INFO {video_channel}-{layer}".format(video_channel=channel,
                                                                    layer=layer)
            else:
                amcp_string = "INFO {video_channel}".format(video_channel=channel)
        else:
            amcp_string = "INFO"

        response = self.send_amcp_command(server, amcp_string)

        if response:
            return response[0]
        else:
            return None

    def info_template(self, server, template):
        """
        .. warning:: This method has not been implemented in UberCarrot yet!
        
        Gets information about the specified template.

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :param str template: The name (including path relative to the CasparCG template directory) of the template \
        to query.
        :rtype: List
        :return: A list containing information on the queried template.
        """
        # INFO TEMPLATE [template:string]

        # TODO: implement INFO TEMPLATE command - though this can't really be done until CCG 2.1 is released

        amcp_string = "INFO TEMPLATE {template}".format(template=template)

        response = self.send_amcp_command(server, amcp_string)
        for r in response:
            print r

        raise NotImplementedError

    def info_config(self, server):
        """
        Gets the contents of the configuration used.

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :rtype: List
        :return: A list containing information about the configuration of the server.
        """
        # INFO CONFIG

        amcp_string = "INFO CONFIG"

        response = self.send_amcp_command(server, amcp_string)
        response = StringIO.StringIO(string.join(response, ""))

        config = {}

        for event, elem in CET.iterparse(response):

            if "path" in elem.tag:
                print "Skipping <paths> - use INFO PATHS instead"
                elem.clear()
            else:
                config[elem.tag] = elem.text
                elem.clear()

        # Just as a point, this doesn't really return anything useful yet, but we'll send something back anyway.

        return config

    def info_paths(self, server):
        """
        Gets information about the paths used in the CasparCG Server configuration.

        The returned List will contain a single entry, that contains a Dict, of the format:::

            {path_name: relative_path,
            ... }

        The *key* will be the name of the path (template, media, etc.), and the value will be the path itself, relative
        to the CasparCG installation directory. The only exception is the *initial* path, which is an absolute path to
        the CasparCG installation directory. Therefore, using ``os.join(paths[initial], paths[template])`` will
        return an absolute path to the CasparCG template directory.

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :rtype: List
        :return: A list containing a dictionary of the paths set by the CasparCG Server configuration.
        """
        # INFO PATHS

        amcp_string = "INFO PATHS"
        response = self.send_amcp_command(server, amcp_string)

        if not response: return None

        paths = {}
        response = StringIO.StringIO(string.join(response, ""))

        for event, elem in CET.iterparse(response):
            if "-path" in elem.tag:
                # Huzzah, we've found a path!
                print "Found", elem.tag, elem.text
                paths[elem.tag.split("-")[0]] = elem.text
                elem.clear()

        return paths

    def info_system(self, server):
        """
        .. warning:: This method has not been implemented in UberCarrot yet!

        Gets system information like OS, CPU and library version numbers.

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :rtype: List
        :return: A list containing various pieces of system information.
        """
        # INFO SYSTEM
        # TODO: implement INFO SYSTEM command

        #amcp_string = "INFO SYSTEM"

        #response = self.send_command_to_caspar(server, amcp_string)
        #for r in response: print r
        #response = StringIO.StringIO(string.join(response, ""))

        #for event, elem in CET.iterparse(response):
        #    if elem.tag == "paths":
        #        print "Skipping <paths> - use INFO PATHS instead"
        #        elem.clear()
        #    else: print CET.dump(elem)

        raise NotImplementedError

    def info_server(self, server):
        """
        .. warning:: This method has not been implemented in UberCarrot yet!

        Gets detailed information about all channels.
        
        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :rtype: List
        :return: Returns a list containing information about all the channels on the server.
        """

        # INFO SERVER
        # TODO: implement INFO SERVER command

        raise NotImplementedError

    def bye(self, server):
        """
        Disconnects from the server if connected remotely; if interacting directly with the console on the machine
        Caspar is running on then this will achieve the same as the KILL command.

        .. seealso:: :py:func:`caspartalk.CasparTalker.kill`

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :rtype: Bool
        :return: True if successful, otherwise False
        """

        # BYE

        amcp_string = "BYE"

        try:
            self.send_amcp_command(server, amcp_string)
        except CasparExceptions.CasparError:
            return False

        return True

    def kill(self, server):
        """
        Shuts the server down.

        .. seealso:: :py:func:`caspartalk.CasparTalker.bye`

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :rtype: Bool
        :return: True if successful, otherwise False
        """
        # KILL

        amcp_string = "KILL"

        try:
            self.send_amcp_command(server, amcp_string)
        except CasparExceptions.CasparError:
            return False

        return True

    # Data commands - create and manipulate datasets

    def data_store(self, server, name, data):
        """
        Stores the dataset *data* under the name *name*. Directories will be created if they do not exist.

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :param str name: The name to save the data under.
        :param str data: The data to save. All data will be escaped as per \
        `CasparCG's requirements <http://casparcg.com/wiki/CasparCG_2.1_AMCP_Protocol#Special_sequences>`_ \
        before being saved.
        :rtype: Bool
        :return: True if successful, otherwise False.
        """
        # DATA STORE [name:string] [data:string]

        data = json.dumps(data)  # Escape quotes, etc.
        amcp_string = "DATA STORE {name} {data}".format(name=name, data=data)

        try:
            self.send_amcp_command(server, amcp_string)
        except CasparExceptions.CasparError:
            return False

    def data_retrieve(self, server, name):
        """
        Returns the data saved under the name *name*.

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :param str name: The name of the dataset (saved as *name* in :py:func:`~caspartalk.CasparTalker.data_store`) \
        to retrieve.
        :rtype: List
        :return: A list containing the data saved under the name *name*.
        """
        # DATA RETRIEVE [name:string]

        amcp_string = "DATA RETRIEVE {name}".format(name=name)

        data = None

        try:
            data = self.send_amcp_command(server, amcp_string)
        except CasparExceptions.CasparError:
            return False

        return data

    def data_list(self, server):
        """
        Returns a list of all stored datasets.

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :rtype: List
        :return: A list of all the datasets stored in CasparCG.
        """
        # DATA LIST

        amcp_string = "DATA LIST"
        data = self.send_amcp_command(server, amcp_string)
        return data

    def data_remove(self, server, name):
        """
        .. warning:: Due to a bug in CasparCG Server 2.0.7 and previous, this command causes UC to hang!

        Removes the dataset saved under the name *name*.

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :param str name: The name of the dataset (saved as *name* in :py:func:`~caspartalk.CasparTalker.data_store`) \
        to remove.
        :rtype: Bool
        :return: True if successful, otherwise False.
        """

        # DATA REMOVE [name:string]
        # fixme - a bug with CCG 2.0 means this doens't work, as CCG returns a code 200, rather than 201.
        # This is fixed in CCG 2.1

        amcp_string = "DATA REMOVE {name}".format(name=name)

        try:
            self.send_amcp_command(server, amcp_string)
        except CasparExceptions.CasparError:
            return False

        return True

    # CG Commands - manipulate Flash templates in Caspar
    def cg_add(self, server, template, channel=1, layer=10, cg_layer=0, play_on_load=0, data=None):
        """
        Prepares a template for displaying.

        It won't show until you call CG PLAY (unless you supply the *play-on-load* flag, 1 for true).
        *Data* is either inline XML or a reference to a saved dataset.

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :param str template: The name (including directory relative to the CasparCG template directory) of the \
        template to load into CasparCG Server.
        :param int channel: The number of the channel to load the template into.
        :param int layer: The video layer of the channel to load the template into. Rarely required unless in case of \
        layering multiple video and CG elements.
        :param int cg_layer: The CG layer of the video layer.
        :param int play_on_load: If 1, the template will play as soon as it has been loaded.
        :param str data: Any data to pass to the template host, either as XML or the name of a stored dataset.
        :rtype: Bool
        :return: True if successful, otherwise False.
        """
        # CG [video_channel:int]{-[layer:int]|-9999} ADD [cg_layer:int] [template:string] [play-on-load:0,1] {[data]}

        data = json.dumps(data)  # Escape quotes, etc.
        amcp_string = "CG {video_channel}-{layer} ADD {cg_layer} {template} {play_on_load} {data}".format(
            video_channel=channel, layer=layer, cg_layer=cg_layer, template=template, play_on_load=play_on_load,
            data=data)

        try:
            self.send_amcp_command(server, amcp_string)
        except CasparExceptions.CasparError:
            return False

        return True

    def cg_play(self, server, channel=1, layer=10, cg_layer=0):
        """
        Plays and displays the template in the specified layer.

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :param int channel: The number of the channel containing the template to play.
        :param int layer: The number of the layer containing the template to play.
        :param int cg_layer: The number of the CG layer containing the template to play.
        :rtype: Bool
        :return: True if successful, otherwise False.
        """

        # CG [video_channel:int]{-[layer:int]|-9999} PLAY [cg_layer:int]

        amcp_string = "CG {video_channel}-{layer} PLAY {cg_layer}".format(video_channel=channel,
                                                                          layer=layer, cg_layer=cg_layer)

        try:
            self.send_amcp_command(server, amcp_string)
        except CasparExceptions.CasparError:
            return False

        return True

    def cg_stop(self, server, channel=1, layer=10, cg_layer=0):
        """
        Stops and removes the template from the specified layer.
        This is different from REMOVE in that the template gets a chance to
        animate out when it is stopped.

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :param int channel: The number of the channel containing the template to stop.
        :param int layer: The number of the layer containing the template to stop.
        :param int cg_layer: The number of the CG layer containing the template to stop.
        :rtype: Bool
        :return: True if successful, otherwise False.
        """
        # CG [video_channel:int]{-[layer:int]|-9999} STOP [cg_layer:int]

        amcp_string = "CG {video_channel}-{layer} STOP [cg_layer]".format(video_channel=channel, layer=layer,
                                                                          cg_layer=cg_layer)

        try:
            self.send_amcp_command(server, amcp_string)
        except CasparExceptions.CasparError:
            return False

        return True

    def cg_next(self, server, channel=1, layer=10, cg_layer=0):
        """
        Triggers a "continue" in the template on the specified layer.
        This is used to control animations that has multiple discrete steps.

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :param int channel: The number of the channel containing the template to trigger the NEXT command on.
        :param int layer: The number of the layer containing the template to trigger the NEXT command on.
        :param int cg_layer: The number of the CG layer containing the template to trigger the NEXT command on.
        :rtype: Bool
        :return: True if successful, otherwise False.
        """
        # CG [video_channel:int]{-[layer:int]|-9999} NEXT [cg_layer:int]

        amcp_string = "CG {video_channel}-{layer} NEXT {cg_layer}".format(video_channel=channel, layer=layer,
                                                                          cg_layer=cg_layer)

        try:
            self.send_amcp_command(server, amcp_string)
        except CasparExceptions.CasparError:
            return False

        return True

    def cg_remove(self, server, channel=1, layer=10, cg_layer=0):
        """
        Removes the template from the specified CG layer.

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :param int channel: The number of the channel containing the the template to remove.
        :param int layer: The number of the layer containing the the template to remove.
        :param int cg_layer: The number of the CG layer containing the the template to remove.
        :rtype: Bool
        :return: True if successful, otherwise False.
        """
        # CG [video_channel:int]{-[layer:int]|-9999} REMOVE [cg_layer:int]

        amcp_string = "CG {video_channel}-{layer} REMOVE {cg_layer}".format(video_channel=channel, layer=layer,
                                                                            cg_layer=cg_layer)

        try:
            self.send_amcp_command(server, amcp_string)
        except CasparExceptions.CasparError:
            return False

        return True

    def cg_clear(self, server, channel=1, layer=10):
        """
        Removes all templates on a video layer. The entire CG producer will be removed.

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :param int channel: The number of the channel containing the CG layer to remove all templates from.
        :param int layer: The number of the layer containing the CG layer to remove all templates from.
        :rtype: Bool
        :return: True if successful, otherwise False
        """
        # CG [video_channel:int]{-[layer:int]|-9999} CLEAR

        amcp_string = "CG {video_channel}-{layer} CLEAR".format(video_channel=channel, layer=layer)

        try:
            self.send_amcp_command(server, amcp_string)
        except CasparExceptions.CasparError:
            return False

        return True

    def cg_update(self, server, channel=1, layer=10, cg_layer = 0, data=None):
        """
        Sends new data to the template on specified CG layer.
        Data is either inline XML or a reference to a saved dataset.

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :param int channel: The number of the channel containing the template to send *data* to.
        :param int layer: The number of the layer containing the template to send *data* to.
        :param int cg_layer: The number of the cg_layer containing the template to send *data* to.
        :param str data: The data to send to the specified template. Either XML or the name of a stored dataset.
        :rtype: Bool
        :return: True if successful, otherwise False.
        """
        # CG [video_channel:int]{-[layer:int]|-9999} UPDATE [cg_layer:int] [data:string]

        data = json.dumps(data)  # Escape quotes, etc.
        amcp_string = "CG {video_channel}-{layer} UPDATE {cg_layer} {data}".format(video_channel=channel,
                                                                                   layer=layer, cg_layer=cg_layer,
                                                                                   data=data)

        try:
            self.send_amcp_command(server, amcp_string)
        except CasparExceptions.CasparError:
            return False

        return True

    def cg_invoke(self, server, method, channel=1, layer=10, cg_layer=0):
        """
        Invokes the given method on the template on the specified CG layer.
        Can be used to jump the playhead to a specific label.

        If using a Flash template, *method* can be an ActionScript method name or frame label. If using a Javascript
        template, *method* can be a Javascript method call.

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :param str method: The name of the AS label to jump to, AS method to call, or JS method to call.
        :param int channel: The number of the channel containing the template to call a method on.
        :param int layer: The number of the layer containing the template to call a method on.
        :param int cg_layer: The number of the CG layer containing the template to call a method on.
        :rtype: Bool
        :return: True if successful, otherwise False.
        """
        # CG [video_channel:int]{-[layer:int]|-9999} INVOKE [cg_layer:int] [method:string]

        amcp_string = "CG {video_channel}-{layer} INVOKE {cg_layer} {method}".format(video_channel=channel, layer=layer,
                                                                                     cg_layer=cg_layer, method=method)

        try:
            self.send_amcp_command(server, amcp_string)
        except CasparExceptions.CasparError:
            return False

        return True

    def cg_info(self, server, channel=1, layer=10, cg_layer=0):
        """
        Retrieves information about the template on the specified CG layer.
        If *cg_layer* is not given, information about the template host is given instead.

        :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
        :param int channel: The number of the channel containing the template to retrieve information about.
        :param int layer: The number of the layer containing the template to retrieve information about.
        :param int cg_layer: The number of the cg_layer containing the template to retrieve information about.
        :rtype: List
        :return: List containing information about the template on the specified CG layer.
        """

        # CG [video_channel:int]{-[layer:int]|-9999} INFO {[cg_layer:int]}

        amcp_string = "CG {video_channel}-{layer} INFO {cg_layer}".format(video_channel=channel, layer=layer,
                                                                          cg_layer=cg_layer)

        try:
            return self.send_amcp_command(server, amcp_string)
        except CasparExceptions.CasparError:
            return None
