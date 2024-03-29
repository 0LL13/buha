#!/usr/bin/env python
# -*- coding: utf-8 -*-
# new_entry.py
import sqlite3
from .constants import choose_option
from .person import MenuNewPerson
from .helpers import Menu


class MenuNewEntry(Menu):
    """Menu options for adding a new entry."""

    def __init__(self):
        super().__init__()
        super().change_menu("new entry")

        self.choices = {
            "1": self.new_person,
            "2": self.new_entity,
            "3": self.new_object,
            "4": self.new_project,
            "5": self.new_service,
            "6": self.new_account,
            "7": self.settings,
            "9": False
        }

    def display_menu(self, company_name: str, language: str,
                     task="new entry") -> None:
        super().display_menu(company_name, language, task=task)

    def run(self, conn: sqlite3.Connection, created_by: str,
            company_name: str, language: str) -> None:

        # "created_by" are the initials of the person working with the program
        while True:
            self.display_menu(company_name, language, task="new entry")
            choice = choose_option(language)

            if not self.choices.get(choice):
                break
            else:
                action = self.choices.get(choice)
                super().change_menu("new entry")
                action(conn, created_by, company_name, language)

        super().go_back()

    def new_person(self, conn: sqlite3.Connection, created_by: str,
                   company_name: str, language: str) -> None:

        print("I was here.")

        menu = MenuNewPerson()
        menu.enter_name(conn, created_by, company_name, language)

    def new_entity(self, conn: sqlite3.Connection, created_by: str,
                   company_name: str, language: str) -> None:
        print("ToDo")  # pragma: no cover

    def new_object(self, conn: sqlite3.Connection, created_by: str,
                   company_name: str, language: str) -> None:
        print("ToDo")  # pragma: no cover

    def new_project(self, conn: sqlite3.Connection, created_by: str,
                    company_name: str, language: str) -> None:
        print("ToDo")  # pragma: no cover

    def new_service(self, conn: sqlite3.Connection, created_by: str,
                    company_name: str, language: str) -> None:
        print("ToDo")  # pragma: no cover

    def new_account(self, conn: sqlite3.Connection, created_by: str,
                    company_name: str, language: str) -> None:
        print("ToDo")  # pragma: no cover

    def settings(self, conn: sqlite3.Connection, created_by: str,
                 company_name: str, language: str) -> None:
        print("ToDo")  # pragma: no cover
