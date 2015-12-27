import json
import xml.etree.cElementTree as cET
import StringIO
import string
import CasparExceptions
import CasparObjects
import CasparServer

# Query commands - return info about various things


def tls(server):
    """
    Lists all template files in the templates folder.
    Use :py:func:`~caspartalk.AMCP.info_paths` to get the path to the templates folder.

    :param CasparServer server: the :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
    :rtype: List or None.
    :return: A list containing the relative path and name of all the templates in the CCG templates folder.
    """

    amcp_string = "TLS"
    templates_response = server.send_amcp_command(amcp_string)
    templates = []

    # The template list is returned in the following fashion (each line is an array entry):
    # "RELATIVE-PATH/TEMPLATE-NAME" SIZE-IN-BYTES TIMESTAMP
    # We'll strip the first quote and everything after (and including) the last quote

    for t in templates_response:
        if not t[0] == '"':
            break
        templates.append(t.split('"')[1])

    return templates


def version(server, component=None):
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

    response = server.send_amcp_command(amcp_string)

    if response:
        return response[0]
    else:
        return None


def info(server, channel=None, layer=None):
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

    response = server.send_amcp_command(amcp_string)

    if response:
        return response[0]
    else:
        return None


def info_template(server, template_fn):
    """
    .. warning:: This method has not been implemented in UberCarrot yet!

    Gets information about the specified template.

    :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
    :param str template_fn: The name (including path relative to the CasparCG template directory) of the template \
    to query.
    :rtype: :py:class:`~caspartalk.CasparObjects.Template`
    :return: A Template populated with the correct data.
    """
    # INFO TEMPLATE [template:string]

    if not isinstance(template_fn, str):
        raise TypeError("Expected string for template, got {0}".format(type(template_fn)))

    amcp_string = "INFO TEMPLATE {template}".format(template=template_fn)

    try:
        response = server.send_amcp_command(amcp_string)
    except CasparExceptions.IllegalParameterError:
        print "Cannot find template data for", template_fn
        return None
    # for r in response:
    #    print r

    template = CasparObjects.Template(server, template_fn)

    el_template = cET.fromstringlist(response)

    print "Template:", template_fn

    if el_template.tag != "template":
        print "No Template found!"
        return None

    if el_template.attrib:
        print el_template.attrib.keys()

        # Find the basic information about the Template
        if "version" in el_template.attrib.keys():
            template.version = el_template.attrib["version"]
        if "authorName" in el_template.attrib.keys():
            template.author_name = el_template.attrib["authorName"]
        if "authorEmail" in el_template.attrib.keys():
            template.author_email = el_template.attrib["authorEmail"]
        if "templateInfo" in el_template.attrib.keys():
            template.template_info = el_template.attrib["templateInfo"]
        if "originalWidth" in el_template.attrib.keys():
            template.original_width = el_template.attrib["originalWidth"]
        if "originalHeight" in el_template.attrib.keys():
            template.original_height = el_template.attrib["originalHeight"]
        if "originalFrameRate" in el_template.attrib.keys():
            template.original_frame_rate = el_template.attrib["originalFrameRate"]

    # Find all the components and their properties, then add these to the Template
    el_components = el_template.find("components").findall("component")
    if el_components is not None and len(list(el_components)):
        for comp in list(el_components):
            print "\tFound component", comp.attrib["name"]
            el_comp_properties = comp.findall("property")
            prop_id = prop_type = prop_info = None
            for prop in el_comp_properties:
                prop_id = prop.attrib["name"]
                print "\t\tID:", prop_id
                prop_type = prop.attrib["type"]
                print "\t\tType:", prop_type
                prop_info = prop.attrib["info"]
                print "\t\tInfo:", prop_info
            comp_prop = CasparObjects.ComponentProperty(prop_id, prop_type, prop_info)
            template.components[comp.attrib["name"]] = CasparObjects.TypedDict(CasparObjects.ComponentProperty)
            template.components[comp.attrib["name"]][prop_id] = comp_prop
    else:
        print "\tNo components found"

    # Find all the keyframes and add them to the Template
    el_keyframes = el_template.find("keyframes")
    if el_keyframes is not None and len(list(el_keyframes)):
        for kf in list(el_keyframes):
            print "\tFound keyframe:", kf.attrib["name"]
            template.keyframes.append(kf.attrib["name"])
    else:
        print "\tNo keyframes found"

    # Find all the instances and add them to the Template
    el_instances = el_template.find("instances")
    if el_instances is not None and len(list(el_instances)):
        for inst in list(el_instances):
            print "\tFound instance", inst.attrib["name"]
            print "\t\tType:", inst.attrib["type"]
            if template.components[inst.attrib["type"]]:
                print "\t\tGood reference"
                template.instances[inst.attrib["name"]] = inst.attrib["type"]
            else: print "Bad reference to", inst.attrib["type"]
    else:
        print "\tNo instances found"

    # Find all the parameters and add them to the Template

    el_parameters = el_template.find("parameters")
    if el_parameters is not None:
        for param in list(el_parameters):
            param_id = param_type = param_info = None
            param_id = param.attrib["id"]
            print "\tFound parameter:", param_id
            param_type = param.attrib["type"]
            print "\t\tType:", param_type
            param_info = param.attrib["info"]
            print "\t\tInfo:", param_info
            temp_param = CasparObjects.TemplateParameter(param_id, param_type, param_info)
            template.parameters[param_id] = temp_param
    else:
        print "\tNo parameters found"

    return template


