def interpret_response(caspar_output):
    r = caspar_output[0]
    print r
    if r.startswith("100"): return parse_100()
    elif r.startswith("101"): return parse_101()
    elif r.startswith("200"): return parse_200()
    elif r.startswith("201"): return parse_201()
    elif r.startswith("202"): return parse_202()
    elif r.startswith("400"): return parse_400()
    elif r.startswith("401"): return parse_401()
    elif r.startswith("402"): return parse_402()
    elif r.startswith("403"): return parse_403()
    elif r.startswith("404"): return parse_404()
    elif r.startswith("500"): return parse_500()
    elif r.startswith("501"): return parse_501()
    elif r.startswith("502"): return parse_502()
    elif r.startswith("600"): return parse_600()

# RETURN FORMATTING
# Each of the following must return a tuple of the format:
# ( status_message, returns_more_data, [final_delimiter] ), where:
#
# status_message    is exactly that - it might just be wise to return the line from Caspar
# returns_more_data is a flag to suggest that the command returns a list, and that
#                   there's more to come.
# final_delimiter   is the character sequence that signals the end of the message, if
#                   returns_more_data is true. Sometimes this is \r\n, sometimes \r\n\r\n

# 100s: Information
def parse_100():
    # 100 [action] - Information about an event.
    raise NotImplementedError


def parse_101():
    # 101 [action] - Information about an event. A line of data is being returned.
    raise NotImplementedError


# 200s: Successful
def parse_200():
    # 200 [command] OK	- The command has been executed and several lines of data
    # (seperated by \r\n) are being returned (terminated with an additional \r\n)
    return "200 OK", True, "\r\n\r\n"


def parse_201():
    # 201 [command] OK	- The command has been executed and data (terminated by \r\n)
    # is being returned.
    return "201 OK", True, "\r\n"


def parse_202():
    # 202 [command] OK	- The command has been executed.
    return "202 OK", False


# 400s: Client Error
def parse_400():
    # 400 ERROR	- Command not understood
    raise NotImplementedError


def parse_401():
    # 401 [command] ERROR	- Illegal video_channel
    raise NotImplementedError


def parse_402():
    # 402 [command] ERROR	- Parameter missing
    raise NotImplementedError


def parse_403():
    # 403 [command] ERROR	- Illegal parameter
    raise NotImplementedError


def parse_404():
    # 404 [command] ERROR	- Media file not found
    raise NotImplementedError


# 500s: Server Error
def parse_500():
    # 500 FAILED	- Internal server error
    raise NotImplementedError


def parse_501():
    # 501 [command] FAILED	- Internal server error
    raise NotImplementedError


def parse_502():
    # 502 [command] FAILED	- Media file unreadable
    raise NotImplementedError


def parse_600():
    # 600 Not Implemented
    raise NotImplementedError
