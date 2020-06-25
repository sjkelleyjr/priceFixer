import numpy as np
import json

class StreamingMeanAndVariance:
    # store these as variables in a ddb table for a unique element.
    # could eventually do a sliding K window to adapt quicker, for now let's just use the naive approach to see
    # if this thing even works.
    def __init__(self, mean = 0, variance = 0, n_elements = 0):
        self.mean = 0
        self.variance = 0
        self.n_elements = 0

    def update(self, element):
        self.variance = ((self.variance + self.mean ** 2) * self.n_elements + element ** 2) / (self.n_elements + 1)
        self.mean = ((self.mean * self.n_elements) + element) / (self.n_elements + 1)
        self.variance = self.variance - self.mean ** 2
        self.n_elements += 1

m = StreamingMeanAndVariance()
n = 10000

if __name__ == '__main__':

    with open('./db.json') as f:
      data = json.load(f)

    #check if this item exists first, it does, check it's "outlierness" and update the values, otherwise simply write them to the file.
    

    #read the price for the unique element
    for i, s in enumerate(np.random.randn(n)):
        #greater than 3 std from the mean is an outlier.
        if not - 3 <= (s - m.mean) / np.sqrt(m.variance) <= 3:
            #an outlier
            print(i, s)
        m.update(s)

    item = {}
    item["mean"] = m.mean
    item["variance"] = m.variance
    item["n_elements"] = m.n_elements
    data["my_fake_item"] = item
    print(json.dumps(data))

    with open('./db.json', 'w') as json_file:
        json.dump(data, json_file)


