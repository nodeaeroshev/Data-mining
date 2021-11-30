import os
from typing import Callable, Iterator
from urllib.parse import urlencode

import scrapy
from scrapy.http import HtmlResponse, Request

from instaparser.items import InstaparserItem
from instaparser.utils import fetch_csrf_token, fetch_user_id


class InstaSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    friendships_url = "https://i.instagram.com/api/v1/friendships/"

    COUNT_FOLLOWERS = 12

    def __init__(self, users: list[str], *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.users_for_parse = users
        self.INST_LOGIN = os.getenv('INST_LOGIN')
        self.INST_PWD = os.getenv('INST_PWD')

    def parse(
            self,
            response: HtmlResponse,
            *args,
            **kwargs
    ) -> Iterator[Request]:
        csrf = fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login,
            formdata={
                'username': self.INST_LOGIN,
                'enc_password': self.INST_PWD
            },
            headers={'X-CSRFToken': csrf}
        )

    def login(self, response: HtmlResponse) -> Iterator[Request] | None:
        json_data = response.json()
        if json_data.get('authenticated'):
            for user in self.users_for_parse:
                yield response.follow(
                    f'/{user}',
                    callback=self.user_parse,
                    cb_kwargs={'username': user}
                )

    def user_parse(
            self,
            response:
            HtmlResponse,
            username: str
    ) -> Iterator[Request]:
        user_id = fetch_user_id(response.text, username)
        followers_url = self.get_followers_url(user_id, self.COUNT_FOLLOWERS)
        yield response.follow(
            followers_url,
            callback=self.parse_subs,
            cb_kwargs={
                'username': username,
                'user_id': user_id,
                'url_gen': self.get_followers_url,
                'subs_description': 'followers'
            }
        )

        following_url = self.get_following_url(user_id, self.COUNT_FOLLOWERS)
        yield response.follow(
            following_url,
            callback=self.parse_subs,
            cb_kwargs={
                'username': username,
                'user_id': user_id,
                'url_gen': self.get_following_url,
                'subs_description': 'following'
            }
        )

    def parse_subs(
            self,
            response: HtmlResponse,
            user_id: int,
            username: str,
            url_gen: Callable[[int, int, int | None], str],
            subs_description: str
    ) -> Iterator[Request] | Iterator[InstaparserItem]:
        next_max_id = response.json().get('next_max_id')
        if next_max_id:
            url = url_gen(user_id, self.COUNT_FOLLOWERS, next_max_id)
            yield response.follow(
                url,
                callback=self.parse_subs,
                cb_kwargs={
                    'user_id': user_id,
                    'username': username,
                    'url_gen': url_gen,
                    'subs_description': subs_description
                }
            )

        users = response.json().get('users')
        new_users = []  # type: list[dict]
        for user in users:
            new_users.append(
                {
                    '_id': user.get('pk'),
                    'full_name': user.get('full_name'),
                    'username': user.get('username'),
                    'profile_pic_url': user.get('profile_pic_url')
                }
            )
        yield InstaparserItem(
            _id=user_id,
            username=username,
            users=new_users,
            collect_name=subs_description
        )

    def get_followers_url(
            self,
            user_id: int,
            count: int,
            max_id: int | None = None
    ) -> str:
        var = {'count': count, 'max_id': max_id}
        if not max_id:
            del var['max_id']
        return (
            f'{self.friendships_url}{user_id}'
            f'/followers/?{urlencode(var)}'
            f'&search_surface=follow_list_page'
        )

    def get_following_url(
            self,
            user_id: int,
            count: int,
            max_id: int | None = None
    ) -> str:
        var = {'count': count, 'max_id': max_id}
        if not max_id:
            del var['max_id']
        return (
            f'{self.friendships_url}{user_id}'
            f'/following/?{urlencode(var)}'
        )
