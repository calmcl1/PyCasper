class CasparObject:
    """
    A generic CasparCG Object.
    It is unlikely that there will be a need to instantiate this directly; use Template or Media instead.

    Likely to either be a template or a media file.
    """

    def __init__(self):
        pass


class Template(CasparObject):
    """
    Holds all the information about a template; this information is returned by CasparCG on a successful INFO TEMPLATE
    command.

    :param str file_name: The name of the template file (including directory, relative to the CasparCG templates \
    folder).

    The *components* variable will hold a Dict of the form::

        { name : { property : value, ... } }

    For example::

        { "CasparTextField" : { "name" : "text",
                                "type" : "string",
                                "info" : "string data"
                                } }


    The *instances* variable will hold a Dict of the form::

        { name : type, ... }

    For example::

        { "f1" : "CasparTextField" ,
            "f2": "CasparTextField"
        }


    The *parameters* variable will hold a Dict of the form::

        { id : { parameters : value, ... } }

    For example::

        { "time"  : { "type" : "int",
                      "info" : "The time to count down in seconds" },
          "image" : { "type" : "string",
                      "info" : "The path to the image to load" }
        }
    """

    def __init__(self, file_name):
        CasparObject.__init__(self)

        self.file_name = file_name
        self.version = None
        self.author_name = None
        self.author_email = None
        self.template_info = None
        self.original_height = 0
        self.original_width = 0
        self.original_frame_rate = 0
        self.components = {}
        self.keyframes = []
        self.instances = {}
        self.parameters = {}

    def check_exists(self):
        pass

    def retrieve_info(self):
        pass

    def get_parameters(self):
        pass


class Media(CasparObject):

    def __init__(self):
        CasparObject.__init__(self)