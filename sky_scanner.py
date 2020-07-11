#NOTE: couldn't get a skyscanner API key :(, so this code is largely useless.
SKY_SCANNER_API_KEY = 'abcdefg'

class sky_scanner:
    def __init__(self, api_endpoint):
        self.api_endpoint = api_endpoint
    def browse_quotes(self, 
        country, 
        currency, 
        locale, 
        originPlace,
        destinationPlace,
        outboundPartialDate,
        inboundPartialDate):
        endpoint_suffix = '/'.join(['browsequotes', 
            'v1.0', 
            country,
            currency,
            locale,
            originPlace,
            destinationPlace,
            outboundPartialDate,
            inboundPartialDate
        ])
        browse_endpoint = self.api_endpoint + endpoint_suffix + f'?apiKey={SKY_SCANNER_API_KEY}'
        print(browse_endpoint)
        print(requests.get(browse_endpoint).json())


    #TODO: need an API key for the skyscanner API so I can see what format the various params need to be in
    # for example, does the locale need to be a dict, or is the locale code sufficient? 
    # (seems like the code should be sufficient but I can't test this assumption without a key)
    # if it *is* a dict, we need to use this API to see what the locale for US
    # print(requests.get(f'https://partners.api.skyscanner.net/apiservices/reference/v1.0/locales?apiKey={SKY_SCANNER_API_KEY}').json())

    # ss = sky_scanner('https://partners.api.skyscanner.net/apiservices/')
    #/{country}/{currency}/{locale}/
    #{originPlace}/
    #{destinationPlace}/
    #{outboundPartialDate}/
    #{inboundPartialDate}
    # ss.browse_quotes('US', 'USD', 'EN', 'SEA', 'anywhere', 'anytime', 'anytime')