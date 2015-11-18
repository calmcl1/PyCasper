class CasparListener:
    def __init__(self):
        raise NotImplementedError

    def parse_caspar_stdout(self, caspar_output):
        raise NotImplementedError

    # 100s: Information
    def parse_100(self):
        # 100 [action] - Information about an event.
        raise NotImplementedError

    def parse_101(self):
        # 101 [action] - Information about an event. A line of data is being returned.
        raise NotImplementedError

    # 200s: Successful
    def parse_200(self):
        # 200 [command] OK	- The command has been executed and several lines of data
        # (seperated by \r\n) are being returned (terminated with an additional \r\n)
        raise NotImplementedError

    def parse_201(self):
        # 201 [command] OK	- The command has been executed and data (terminated by \r\n)
        # is being returned.
        raise NotImplementedError

    def parse_202(self):
        # 202 [command] OK	- The command has been executed.
        raise NotImplementedError

    # 400s: Client Error
    def parse_400(self):
        # 400 ERROR	- Command not understood
        raise NotImplementedError

    def parse_401(self):
        # 401 [command] ERROR	- Illegal video_channel
        raise NotImplementedError

    def parse_402(self):
        # 402 [command] ERROR	- Parameter missing
        raise NotImplementedError

    def parse_403(self):
        # 403 [command] ERROR	- Illegal parameter
        raise NotImplementedError

    def parse_404(self):
        # 404 [command] ERROR	- Media file not found
        raise NotImplementedError

    # 500s: Server Error
    def parse_500(self):
        # 500 FAILED	- Internal server error
        raise NotImplementedError

    def parse_501(self):
        # 501 [command] FAILED	- Internal server error
        raise NotImplementedError

    def parse_502(self):
        # 502 [command] FAILED	- Media file unreadable
        raise NotImplementedError

    def parse_600(self):
        # 600 Not Implemented
        raise NotImplementedError