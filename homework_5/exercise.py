import json
import os

from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

DEBUG=False


class Mail:
    def __init__(self, **kwargs) -> None:
        for name, value in kwargs.items():
            setattr(self, name, value)

    def __str__(self) -> str:
        return json.dumps(self.__dict__, indent=2)


class MailCollector:
    """Сборщик писем из почтового ящика"""
    LOGIN = "study.ai_172@mail.ru"
    PASSWORD = "NextPassword172#"
    __slots__ = ("driver", "client", "wait", "ship")

    def __init__(self) -> None:
        chrome_options = Options()
        if not DEBUG:
            chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.client = MongoClient('127.0.0.1', 27017)
        self.wait = WebDriverWait(self.driver, 10)
        self.ship = []  # type: list[Mail]

    def _login_mailbox(self) -> None:
        self.driver.get("https://mail.ru/")
        login_field = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[@data-testid='login-input']")
            )
        )
        login_field.send_keys(self.LOGIN, Keys.ENTER)
        passwd_field = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//input[@data-testid='password-input']")
            )
        )
        passwd_field.send_keys(self.PASSWORD, Keys.ENTER)

    def _collect_data_from_mail(self) -> None:
        title_subject = self.wait.until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "thread__subject")
            )
        )
        author_subject = self.wait.until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "letter-contact")
            )
        )
        date_subject = self.wait.until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "letter__date")
            )
        )
        letter_subject = self.wait.until(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "letter-body")
            )
        )
        self.ship.append(
            Mail(
                title=title_subject.text,
                author=author_subject.text,
                date=date_subject.text,
                letter=letter_subject.text
            )
        )

    def _collect_mails(self) -> None:
        mail_items = self.wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//a[contains(@class, 'js-letter-list-item')]")
            )
        )
        main_window = self.driver.current_window_handle
        for mail in mail_items:
            href_mail = mail.get_attribute("href")
            self.driver.execute_script('window.open(arguments[0]);', href_mail)
            new_window = [
                window
                for window in self.driver.window_handles
                if window != main_window
            ][0]
            self.driver.switch_to.window(new_window)
            self._collect_data_from_mail()
            self.driver.close()
            self.driver.switch_to.window(main_window)

    def process(self) -> None:
        self._login_mailbox()
        self._collect_mails()
        self.driver.quit()

    def save(self) -> None:
        db = self.client["mails"]
        collec = db.mail_ru
        for container in self.ship:
            collec.update_one(
                filter={"date": {"$eq": container.date}},
                update={"$set": container.__dict__},
                upsert=True
            )


if __name__ == '__main__':
    collector = MailCollector()
    collector.process()
    collector.save()