def info_config(server):
    """
    .. warning:: This method has not been implemented in UberCarrot yet!


    Gets the contents of the configuration used.

    :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
    :rtype: :py:class:`caspartalk.CasparServer.ServerConfig`
    :return: A ServerConfig containing information about the configuration of the server.
    """
    # INFO CONFIG
    # TODO: Implement info_config command

    raise NotImplementedError

    amcp_string = "INFO CONFIG"
    response = server.send_amcp_command(amcp_string)
    response = StringIO.StringIO(string.join(response, ""))

    for event, elem in cET.iterparse(response):

        if "path" in elem.tag:
            print "Skipping <paths> - use INFO PATHS instead"
            elem.clear()
        else:
            config[elem.tag] = elem.text
            elem.clear()

    # Just as a point, this doesn't really return anything useful yet, but we'll send something back anyway.

    return config


def info_paths(server):
    """
    Gets information about the paths used in the CasparCG Server configuration.

    The returned List will contain a single entry, that contains a Dict, of the format:::

        {path_name: relative_path,
        ... }

    The *key* will be the name of the path (template, media, etc.), and the value will be the path itrelative
    to the CasparCG installation directory. The only exception is the *initial* path, which is an absolute path to
    the CasparCG installation directory. Therefore, using ``os.join(paths[initial], paths[template])`` will
    return an absolute path to the CasparCG template directory.

    :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
    :rtype: List
    :return: A list containing a dictionary of the paths set by the CasparCG Server configuration.
    """
    # INFO PATHS

    amcp_string = "INFO PATHS"
    response = server.send_amcp_command(amcp_string)

    if not response: return None

    paths = {}
    response = StringIO.StringIO(string.join(response, ""))

    for event, elem in cET.iterparse(response):
        if "-path" in elem.tag:
            # Huzzah, we've found a path!
            print "Found", elem.tag, elem.text
            paths[elem.tag.split("-")[0]] = elem.text
            elem.clear()

    return paths


def info_system(server):
    """
    .. warning:: This method has not been implemented in UberCarrot yet!

    Gets system information like OS, CPU and library version numbers.

    :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
    :rtype: List
    :return: A list containing various pieces of system information.
    """
    # INFO SYSTEM
    # TODO: implement INFO SYSTEM command

    # amcp_string = "INFO SYSTEM"

    # response = self.send_command_to_caspar(server, amcp_string)
    # for r in response: print r
    # response = StringIO.StringIO(string.join(response, ""))

    # for event, elem in CET.iterparse(response):
    #    if elem.tag == "paths":
    #        print "Skipping <paths> - use INFO PATHS instead"
    #        elem.clear()
    #    else: print CET.dump(elem)

    raise NotImplementedError


def info_server(server):
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


