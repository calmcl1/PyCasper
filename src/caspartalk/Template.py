from CasparObjects import *


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

        self.file_name = file_name  # The name of the file + relative directory to CCG templates folder
        self.owner_server = None  # The server that the template exists on

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
        self.parameters = ParameterDict()

    def check_exists(self):
        """
        .. warning:: This method has not been implemented in UberCarrot yet!

        Confirms that this template exists on the server.

        :return:
        """

        # TODO: implement caspartalk.CasparObjects.Template.check_exists()
        raise NotImplementedError

    def retrieve_info(self):
        """
        .. warning:: This method has not been implemented in UberCarrot yet!
        """

        # TODO: implement caspartalk.CasparObjects.Template.retrieve_info()

        response = AMCP.info_template(self.owner_server, self.file_name)

        raise NotImplementedError

    def get_parameters(self):
        """
        .. warning:: This method has not been implemented in UberCarrot yet!

        :return:
        """
        # TODO: implement caspartalk.CasparObjects.Template.get_parameters()
        raise NotImplementedError


class TemplateParameter(object):
    """

    """

    def __init__(self, param_id, param_type, param_info, param_value=None):
        self.id = param_id
        self.type = param_type
        self.info = param_info
        self._value = None
        if param_value:
            self.set_value(param_value)

    def set_value(self, param_value):
        expected_type = CasparTypes[self.type]
        if isinstance(param_value, expected_type):
            self._value = param_value
        else:
            raise TypeError("Expected {value} to be of type {correct_type}; got {wrong_type} instead".format(value=param_value,
                                                                                                   correct_type=expected_type,
                                                                                                   wrong_type=type(
                                                                                                       param_value)))

    def get_value(self):
        return self._value

    value = property(get_value, set_value)

    def __repr__(self):
        return str(self.get_value())


class ParameterDict(dict):

    def __init__(self, *args):
        dict.__init__(self, *args)

    def __setitem__(self, key, value):
        if key in self.keys():
            # We already have a TemplateParameter of this name in the collection
            self.get(key).value = value

        else:
            if not isinstance(value, TemplateParameter):
                raise TypeError("{value} is not a TemplateParameter.".format(value=value))

            dict.__setitem__(self, key, value)

