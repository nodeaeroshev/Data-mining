"""В этом задании необходимо поставить third-party библиотеку unidecode, она заметно упрощает работу с UNICODE"""
import json
from itertools import chain

import requests
from bs4 import BeautifulSoup, Tag
from unidecode import unidecode


class DataClass:
    """Контейнер для собранных данных"""

    def __init__(self, **kwargs) -> None:
        for name, value in kwargs.items():
            setattr(self, name, value)

    def __str__(self) -> str:
        return json.dumps(self.__dict__, indent=2)


class DataClassEncoder(json.JSONEncoder):
    """Энкодер для сериализации в формат JSON"""

    def default(self, obj):
        return obj.__dict__


class HHPythonScrapper:
    """Скраппер по вакансиям Python сайта hh.ru"""
    BASE_URL = 'https://hh.ru/search/vacancy'
    QUERY_PARAMS = {
        "area": 1,
        "fromSearchLine": True,
        "text": "python"
    }
    HEADERS = {
        "User-Agent": "Custom"
    }
    PARSER = 'html.parser'
    STORAGE = 'soup.html'

    def __init__(self) -> None:
        self.soup = None  # type: BeautifulSoup | None

    @staticmethod
    def _get_html_page(url: str, headers: dict, query_params: dict) -> str | None:
        """Ходим получить HTML страницу"""
        response = requests.get(url, headers=headers, params=query_params)
        if response.ok:
            with open(HHPythonScrapper.STORAGE, 'w') as file:
                file.write(response.text)
            return response.text
        # else:
        #   with open (HHPythonScrapper.STORAGE, 'r') as file:
        #       return file.read()

    def _parse_html(self, html_str: str) -> None:
        """Парсим HTML строку в объект BS"""
        if html_str is None:
            raise RuntimeError('Empty html')
        self.soup = BeautifulSoup(html_str, self.PARSER)

    def _get_list_category(self) -> list[Tag]:
        """Получить список вакансий (в списке также попадаются рекламные баннеры)"""
        return self.soup.find(
            'div',
            attrs={
                'class': 'vacancy-serp',
                'data-qa': 'vacancy-serp__results'
            }
        ).contents

    def _decompose_div(self, tag: Tag) -> DataClass:
        """Разложить DIV вакансии по составляющим"""
        if 'vacancy-serp-item' in tag.attrs.get('class', []):
            vacancy_name, vacancy_ref = self._find_vacancy_name_ref(tag)
            salary_min, salary_max, salary_value = self._find_vacancy_salary(tag)
            company_name = self._find_hirer(tag)
            container = DataClass(
                    name=vacancy_name,
                    reference=vacancy_ref,
                    min_salary=salary_min,
                    max_salary=salary_max,
                    salary_value=salary_value,
                    company_name=company_name,
                    source=self.BASE_URL
                )
            return container

    def _find_vacancy_name_ref(self, tag: Tag) -> tuple[str, str]:
        """Вытянуть название вакансии и ссылку на эту вакансию"""
        vacancy_tag = tag.find(
            'span',
            attrs={
                'class': 'resume-search-item__name'
            }
        )
        a_tag = vacancy_tag.find('a')
        return unidecode(a_tag.string), a_tag.attrs.get('href')

    def _find_vacancy_salary(self, tag: Tag) -> tuple[int | None, int | None, str | None]:
        """Разобрать параметр зарплаты"""
        sidebar_tag = tag.find(
            'div',
            attrs={
                'class': 'vacancy-serp-item__sidebar'
            }
        )
        if sidebar_tag:
            # type: list[str]
            dim_salary = [item for item in sidebar_tag.contents[0].stripped_strings]
            if len(dim_salary) > 1:
                if dim_salary[0] == 'от':
                    return self._convert_unicode_to_int(dim_salary[1]), None, unidecode(dim_salary[2])
                elif dim_salary[0] == 'до':
                    return None, self._convert_unicode_to_int(dim_salary[1]), unidecode(dim_salary[2])
                else:
                    salary_lr = [
                        int(string.replace(' ', ''))
                        for string in unidecode(dim_salary[0]).split('-')
                    ]
                    return salary_lr[0], salary_lr[1], unidecode(dim_salary[1])

        return None, None, None

    @staticmethod
    def _convert_unicode_to_int(string: str) -> int:
        """Конвертация UNICODE в int"""
        normal_string = unidecode(string)
        no_whitespace = normal_string.replace(' ', '')
        return int(no_whitespace)

    def _find_hirer(self, tag: Tag) -> str:
        """Достать название компании"""
        hirer_company_tag = tag.find(
            'div',
            attrs={
                'class': 'vacancy-serp-item__meta-info-company'
            }
        )
        a_tag = hirer_company_tag.find('a')
        return ''.join(unidecode(a) for a in a_tag.contents)

    def _load(self, page_numner: int) -> None:
        """Загрузить в класс данные в формате BS"""
        html_doc = self._get_html_page(
            self.BASE_URL, self.HEADERS, self.QUERY_PARAMS | {'page': page_numner}
        )
        self._parse_html(html_doc)

    def _process(self) -> list[DataClass]:
        """Обратать сырые данные в список контейнеров"""
        if self.soup is None:
            raise RuntimeError("Empty body soup")

        ship = []  # list[DataClass]
        for vacancy in self._get_list_category():
            container = self._decompose_div(vacancy)
            if container:
                ship.append(container)
        return ship

    def collect(self) -> list[DataClass]:
        """Публичный метод для сбора данных"""
        all_data = []  # type: list[DataClass]
        for page_number in range(100):
            try:
                self._load(page_number)
                data = self._process()
                all_data += data
            except RuntimeError:
                break
        return all_data

    def save(self, data: list[DataClass]) -> None:
        """Сохранить в файл"""
        with open('scrapped.json', 'w') as file:
            json.dump(data, file, indent=2, cls=DataClassEncoder)

    def __str__(self) -> str:
        return self.soup or 'Empty soup'


if __name__ == '__main__':
    scrapper = HHPythonScrapper()
    data = scrapper.collect()
    scrapper.save(data)
