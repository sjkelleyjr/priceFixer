import json

with open('outliers.json', 'r+') as f:
	data = json.load(f)
	for key in data:
		for outlier_data in data[key]:
			# if float(outlier_data['price']) < 200:
			print(key, outlier_data)