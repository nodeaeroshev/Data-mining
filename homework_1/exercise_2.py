import os
import requests
import json
from pprint import pprint


class VKScrapper:
	VK_API_URL = 'https://api.vk.com/'

	def __init__(self) -> None:
		self.ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
		self.APP_ID = os.environ.get('APP_ID')

	def get_groups(self):
		response = requests.get(f'{self.VK_API_URL}method/groups.get/?v=5.81&access_token={self.ACCESS_TOKEN}')
		if response.ok:
			return response.json()


if __name__ == '__main__':
	data_groups = VKScrapper().get_groups()
	pprint(data_groups)
	with open('groups.json', 'w') as file:
		json.dump(data_groups, file, indent=2)
