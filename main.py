#!/usr/bin/env python
# -*- coding: utf-8 -*-
# main.py
import getpass
import sqlite3
from typing import Tuple

from src.buha.scripts.helpers import check_databases  # looking for databases
from src.buha.scripts.helpers import state_company
from src.buha.scripts.helpers import path_to_database
from src.buha.scripts.helpers import continue_
from src.buha.scripts.helpers import show_table
from src.buha.scripts.helpers import check_for_matches
from src.buha.scripts.helpers import clear_screen
from src.buha.scripts.start import MenuStart
from src.buha.scripts.login import LoginMenu
from src.buha.scripts.person import MenuNewPerson as NewPerson
from src.buha.scripts.settings import add_settings


"""
Entry point for buha. Get name of company. The name of the company makes the
name of the database. If no database of that name is there, a new database will
be created and a first employee is added. Once a database is installed
employees log in with initials (unique identifiers) and password after they
picked their company.
"""


screen_cleared = False


def initialize() -> Tuple[sqlite3.Connection, str, str]:
    """
    - check if database exists
    - if not exists:
        - start new db: setup_new_db
            - language
            - company_name
            - created_by
            - activate new database -> conn
            - create first employee: new_person
            - add_settings (initials, password, language) for first employee
    - if exists:
        - ask for language, company_name
        - if company_name doesn't fit create new database (start_new_db)
        - return sqlite3.Connection, language and company_name -> login
    """
    global screen_cleared
    if not screen_cleared:
        clear_screen()
        screen_cleared = True
    targets = check_databases()  # returns list with databases
    # language can be changed in settings
    language = "de"
    if targets == []:   # no database found
        conn, language, company_name = setup_new_db(language)
        return conn, language, company_name
    else:
        company_name = state_company(language)
        match = check_for_matches(company_name, targets, language)
        if match is None:
            print("    Neue Firma.")
            conn, language, company_name = setup_new_db()
            return conn, language, company_name
        conn = activate_database(match)
        return conn, language, match


def setup_new_db(language: str) -> Tuple[sqlite3.Connection, str, str]:
    # database will be named after company
    company_name = state_company(language)
    created_by = getpass.getuser()
    conn = activate_database(company_name)
    # first person of the company to be created
    new_person = NewPerson()
    name, person_id, initials = new_person.enter_name(conn, created_by, company_name, language)  # noqa
    # is_internal is True because this is the very first person to be created.
    add_settings(conn, created_by, language, person_id, initials, is_internal=True)  # noqa

    if 0:
        print("show_persons")
        show_table(conn, "persons")
        print("show_names")
        show_table(conn, "names")
        print("show_settings")
        show_table(conn, "settings")
        if continue_():
            pass

    return conn, language, company_name


def activate_database(company_name: str) -> sqlite3.Connection:
    path = path_to_database()
    db_path = path / company_name
    if 0:
        print("activate_database in main.py: ")
        print("path: ", path)
        print("company_name: ", company_name)
        print("db_path: ", db_path)
    conn = sqlite3.connect(db_path)
    return conn


def main():
    conn, language, company_name = initialize()
    login_menu = LoginMenu()
    authenticated, initials = login_menu.run(conn, language, company_name)  # noqa
    if authenticated:
        menu = MenuStart()
        menu.run(conn, initials, company_name, language)
    else:
        main()


if __name__ == "__main__":
    main()
