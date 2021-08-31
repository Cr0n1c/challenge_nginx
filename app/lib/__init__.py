import datetime
import re
import socket

from urllib.parse import unquote


class NginxLogEntry:

    def __init__(self, log_parsed: re.Match) -> None:
        self.error = None
        self.log_entry = log_parsed[0]
        self.remote_addr = self.__validate_ip__(log_parsed[1])
        self.remote_user = log_parsed[2]
        self.date = self.__validate_timestamp__(log_parsed[3])
        self.http_verb = self.__validate_http_verb__(log_parsed[4])
        self.http_path = self.__validate_http_path__(log_parsed[5])
        self.http_version = log_parsed[6]
        self.http_response_code = self.__validate_response_code__(log_parsed[7])
        self.http_response_time_milliseconds = self.__validate_response_time__(log_parsed[8])
        self.user_agent_string = log_parsed[9]
    
    def __validate_http_path__(self, path: str) -> str:
        return unquote(path)

    def __validate_http_verb__(self, verb: str) -> str:
        # Mapping to RFC. Adding 'PATCH' as it was a later add and not in the supplied RFC.
        # Ref: https://datatracker.ietf.org/doc/html/rfc5789#section-2
        if verb in ['CONNECT', 'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT', 'TRACE']:
            return verb
        else:
            self.error = True
            return ''

    def __validate_ip__(self, ip_address: str) -> str:
        try:
            socket.inet_aton(ip_address)
        except socket.error:
            self.error = True
            return ''
        else:
            return ip_address
    
    def __validate_response_code__(self, code: str) -> str:
        # Mapping to RFC
        try:
            if int(code) not in range(100, 600):
                raise ValueError 
        except ValueError:
            self.error = True
            return ''
        else:
            return code
    
    def __validate_response_time__(self, response_time: str) -> int:
        try:
            if int(response_time) < 0:
                raise ValueError
        except ValueError:
            self.error = True
            return ''
        else:
            return int(response_time)

    def __validate_timestamp__(self, timestamp: str) -> str:
        # Regex for common log format datetime
        try:
            datetime.datetime.strptime(timestamp, '%d/%b/%Y:%H:%M:%S %z')
        except ValueError:
            self.error = True
            return ''
        else:
            return timestamp
