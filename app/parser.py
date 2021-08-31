import argparse
import json
import os
import re
import sys

from pathlib import Path
from typing import NewType

from lib import NginxLogEntry

ParserResults = NewType('ParserResults', dict)


def out_to_json_file(data: dict, output_file: str) -> bool:
    try:
        with open(output_file, 'w') as f:
            print(json.dumps(data, indent=2), file=f)
    except Exception as e:
        print(e)
        return False
    else:
        return True


def parse_nginx_log(arguments: argparse.Namespace) -> ParserResults:
    nginx_ips = {}
    url_load_times = {}

    results = {
        'total_number_of_lines_processed': 0,
        'total_number_of_lines_ok': 0,
        'total_number_of_lines_failed': 0,
        'top_client_ips': {},
        'top_path_avg_seconds': {}
    }

    # Basic regex to ensure that we have the correct amount of fields with extremely basic pattern matching
    # We will do the more advanced checks later. This is to clear the low hanging fruit.
    pattern = '^(\d+\.\d+\.\d+\.\d+) - (.*?) \[(.*?)\] "(.*?) (.*?) (HTTP/\d\.\d)" ([1-5]\d{2}) (\d+) "(.*)"$'
    compiled_pattern = re.compile(pattern)

    for entry in open(arguments.input_file):
        # Start of processing for each new log entry
        results['total_number_of_lines_processed'] += 1
        parsed_entry = compiled_pattern.match(entry)

        # Error handling to ensure the entry passed basic regex checks
        if not bool(parsed_entry):
            results['total_number_of_lines_failed'] += 1
            continue
        
        # More sufficsticated validation for the log entry
        log_object = NginxLogEntry(parsed_entry)
        if log_object.error == True:
            results['total_number_of_lines_failed'] += 1
            continue
        
        # All our checks our completed and we have an 'ok' line
        results['total_number_of_lines_ok'] += 1

        # Counting the customer ip addresses
        if nginx_ips.get(log_object.remote_addr):
            nginx_ips[log_object.remote_addr] += 1
        else:
            nginx_ips[log_object.remote_addr] = 1

        # Determining average load times for pages
        if url_load_times.get(log_object.http_path):
            url_load_times[log_object.http_path]['count'] += 1
            url_load_times[log_object.http_path]['total_ms_load_time'] += log_object.http_response_time_milliseconds
        else:
            url_load_times[log_object.http_path] = {
                'count': 1,
                'total_ms_load_time': log_object.http_response_time_milliseconds
            }
                
    # Iterating through remote_addr of 'ok' lines to get our top client ips
    results['top_client_ips'] = {k: v for k, v in sorted(nginx_ips.items(), 
        key=lambda x: x[1], reverse=True)[0:arguments.top_client_ips]}
    nginx_ips = None # Freeing up memory

    # Setting average load times per http_path
    average_load_times = {k: round(v['total_ms_load_time'] / v['count'] / 1000, 2) for k, v in url_load_times.items()}
    url_load_times = None # Freeing up memory

    # Setting top_path_avg_seconds of 'ok' lines to get our top path average times
    results['top_path_avg_seconds'] = {k: v for k, v in sorted(average_load_times.items(), 
        key=lambda x: x[1], reverse=True)[0:arguments.top_path_avg_seconds]}
    average_load_times = None # Freeing up memory

    return results


if __name__ == '__main__':
    # Parsing from CLI
    parser = argparse.ArgumentParser(
        add_help=True,
        description='chunk-o-lytics nginx log parse and extractor'
    )
    parser.add_argument(
        '--in',
        dest='input_file',
        help='[Required] Input file to be parsed',
        required=True
    )
    parser.add_argument(
        '--out',
        dest='output_file',
        help='[Required] Output JSON file',
        required=True
    )
    parser.add_argument(
        '--max-client-ips',
        choices=range(0, 10001),
        default=10,
        dest='top_client_ips',
        help='Defines the maximum number of results to output in the top_client_ips field. ' + 
             'Defaults to 10 if not provided. Choices are integers between 0 and 100.',
        metavar='[Choices are integers between 0 and 10000]',
        type=int
    )
    parser.add_argument(
        '--max-paths',
        choices=range(0, 10001),
        default=10,
        dest='top_path_avg_seconds',
        help='Defined the maximum number of results to output on the top_path_avg_seconds field. ' +
             'Defaults to 10 if not provided.',
        metavar='[Choices are integers between 0 and 10000]',
        type=int
    )

    # Error handling for required fields check and input_file
    try:
        arguments = parser.parse_args()

        if not os.path.isfile(arguments.input_file):
            print(f'FileNotFoundError: [Errno 2] [--in] must contain a valid filepath: {arguments.input_file}')
            raise OSError
    except (SystemExit, OSError):
        parser.print_help()
        sys.exit(1)
    
    # Error control for ensuring that we can write to the output_file
    try:
        Path(os.path.dirname(arguments.output_file)).mkdir(parents=True, exist_ok=True)
        Path(arguments.output_file).touch()
    except OSError as e:
        print(f'OSError: [Errno {e.errno}] [--out] failed to access {arguments.output_file}')
        sys.exit(1)
    except PermissionError as e:
        print(e.args[-1])
        sys.exit(1)
    
    # Running parser logic
    if not out_to_json_file(parse_nginx_log(arguments), arguments.output_file):
        sys.exit(2)

