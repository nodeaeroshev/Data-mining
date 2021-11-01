import requests
import sys
import json


class GetRequestError(Exception):
	def __init__(self, message: str, errors: str):
		super().__init__(message)
		self.errors = errors


class GitHubScrapper:
	"""Скрапер для сбора данных с GitHub"""
	BASE_URL = 'http://api.github.com/'

	def get_info_user(self, username: str) -> dict:
		response = requests.get(f'{self.BASE_URL}users/{username}')
		if response.ok:
			return response.json()
		raise GetRequestError('Error occured while get info users')

	def get_info_repo_user(self, url_repos: str) -> list[dict]:
		if url_repos is None:
			raise GetRequestError('Invalid URL')
		response = requests.get(url_repos)
		if response.ok:
			return response.json()
		raise GetRequestError('Error occured while get info repos of user')

	def save_in_file(self, username: str, data: list[dict]) -> None:
		with open(f'{username}.json', 'w') as file:
			json.dump(data, file, indent=2)

	def scrapping_github(self, username: str) -> str:
		try:
			user_data = self.get_info_user(username)
			repos_data = self.get_info_repo_user(user_data.get('repos_url'))
		except GetRequestError as e:
			return e
		self.save_in_file(username, repos_data)
		return 'Done!'


if __name__ == '__main__':
	try:
		_, username = sys.argv
	except ValueError as e:
		print(e)
	else:
		scrapper = GitHubScrapper()
		info_res = scrapper.scrapping_github(username)
		print(info_res)
