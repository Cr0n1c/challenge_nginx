import datetime
import ipaddress

from urllib.parse import unquote


def validate_entry(entry: dict) -> dict:
    ''' Validation function for key fields in an Nginx Log Entry
    
        Parameters
        ----------
        entry: NginxLogEntry
            dictionary containing the raw field entries
        
        Return
        ------
        NginxLogEntry
            dictionary containing the validated and standardized field entries
            If 'False' is returned, that means the dictionary had an invalid entry
    '''

    # Validating remote_addr
    entry['remote_addr'] = validate_ip_address(entry['remote_addr'])
    if not entry['remote_addr']:
        return False
    
    # Validating date against common log format regex
    try:
        datetime.datetime.strptime(entry['date'], '%d/%b/%Y:%H:%M:%S %z')
    except ValueError:
        return False

    # Mapping http_verb to RFC. Adding 'PATCH' as it was a later add and not in the supplied RFC.
    # Ref: https://datatracker.ietf.org/doc/html/rfc5789#section-2
    if not entry['http_verb'] in ['CONNECT', 'DELETE', 'GET', 'HEAD', 'OPTIONS', 'PATCH', 'POST', 'PUT', 'TRACE']:
        return False

    # Standardizing http_path output to support URL encoding
    entry['http_path'] = unquote(entry['http_path']).split('?')[0]

    # Validating http_response_code is an integer between 100 and 599
    try:
        if int(entry['http_response_code']) not in range(100, 600) or len(entry['http_response_code']) != 3:
            raise ValueError 
    except ValueError:
        return False
    
    # Casting http_response_time_milliseconds to int to support math operations later
    try:
        entry['http_response_time_milliseconds'] = int(entry['http_response_time_milliseconds'])
        if entry['http_response_time_milliseconds'] < 0:
            raise ValueError
    except ValueError:
        return False

    return entry
        

def validate_ip_address(address: str) -> str:
    ''' Basic IP validation and standardization function
    
        Parameters
        ----------
        address: str
            an IPv4 or an IPv6 address in human readable form. This address can be short hand
            or long hand.

        Return
        ------
        IPAddress
            an IPv4 or an IPv6 address in human readable form in short hand (if possible)
            If 'False' is returned then the input was not a valid IPv4 or IPv6 address
    '''

    try:
        ip_int = int(ipaddress.ip_address(address))
    except:
        return False
    else:
        return str(ipaddress.ip_address(ip_int))