def bye(server):
    """
    Disconnects from the server if connected remotely; if interacting directly with the console on the machine
    Caspar is running on then this will achieve the same as the KILL command.

    .. seealso:: :py:func:`caspartalk.AMCP.kill`

    :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
    :rtype: Bool
    :return: True if successful, otherwise False
    """

    # BYE

    amcp_string = "BYE"

    try:
        server.send_amcp_command(amcp_string)
    except CasparExceptions.CasparError:
        return False

    return True


def kill(server):
    """
    Shuts the server down.

    .. seealso:: :py:func:`caspartalk.AMCP.bye`

    :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
    :rtype: Bool
    :return: True if successful, otherwise False
    """
    # KILL

    amcp_string = "KILL"

    try:
        server.send_amcp_command(amcp_string)
    except CasparExceptions.CasparError:
        return False

    return True


# Data commands - create and manipulate datasets

def data_store(server, name, data):
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
        server.send_amcp_command(amcp_string)
    except CasparExceptions.CasparError:
        return False


def data_retrieve(server, name):
    """
    Returns the data saved under the name *name*.

    :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
    :param str name: The name of the dataset (saved as *name* in :py:func:`~caspartalk.AMCP.data_store`) \
    to retrieve.
    :rtype: List
    :return: A list containing the data saved under the name *name*.
    """
    # DATA RETRIEVE [name:string]

    amcp_string = "DATA RETRIEVE {name}".format(name=name)

    data = None

    try:
        data = server.send_amcp_command(amcp_string)
    except CasparExceptions.CasparError:
        return False

    return data


def data_list(server):
    """
    Returns a list of all stored datasets.

    :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
    :rtype: List
    :return: A list of all the datasets stored in CasparCG.
    """
    # DATA LIST

    amcp_string = "DATA LIST"
    data = server.send_amcp_command(amcp_string)
    return data


def data_remove(server, name):
    """
    .. warning:: Due to a bug in CasparCG Server 2.0.7 and previous, this command causes UC to hang!

    Removes the dataset saved under the name *name*.

    :param CasparServer server: The :py:class:`~caspartalk.CasparServer` that the *amcp_command* will be sent to.
    :param str name: The name of the dataset (saved as *name* in :py:func:`~caspartalk.AMCP.data_store`) \
    to remove.
    :rtype: Bool
    :return: True if successful, otherwise False.
    """

    # DATA REMOVE [name:string]
    # fixme - a bug with CCG 2.0 means this doens't work, as CCG returns a code 200, rather than 201.
    # This is fixed in CCG 2.1

    amcp_string = "DATA REMOVE {name}".format(name=name)

    try:
        server.send_amcp_command(amcp_string)
    except CasparExceptions.CasparError:
        return False

    return True


# CG Commands - manipulate Flash templates in Caspar
def cg_add(server, template, channel=1, layer=10, cg_layer=0, play_on_load=0, data=None):
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
        server.send_amcp_command(amcp_string)
    except CasparExceptions.CasparError:
        return False

    return True


def cg_play(server, channel=1, layer=10, cg_layer=0):
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
        server.send_amcp_command(amcp_string)
    except CasparExceptions.CasparError:
        return False

    return True


def cg_stop(server, channel=1, layer=10, cg_layer=0):
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
        server.send_amcp_command(amcp_string)
    except CasparExceptions.CasparError:
        return False

    return True


def cg_next(server, channel=1, layer=10, cg_layer=0):
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
        server.send_amcp_command(amcp_string)
    except CasparExceptions.CasparError:
        return False

    return True


def cg_remove(server, channel=1, layer=10, cg_layer=0):
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
        server.send_amcp_command(amcp_string)
    except CasparExceptions.CasparError:
        return False

    return True


def cg_clear(server, channel=1, layer=10):
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
        server.send_amcp_command(amcp_string)
    except CasparExceptions.CasparError:
        return False

    return True


def cg_update(server, channel=1, layer=10, cg_layer=0, data=None):
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
        server.send_amcp_command(amcp_string)
    except CasparExceptions.CasparError:
        return False

    return True


def cg_invoke(server, method, channel=1, layer=10, cg_layer=0):
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
        server.send_amcp_command(amcp_string)
    except CasparExceptions.CasparError:
        return False

    return True


def cg_info(server, channel=1, layer=10, cg_layer=0):
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
        return server.send_amcp_command(amcp_string)
    except CasparExceptions.CasparError:
        return None
