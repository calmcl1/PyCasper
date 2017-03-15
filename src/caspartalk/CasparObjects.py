import types
import collections
import amcp

CasparTypes = {"string": types.StringType,
               "int": types.IntType,
               "number": types.FloatType,
               "boolean": types.BooleanType}


class CasparObject(object):
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

    The *components* variable will hold a :py:class:`~caspartalk.CasparObjects.TypedDict` containing
    another TypedDict, containing :py:class:`~caspartalk.CasparObjects.ComponentProperty` s.
    This is because a component is simply a collection of properties. It would be overly complicated to create a new
    ``TemplateComponent`` class, which would only contain one variable, holding a collection of properties - especially
    since the component's properties can be accessed simply via ``Template.components[component-id][property-id]``.


    The *instances* variable will hold a Dict of the form::

        { name : type, ... }

    For example::

        { "f1" : "CasparTextField" ,
            "f2": "CasparTextField"
        }


    The *parameters* variable will hold a :py:class:`~caspartalk.CasparObjects.TypedDict` containing
    :py:class:`~caspartalk.CasparObjects.TemplateParameter` s.

    :param str file_name: The name of the template file (including directory, relative to the CasparCG templates \
    folder).
    :param casparServer owner_server: The server that the template exists on.

    """

    def __init__(self, owner_server, file_name):
        CasparObject.__init__(self)

        self.file_name = file_name  # The name of the file + relative directory to CCG templates folder
        self.owner_server = owner_server  # The server that the template exists on

        self.version = None
        self.author_name = None
        self.author_email = None
        self.template_info = None
        self.original_height = 0
        self.original_width = 0
        self.original_frame_rate = 0
        # A component is just a named collection of properties
        self.components = TypedDict(TypedDict)
        self.keyframes = []
        self.instances = {}
        self.parameters = TypedDict(TemplateParameter)

    def __repr__(self):
        return str(type(self).__name__ + " " + self.file_name)


class TemplateParameter(object):
    """
    A TemplateParameter represents a Parameter that a CCG Template can accept. This is essentially a variable within
    the Template that can be set from a CCG client. Different Templates will accept different Parameters, or none at
    all.

    :param param_id: The ID of the parameter within the Template.
    :param param_type: The data type that *param_value* must be.
    :param param_info: A string containing information describing the Parameter.
    :param param_value: The value of the parameter, of type *param_type*.

    """

    def __init__(self, param_id, param_type, param_info, param_value=None):
        self.id = param_id

        if param_type in CasparTypes.keys():
            self.type = CasparTypes[param_type]
        elif param_type in CasparTypes.values():
            self.type = param_type
        else:
            raise ValueError("'{wrong}' is not a valid Caspar Type {types})".format(wrong=param_type),
                             types=CasparTypes.keys())

        self.info = param_info
        self._value = None
        if param_value:
            self.set_value(param_value)

    def set_value(self, param_value):
        expected_type = self.type
        if isinstance(param_value, expected_type):
            self._value = param_value
        else:
            raise TypeError(
                    "Expected {value} to be of type {correct_type}; got {wrong_type} instead".format(value=param_value,
                                                                                                     correct_type=expected_type,
                                                                                                     wrong_type=type(
                                                                                                             param_value)))

    def get_value(self):
        return self._value

    value = property(get_value, set_value)

    def __repr__(self):
        return str(type(self).__name__)


class ComponentProperty(object):
    """
    A ComponentProperty is simply a Property of a Component in a CCG Template.
    Components are simply collections of Properties.

    :param data_id: The name of the property.
    :param data_type: The type of the value of the property.
    :param data_info: The string containing information about the property.
    :param data_value: The value of the property, of type *data_type*.
    """

    def __init__(self, data_id, data_type, data_info, data_value=None):
        self.id = data_id

        if data_type in CasparTypes.keys():
            self.type = CasparTypes[data_type]
        elif data_type in CasparTypes.values():
            self.type = data_type
        else:
            raise ValueError("'{wrong}' is not a valid Caspar Type {types})".format(wrong=data_type),
                             types=CasparTypes.keys())

        self.info = data_info
        self._value = None
        if data_value:
            self.set_value(data_value)

    def set_value(self, data_value):
        expected_type = self.type
        if isinstance(data_value, expected_type):
            self._value = data_value
        else:
            raise TypeError(
                    "Expected {value} to be of type {correct_type}; got {wrong_type} instead".format(value=data_value,
                                                                                                     correct_type=expected_type,
                                                                                                     wrong_type=type(
                                                                                                             data_value)))

    def get_value(self):
        return self._value

    value = property(get_value, set_value)

    def __repr__(self):
        return str(type(self).__name__)


class TypedDict(collections.MutableMapping):
    """
    A TypedDict is what it sounds like - a normal Dict, but with the setter overridden so that the key is as normal,
    just a string, but the value is checked to make sure that it is a certain type before it is added to the Dict,
    so as to ensure that the values stored can safely be expected to be of a certain type.

    :param value_type: The permissible type of values to be stored in the TypedDict.
    """

    def __init__(self, value_type, *args, **kwargs):
        self.store = dict()
        # dict.__init__(dict(), *args, **kwargs)
        self.store.update(*args, **kwargs)

        if isinstance(value_type, TypedDict):
            value_type = TypedDict
        elif not isinstance(value_type, types.TypeType):
            raise TypeError("value_type is not a type, got {arg} instead".format(arg=type(value_type)))

        self._value_type = value_type

    def __getitem__(self, key):
        return self.store[key]

    def __setitem__(self, key, value):
        if not isinstance(value, self.value_type):
            raise TypeError("{value} is not a {type}.".format(value=value, type=self.value_type))
        self.store[key] = value

    def __delitem__(self, key):
        del self.store[key]

    def __iter__(self):
        return iter(self.store)

    def __len__(self):
        return len(self.store)

    def get_value_type(self):
        return self._value_type

    value_type = property(get_value_type)
