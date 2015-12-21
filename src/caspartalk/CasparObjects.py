import AMCP
import Template
import Media

CasparTypes = {"string": str,
               "int": int}


class CasparObject:
    """
    A generic CasparCG Object.
    It is unlikely that there will be a need to instantiate this directly; use Template or Media instead.

    Likely to either be a template or a media file.
    """

    def __init__(self):
        pass
