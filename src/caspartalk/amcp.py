import json
import xml.etree.cElementTree as cET
import StringIO
import string
import CasparExceptions
import CasparObjects
import casparServer


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
            else:
                print "Bad reference to", inst.attrib["type"]
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
    :rtype: :py:class:`caspartalk.casparServer.ServerConfig`
    :return: A ServerConfig containing information about the configuration of the server.
    """
    # INFO CONFIG
    # TODO: Implement info_config command

    raise NotImplementedError

    amcp_string = "INFO CONFIG"
    response = server.send_amcp_command(amcp_string)
    response = StringIO.StringIO(string.join(response, ""))

    # ==============================
    # TODO: Add CasparServer.controllers support

    cnf = casparServer.ServerConfig()

    # Let's go through the response!
    # To check the text values, we'll use the 'x in elem.text' method, rather than the 'elem.text == x' method,
    # as many of the values are whitespace-padded for readability in the XML config file.

    for event, elem in cET.iterparse(response):
        if elem.tag == "log-level":
            # <log-level>       trace [trace|debug|info|warning|error]</log-level>
            for i in casparServer.log_level:
                if str(i) in elem.tag:
                    cnf.log_level = i

            elem.clear()

        elif elem.tag == "channel-grid":
            # <channel-grid>    false [true|false]</channel-grid>
            if "true" in elem.tag:
                cnf.channel_grid = True
            else:
                cnf.channel_grid = False
            elem.clear()

        elif elem.tag == "mixer":
            # <mixer>
            #    <blend-modes>          false [true|false]</blend-modes>
            #    <straight-alpha>       false [true|false]</straight-alpha>
            #    <chroma-key>           false [true|false]</chroma-key>
            #    <mipmapping_default_on>false [true|false]</mipmapping_default_on>
            # </mixer>
            bm = elem.findtext("blend-modes")
            sa = elem.findtext("straight-alpha")
            ck = elem.findtext("chroma-key")
            mdo = elem.findtext("mipmapping_default_on")

            if bm and "true" in bm:
                cnf.mixer["blend_modes"] = True
            if sa and "true" in sa:
                cnf.mixer["straight_alpha"] = True
            if ck and "true" in ck:
                cnf.mixer["chroma_key"] = True
            if mdo and "true" in mdo:
                cnf.mixer["mipmapping_default_on"] = True
            elem.clear()

        elif elem.tag == "auto-deinterlace":
            # <auto-deinterlace>true  [true|false]</auto-deinterlace>
            if "true" in elem.text:
                cnf.auto_deinterlace = True
            else:
                cnf.auto_deinterlace = False
            elem.clear()

        elif elem.tag == "auto-transcode":
            # <auto-transcode>  true  [true|false]</auto-transcode>
            if "true" in elem.text:
                cnf.auto_transcode = True
            else:
                cnf.auto_transcode = False
            elem.clear()

        elif elem.tag == "pipeline-tokens":
            # <pipeline-tokens> 2     [1..]       </pipeline-tokens>
            try:
                cnf.pipeline_tokens = int(elem.text)
            except ValueError, e:
                print e.message
            finally:
                elem.clear()

        elif elem.tag == "template-hosts":
            # <template-hosts>
            #    <template-host>
            #        <video-mode/>
            #        <filename/>
            #        <width/>
            #        <height/>
            #    </template-host>
            # </template-hosts>
            # TODO: Support CasparServer TemplateHosts
            elem.clear()

        elif elem.tag == "flash":
            # <flash>
            #     <buffer-depth>auto [auto|1..]</buffer-depth>
            # </flash>
            buf_depth = elem.findtext("buffer-depth")
            if buf_depth and "auto" in buf_depth:
                cnf.flash["buffer_depth"] = "auto"
            elif buf_depth:  # We've got a buffer depth, but it's not 'auto'
                try:
                    cnf.flash["buffer_depth"] = int(buf_depth)
                except ValueError, e:
                    print e.message
            elem.clear()

        elif elem.tag == "thumbnails":
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
            generate_thumbnails = elem.findtext("thumbnails")
            width = elem.findtext("width")
            height = elem.findtext("height")
            video_grid = elem.findtext("video-grid")
            scan_int = elem.findtext("scan-interval-millis")
            generate_delay = elem.findtext("generate-delay-millis")
            video_mode = elem.findtext("video-mode")
            mipmap = elem.findtext("mipmap")

            if generate_thumbnails and "true" in generate_thumbnails:
                cnf.thumbnails["generate_thumbnails"] = True
            else:
                cnf.thumbnails["generate_thumbnails"] = False
            if width:
                try:
                    cnf.thumbnails["width"] = int(width)
                except ValueError, e:
                    print e.message
                    # TODO: Provide default values
            if height:
                try:
                    cnf.thumbnails["height"] = int(height)
                except ValueError, e:
                    print e.message
            if video_grid:
                try:
                    cnf.thumbnails["video_grid"] = int(video_grid)
                except ValueError, e:
                    print e.message
            if scan_int:
                try:
                    cnf.thumbnails["scan_interval_millis"] = int(scan_int)
                except ValueError, e:
                    print e.message
            if generate_delay:
                try:
                    cnf.thumbnails["generate_delay_millis"] = int(generate_delay)
                except ValueError, e:
                    print e.message
            if video_mode:
                for i in casparServer.video_mode:
                    if str(i) in elem.tag:
                        cnf.thumbnails["video_mode"] = i
            if mipmap and "true" in mipmap:
                cnf.thumbnails["mipmap"] = True
            else:
                cnf.thumbnails["mipmap"] = False

            elem.clear()

        elif elem.tag == "channel":
            # <channels>
            #   <channel>

            ch = casparServer.Channel()

            #       <video-mode> PAL [PAL|NTSC| ... ] </video-mode>
            #       <channel-layout>stereo [mono|stereo|dts|dolbye|dolbydigital|smpte|passthru]</channel-layout>
            #       <straight-alpha-output>false [true|false]</straight-alpha-output>
            #           <consumers>
            video_mode = elem.findtext("video_mode")
            chan_layout = elem.findtext("channel-layout")
            straight_alpha = elem.findtext("straight-alpha-output")
            if video_mode:
                for i in casparServer.log_level:
                    if str(i) in video_mode:
                        ch.video_mode = i
            if chan_layout:
                for i in casparServer.channel_layout:
                    if str(i) in chan_layout:
                        ch.channel_layout = i
            if straight_alpha and "true" in straight_alpha:
                ch.straight_alpha_output = True
            else:
                ch.straight_alpha_output = False

            consumers_elem = elem.find("consumers")
            if consumers_elem:
                # <decklink>
                #   <device>[1..]</device>
                #   <key-device>device + 1 [1..]</key-device>
                #   <embedded-audio>false [true|false]</embedded-audio>
                #   <channel-layout>stereo [mono|stereo|dts|dolbye|dolbydigital|smpte|passthru]</channel-layout>
                #   <latency>normal [normal|low|default]</latency>
                #   <keyer>external [external|external_separate_device|internal|default]</keyer>
                #   <key-only>false [true|false]</key-only>
                #   <buffer-depth>3 [1..]</buffer-depth>
                #   <custom-allocator>true [true|false]</custom-allocator>
                # </decklink>
                consumers_decklink = consumers_elem.findall("decklink")
                for decklink in consumers_decklink:
                    dl = casparServer.ConsumerDecklink()

                    device = decklink.findtext("device")
                    key_device = decklink.findtext("key-device")
                    embedded_audio = decklink.findtext("embedded-audio")
                    channel_layout = decklink.findtext("channel-layout")
                    latency = decklink.findtext("latency")
                    keyer = decklink.findtext("keyer")
                    key_only = decklink.findtext("key-only")
                    buffer_depth = decklink.findtext("buffer-depth")
                    custom_allocator = decklink.findtext("custom-allocator")

                    if dl.device:
                        try:
                            dl.device = int(device)
                        except ValueError, e:
                            print e.message
                            dl.device = 1
                    if dl.key_device:
                        try:
                            dl.key_device = int(key_device)
                        except ValueError, e:
                            print e.message
                            dl.key_device = 2
                    if embedded_audio and "true" in embedded_audio:
                        dl.embedded_audio = True
                    else:
                        dl.embedded_audio = False
                    if channel_layout:
                        for i in casparServer.channel_layout:
                            if str(i) in channel_layout:
                                dl.channel_layout = i
                    if latency:
                        for i in casparServer.latency:
                            if str(i) in latency:
                                dl.latency = i
                    if keyer:
                        for i in casparServer.keyer:
                            if str(i) in keyer:
                                dl.keyer = i
                    if key_only and "true" in key_only:
                        dl.key_only = True
                    else:
                        dl.key_only = False
                    if buffer_depth:
                        try:
                            dl.buffer_depth = int(buffer_depth)
                        except ValueError, e:
                            print e.message
                            dl.buffer_depth = 3
                    if custom_allocator and "true" in custom_allocator:
                        dl.custom_allocator = True
                    elif "false" in custom_allocator:
                        dl.custom_allocator = False
                    else:
                        dl.custom_allocator = True

                    ch.consumers.append(dl)
                    decklink.clear()

                # <bluefish>
                #   <device>[1..]</device>
                #   <embedded-audio>false [true|false]</embedded-audio>
                #   <channel-layout>stereo [mono|stereo|dts|dolbye|dolbydigital|smpte|passthru]</channel-layout>
                #   <key-only>false [true|false]</key-only>
                # </bluefish>
                consumers_bluefish = consumers_elem.findall("bluefish")
                for bluefish in consumers_bluefish:
                    bf = casparServer.ConsumerBluefish()

                    device = bluefish.findtext("device")
                    embedded_audio = bluefish.findtext("embedded-audio")
                    channel_layout = bluefish.findtext("channel-layout")
                    key_only = bluefish.findtext("key-only")

                    if device:
                        try:
                            bf.device = int(device)
                        except ValueError, e:
                            print e.message
                            bf.device = 1
                    if embedded_audio and "true" in embedded_audio:
                        bf.embedded_audio = True
                    else:
                        bf.embedded_audio = False
                    if channel_layout:
                        for i in casparServer.channel_layout:
                            if str(i) in channel_layout:
                                bf.channel_layout = i
                    if key_only and "true" in key_only:
                        bf.key_only = True
                    else:
                        bf.key_only = False

                    ch.consumers.append(bf)
                    bluefish.clear()

                # <system-audio></system-audio>
                consumers_sysaudio = consumers_elem.findall("system-audio")
                if consumers_sysaudio:
                    sa = casparServer.ConsumerSystemAudio()
                    ch.consumers.append(sa)


                # <screen>
                #   <device>[0..]</device>
                #   <aspect-ratio>default [default|4:3|16:9]</aspect-ratio>
                #   <stretch>fill [none|fill|uniform|uniform_to_fill]</stretch>
                #   <windowed>false [true|false]</windowed>
                #   <key-only>false [true|false]</key-only>
                #   <auto-deinterlace>true [true|false]</auto-deinterlace>
                #   <vsync>false [true|false]</vsync>
                #   <name>[Screen Consumer]</name>
                #   <borderless>false [true|false]</borderless>
                # </screen>
                consumers_screen = consumers_elem.findall("screen")
                for screen in consumers_screen:
                    sc = casparServer.ConsumerScreen()

                    device = screen.findtext("device")
                    aspect_ratio = screen.findtext("aspect-ratio")
                    stretch = screen.findtext("stretch")
                    windowed = screen.findtext("windowed")
                    key_only = screen.findtext("key-only")
                    auto_deinterlace = screen.findtext("auto-deinterlace")
                    vsync = screen.findtext("vsync")
                    name = screen.findtext("name")
                    borderless = screen.findtext("borderless")

                    if device:
                        try:
                            sc.device = int(device)
                        except ValueError, e:
                            print e.message
                            sc.device = 0
                    if aspect_ratio:
                        for i in casparServer.aspect_ratio:
                            if str(i) in aspect_ratio:
                                sc.aspect_ratio = i
                    if stretch:
                        for i in casparServer.stretch:
                            if str(i) in stretch:
                                sc.stretch = i
                    if windowed and "true" in windowed:
                        sc.windowed = True
                    else:
                        sc.windowed = False
                    if key_only and "true" in key_only:
                        sc.key_only = True
                    else:
                        sc.key_only = False
                    if auto_deinterlace and "false" in auto_deinterlace:
                        sc.auto_deinterlace = False
                    else:
                        sc.auto_deinterlace = True
                    if vsync and "true" in vsync:
                        sc.vsync = True
                    else:
                        sc.vsync = False
                    if name:
                        sc.name = name
                    else:
                        sc.name = "[Screen Consumer]"
                    if borderless and "true" in borderless:
                        sc.borderless = True
                    else:
                        sc.borderless = False

                    ch.consumers.append(sc)
                    screen.clear()

                # <newtek-ivga>
                #   <channel-layout>stereo [mono|stereo|dts|dolbye|dolbydigital|smpte|passthru]</channel-layout>
                #   <provide-sync>true [true|false]</provide-sync>
                # </newtek-ivga>
                consumers_newtek = consumers_elem.findall("newtek-ivga")
                for newtek in consumers_newtek:
                    nt = casparServer.ConsumerNewtekIVGA()

                    channel_layout = newtek.findtext("channel-layout")
                    provide_sync = newtek.findtext("provide-sync")

                    if channel_layout:
                        for i in casparServer.channel_layout:
                            if str(i) in channel_layout:
                                nt.channel_layout = i

                    if provide_sync and "false" in provide_sync:
                        nt.provide_sync = False
                    else:
                        nt.provide_sync = True

                    ch.consumers.append(nt)
                    newtek.clear()

                # <file>
                #   <path></path>
                #   <vcodec>libx264 [libx264|qtrle]</vcodec>
                #   <separate-key>false [true|false]</separate-key>
                # </file>

                consumers_file = consumers_elem.findall("file")
                for cfile in consumers_file:
                    cf = casparServer.ConsumerFile()

                    path = cfile.findtext("file")
                    vcodec = cfile.findtext("vcodec")
                    separate_key = cfile.findtext("separate-key")

                    if path:
                        cf.path = path
                    if vcodec:
                        for i in casparServer.vcodec:
                            if str(i) in vcodec:
                                cf.vcodec = i
                    if separate_key and "true" in separate_key:
                        cf.separate_key = True
                    else:
                        cf.separate_key = False

                    ch.consumers.append(cf)
                    cfile.clear()

                # <stream>
                #   <path></path>
                #   <args></args>
                # </stream>
                consumers_stream = consumers_elem.findall("stream")
                for stream in consumers_stream:
                    st = casparServer.ConsumerStream()

                    path = stream.findtext("path")
                    args = stream.findtext("args")

                    if path:
                        st.path = path

                    if args:
                        st.args = args

                    ch.consumers.append(st)
                    stream.clear()

            consumers_elem.clear()

        # <osc>
        #   <default-port>6250</default-port>
        #   <predefined-clients>
        #      <predefined-client>
        #        <address>127.0.0.1</address>
        #        <port>5253</port>
        #       </predefined-client>
        #   </predefined-clients>
        # </osc>
        elif elem.tag == "osc":
            osc = casparServer.OSC()

            default_port = elem.findtext("default-port")
            try:
                osc.default_port = int(default_port)
            except ValueError, e:
                print e.message
                osc.default_port = 6250

            predefined_clients = elem.find("predefined-client")
            for client in predefined_clients:
                addr = client.findtext("address")
                port = client.findtext("port")
                osc.predefined_clients[addr] = port

                client.clear()

            cnf.osc.append(osc)

        elif elem.tag == "audio":
            # TODO: CONTINUE
            pass



        elem.clear()


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

    if not response:
        return None

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
