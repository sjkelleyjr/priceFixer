import numpy as np
import json
from json import JSONDecodeError
from math import sqrt
import requests
from amadeus import Client, ResponseError
from country_list import countries
from amadeus_keys import *

class file_writer:
    def __init__(self, filename):
        self.filename = filename
        with open(self.filename, 'r+') as f:
            try:
                self.data = json.load(f)
            except JSONDecodeError:
                print('file wasn\'t valid JSON, using an empty dict instead.')
                self.data = {}

    def upsert(self, item_id, payload):
        self.data[item_id] = payload
        self.flush_to_disk()

    def push_to_list(self, item_id, payload):
        if item_id in self.data:
            self.data[item_id].append(payload)
        else:
            self.data[item_id] = [payload]
        self.flush_to_disk()

    def get(self, item_id):
        return self.data[item_id] if item_id in self.data else None

    def flush_to_disk(self):
        with open(self.filename, 'w') as json_file:
            json.dump(self.data, json_file)

class stat_manager:
    def __init__(self, accessor):
        self.accessor = accessor

    def get_sd(self, item_id, price):
        item_stats = self.accessor.get(item_id)
        if item_stats is None:
            return None
        if item_stats['variance'] < 0 or item_stats['variance'] is None:
            print(f'variance ({item_stats["variance"]}) is negative or None, returning None for now.')
            return None
        if sqrt(item_stats['variance']) == 0:
            print('The variance is 0, which implies all of the numbers have been the same or we\'ve only seen 1 number')
            # if we've seen 5 elements assume they've all just been the same, in which case if we see a number different then these it's likely an outlier.
            # TODO make this configurable, who knows if this is the appropriate number for real data.
            if item_stats['n_elements'] > 5:
                return (price - item_stats['mean'])
            else:
                return float('NaN')
        else:
            return (price - item_stats['mean']) / sqrt(item_stats['variance'])

    def put_price(self, item_id, price):
        payload = {}
        item_stats = self.accessor.get(item_id)
        if item_stats is None:
            payload['mean'] = price
            payload['variance'] = 0
            payload['n_elements'] = 1
        else:
            (new_mean, new_variance, new_n) = self.update_stats(item_stats, price)
            payload['mean'] = new_mean
            payload['variance'] = new_variance
            payload['n_elements'] = new_n
        self.accessor.upsert(item_id, payload)

    def update_stats(self, current_stats, price):
        intermediate_variance = ((current_stats['variance'] + current_stats['mean'] ** 2) * current_stats['n_elements'] + price ** 2) / (current_stats['n_elements'] + 1)
        new_mean = ((current_stats['mean'] * current_stats['n_elements']) + price) / (current_stats['n_elements'] + 1)
        new_variance = intermediate_variance - new_mean ** 2
        new_n = current_stats['n_elements'] + 1
        return (new_mean, new_variance, new_n)

#just a test to see if we can detect the outliers in a normal distribution.
def testSM(sm):
    for i, s in enumerate(np.random.randn(10000)):
        item_id = i % 100
        sd = sm.get_sd(str(item_id), s)
        if sd is not None and sd < -3:
            print(f'low price outlier detected! sd: {sd}, item_id: {item_id}, s: {s}')
        sm.put_price(str(item_id), s)

if __name__ == '__main__':

    fr = file_writer('test.json')
    outliers = file_writer('outliers.json')
    sm = stat_manager(fr)


    amadeus = Client(
        client_id = amadeus_dev_client_id,
        client_secret = amadeus_dev_client_secret
    )

    for country in countries:
        location, airport_code = (''.join(country.split(' ')[0:1]), country.split(' ')[-1].replace('(', '').replace(')', ''))
        try:
            #these can definitely be parallelized if necessary
            response = amadeus.shopping.flight_offers_search.get(
                originLocationCode='SEA',
                destinationLocationCode=airport_code,
                departureDate='2020-10-01',
                adults=1)
        except ResponseError as error:
            print(error)
        print(f'{len(response.data)} flights returned for {country} ({airport_code})')
        # if len(response.data) > 0:
        #     # could be one-way, need to consider that
        #     print(f'first is {response.data[0]}')

        price_list = []
        for payload in response.data:
            flight_ids = []
            for segment in payload['itineraries'][0]['segments']:
                flight_ids.append(':'.join((segment['carrierCode'],segment['number'])))
            price_list.append((payload['price']['grandTotal'], '-'.join(flight_ids)))
        price_list.sort(reverse = True, key=lambda tup: tup[0])

        for price in price_list:
            sd = sm.get_sd(airport_code, float(price[0]))
            if sd is not None and sd < -3:
                print(f'potential outlier detected | flight_ids: {price[1]}, price: {price[0]}, sd: {sd}')
                outlier_data = {}
                outlier_data['flight_ids'] = price[1]
                outlier_data['price'] = price[0]
                outlier_data['std_dev'] = sd
                outliers.push_to_list(airport_code, outlier_data)
            sm.put_price(airport_code, float(price[0]))


    # try:
    #     response = amadeus.shopping.flight_offers_search.get(
    #         originLocationCode='SEA',
    #         destinationLocationCode='anywhere',
    #         departureDate='2020-10-01',
    #         adults=1)
    #     for payload in response.data:
    #         print(payload['price'])
    # except ResponseError as error:
    #     print(error)


    #TODO: scrape some data off the airlines every day in Seattle (do they have an API or do we have to scrape the page?)
    #let's start with only 1 airline for now, say Delta, and leave it running for a month or so and analyze the results.
    #need to deploy this code to the pi so it can run on a cron every day.



