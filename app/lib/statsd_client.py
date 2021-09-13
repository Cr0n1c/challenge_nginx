import os 

import statsd


def start_client() -> statsd.StatsClient:
    ''' Function to instatiate a statsd session. 

        Notes: This function requires an extrenal library called 'statsd'
               Please install via pip prior to running this function in standalone
               'pip install statsd' 
        
        Parameters
        ----------
        prefix: str (optional)
            This is the prefix for any metric that you send. If no prefix value is supplied
            then this defaults to 'metric'.

        Return
        ------
        statsd.StatsClient
            Use this object to pass data to a statsd server.
            Ref: https://statsd.readthedocs.io/en/v3.3/
    '''

    statsd_server = os.getenv('STATSD_SERVER').split(':')

    return statsd.StatsClient(host=statsd_server[0], 
                              port=statsd_server[1],
                              prefix='metric'
    )

