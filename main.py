#!/usr/bin/env python
# -*- coding: utf-8 -*-
# main.py
import getpass
import sqlite3
import sys
from typing import Tuple

from src.buha.scripts.helpers import check_databases
from src.buha.scripts.helpers import state_company
from src.buha.scripts.helpers import path_to_database
from src.buha.scripts.helpers import check_for_matches
from src.buha.scripts.helpers import clear_screen
from src.buha.scripts.helpers import continue_
from src.buha.scripts.helpers import Menu
from src.buha.scripts.login import LoginMenu
from src.buha.scripts.person import MenuNewPerson as NewPerson
from src.buha.scripts.start import MenuStart


"""
Entry point for buha. Get name of company. The name of the company makes the
name of the database. If no database of that name is there, a new database will
be created and a first employee is added. Once a database is installed
employees log in with initials (unique identifiers) and password after they
picked their company.
"""


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
    clear_screen()

    # language can be changed in settings
    language = "de"
    company_name = "BuHa   "  # last three chars will be cut off, usually .db
    task = "main"

    menu = Menu()
    menu.print_headline(company_name, language, task)
    print()

    company_name = state_company(language)

    targets = check_databases()  # returns list with databases
    if targets == []:   # no database found --> first database
        return setup_new_company(company_name, language)
    else:
        # check for typos -> return best match
        match = check_for_matches(company_name, targets, language)

        # if difference too big --> different/new company
        if match is None:
            print("    Neue Firma.")
            return setup_new_company(company_name, language)

        conn = activate_database(match)
        return conn, language, match


def setup_new_company(company_name: str, language: str) -> Tuple[sqlite3.Connection, str, str]:  # noqa
    # database will be named after company
    conn = activate_database(company_name)

    # Owner of PC does the first database entry
    created_by = getpass.getuser()

    # A first user needs to be created bc otherwise no access to db ...
    new_person = NewPerson()
    new_person.enter_name(conn, created_by, company_name, language)

    return conn, language, company_name


def activate_database(company_name: str) -> sqlite3.Connection:
    db_path = path_to_database(company_name)
    conn = sqlite3.connect(db_path)

    return conn


def main():
    conn, language, company_name = initialize()

    login_menu = LoginMenu()
    authenticated, initials = login_menu.run(conn, language, company_name)
    if 0:
        print("initials: ", initials)
        continue_()
    if (authenticated, initials) == (False, None):
        conn.close()
        sys.exit()
    else:
        menu = MenuStart()
        menu.run(conn, initials, company_name, language)


if __name__ == "__main__":
    main()
