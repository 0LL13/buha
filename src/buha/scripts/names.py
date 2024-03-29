#!/usr/bin/env python
# -*- coding: utf-8 -*-
# names.py
"""Use dataclass Name and menu to enter names. Check if entry with given names
already exists. If not, create entry in sqlite3 table "names", with names
referencing to person_id via foreign key."""
import datetime
import re
import sqlite3
from operator import itemgetter
from .constants import choose_option
from .constants import firstname_prompt
from .constants import lastname_prompt
from .constants import middlenames_prompt
from .constants import nickname_prompt
from .constants import previous_prompt
from .constants import salutation_prompt
from .constants import suffix_prompt
from .constants import enter_prompt
from .helpers import Menu
from .shared import Name


class MenuName(Menu):
    """Menu to enter the names of a contact."""

    def __init__(self):
        super().__init__()
        super().change_menu("names")

        self.entries = {
            "fn": None,
            "mn": None,
            "ln": None,
            "nn": None,
            "pn": None,
            "suffix": None,
            "salutation": None,
        }

        self.choices = {
            "1": self.enter_firstname,
            "2": self.enter_middlenames,
            "3": self.enter_lastname,
            "4": self.enter_nickname,
            "5": self.enter_previousname,
            "6": self.enter_generational_suffix,
            "7": self.enter_salutation,
            "8": self.commit,
            "9": False,
        }

    def reset_entries(self):
        self.entries = {key: None for key in self.entries}

    def display_menu(self, company_name: str, language: str,
                     task: str = "names") -> None:
        super().display_menu(company_name, language, task=task)

    def run(self, conn: sqlite3.Connection, created_by: str, company_name: str,
            language: str) -> Name | None:

        """Display Menu, gather entries in dict "entries", and finally put
        the data in new instance of Name."""

        while True:
            self.display_menu(company_name, language, task="names")
            choice = choose_option(language)
            if not self.choices.get(choice):
                break
            else:
                action = self.choices.get(choice)
                if action and choice == "8":
                    name = action(created_by, conn, language)
                    super().go_back()
                    return name
                else:
                    super().change_menu("names")
                    action(language)

        super().go_back()
        return None

    def commit(self, conn: sqlite3.Connection, created_by: str,
               language: str) -> Name | None:
        name = self.generate_name_instance()
        if name.first_name is None or name.last_name is None:
            print("No valid name. Name needs first and last names.")
            super().go_back()
            return None

        # note: the actual commitment to the database will be done by the
        # calling function from person.py because person_id is needed and can
        # only be provided from there

        super().go_back()
        return name

    def enter_firstname(self, language: str) -> None:
        firstname = enter_prompt(firstname_prompt, language)
        self.entries["fn"] = firstname

    def enter_middlenames(self, language) -> None:
        middlename = enter_prompt(middlenames_prompt, language)
        middlename = re.sub(" +", " ", middlename)
        self.entries["mn"] = middlename

    def enter_lastname(self, language: str) -> None:
        lastname = enter_prompt(lastname_prompt, language)
        self.entries["ln"] = lastname

    def enter_nickname(self, language) -> None:
        nickname = enter_prompt(nickname_prompt, language)
        self.entries["nn"] = nickname

    def enter_previousname(self, language) -> None:
        previousname = enter_prompt(previous_prompt, language)
        previousname = re.sub(" +", " ", previousname)
        self.entries["pn"] = previousname

    def enter_generational_suffix(self, language) -> None:
        suffix = enter_prompt(suffix_prompt, language)
        self.entries["suffix"] = suffix

    def enter_salutation(self, language) -> None:
        salutation = enter_prompt(salutation_prompt, language)
        self.entries["salutation"] = salutation

    def generate_name_instance(self) -> Name:
        collected_entries = self.entries
        # see here about use of itemgetter:
        # https://stackoverflow.com/a/17755259/6597765
        first_name, last_name = itemgetter("fn", "ln")(collected_entries)
        name_list = [first_name, last_name]
        mn, nn, pn, suffix, salutation = \
            itemgetter("mn", "nn", "pn", "suffix", "salutation")(collected_entries)  # noqa
        default_names_list = [mn, nn, pn, suffix, salutation]

        name = Name(*name_list, *default_names_list)
        if 0:
            print(name)
        return name

    def generate_table_names(self, conn: sqlite3.Connection) -> None:
        table_names = """CREATE TABLE IF NOT EXISTS names (
                         name_id INTEGER PRIMARY KEY,
                         person_id INTEGER,
                         created_by TEXT,
                         timestamp TEXT,
                         first_name TEXT NOT NULL,
                         middle_names TEXT,
                         last_name TEXT NOT NULL,
                         nickname TEXT,
                         previous_name TEXT,
                         suffix TEXT,
                         salutation TEXT,
                         FOREIGN KEY (person_id)
                            REFERENCES persons(person_id)
                            ON DELETE CASCADE
                         )"""
        with conn:
            cur = conn.cursor()
            cur.execute(table_names)
            conn.commit()

    def commit_name_to_db(self, conn: sqlite3.Connection, created_by: str,
                          name: Name, person_id: int, language: str) -> None:
        self.generate_table_names(conn)
        if not self.name_already_in_db(conn, name, language):
            self.add_name_to_db(conn, created_by, name, person_id)
            self.reset_entries()
        else:
            self.handle_double_entry(conn, created_by, name, person_id, language)  # noqa

    def handle_double_entry(self, conn: sqlite3.Connection, created_by: str,
                            name: Name, person_id: int, language: str) -> None:
        double = """
        Entry with these first and last names already exists.
        Please add a middle name!
        """

        print(double)
        self.enter_middlenames(language)
        name = self.generate_name_instance()

        if not self.name_already_in_db(conn, name, language):
            self.add_name_to_db(conn, created_by, name, person_id)
            self.reset_entries()
            return
        else:
            message_name_exists = "Name already exists. Aborting"
            print(message_name_exists)
            self.reset_entries()
            return

    def add_name_to_db(self, conn: sqlite3.Connection, created_by: str,
                       name: Name, person_id: int) -> None:
        add_name = """INSERT INTO names (
                      person_id, created_by, timestamp, first_name,
                      middle_names, last_name, nickname, previous_name, suffix,
                      salutation)
                      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        # timestamp = str(datetime.date.today())

        with conn:
            cur = conn.cursor()
            cur.execute(add_name, (person_id, created_by, timestamp,
                                   name.first_name, name.middle_names,
                                   name.last_name, name.nickname,
                                   name.previous_name, name.suffix,
                                   name.salutation))
            conn.commit()

    def name_already_in_db(self, conn: sqlite3.Connection, name: Name,
                           language) -> bool:
        select_names = "SELECT first_name, middle_names, last_name FROM names"
        with conn:
            cur = conn.cursor()
            res = cur.execute(select_names)
            names = res.fetchall()

        for name_tuple in names:
            fn, mn, ln = name_tuple[0], name_tuple[1], name_tuple[2]
            if 0:
                print(fn, mn, ln)
            if fn.lower() == name.first_name.lower():
                if ln.lower() == name.last_name.lower():
                    if mn is None and name.middle_names is None:
                        return True
                    elif mn is None and name.middle_names is not None:
                        return False
                    else:
                        return mn.lower() == name.middle_names.lower()
