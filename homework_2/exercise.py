import requests
import sys
from bs4 import BeautifulSoup, Tag
from pprint import pprint


class RosKontrolScrapper:
	"""Скраппер по продуктам росконтроля"""
	BASE_URL = 'https://roscontrol.com/category/produkti/'
	PARSER = 'html.parser'

	def __init__(self) -> None:
		self.soup = None

	@staticmethod
	def _get_html_page(url: str) -> str:
		response = requests.get(url)
		if response.ok:
			return response.text

	def _parse_html(self, html_str: str) -> None:
		self.soup = BeautifulSoup(html_str, self.PARSER)

	def _get_list_category(self) -> list[Tag]:
		container = self.soup.find(
			'div',
			attrs={
				'class': 'testlab-category'
			}
		)
		pprint(container.contents)


	def load(self) -> None:
		html_doc = self._get_html_page(self.BASE_URL)
		self._parse_html(html_doc)

	def __str__(self) -> str:
		return self.soup or 'Empty soup'



if __name__ == '__main__':
	scrapper = RosKontrolScrapper()
	scrapper.load()
	scrapper._get_list_category()
