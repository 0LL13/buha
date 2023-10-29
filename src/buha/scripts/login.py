#!/usr/bin/env python
# -*- coding: utf-8 -*-
# login.py
import getpass
import hashlib
import os
import sqlite3
import sys
from typing import Tuple
from .helpers import clear_screen
from .helpers import create_headline


screen_cleared = False


class LoginMenu():
    """Menu options for starting buha."""

    def display_menu(self, company_name: str, language: str) -> None:
        global screen_cleared
        prompt = "LOGIN MENU"
        menu_login_head = create_headline(company_name, language, prompt=prompt)  # noqa

        if not screen_cleared:
            clear_screen()
            screen_cleared = True
            print(menu_login_head)

        login_menu = """
        1: Login
        2: Quit
        """

        print(login_menu)

    def run(self, conn: sqlite3.Connection, language: str,
            company_name: str) -> Tuple[bool, str]:
        """
        Display login menu: login or quit.
        Needs "company_name" for the head of menu, "language" for its language,
        and "conn".
        Logout closes connection and exits.
        """
        while True:
            self.display_menu(company_name, language)
            choice = input("Enter an option: ")
            if choice == "1":
                authenticated, initials = login_employee(conn, language,
                                                         company_name)
                conn.commit()
                break
            else:
                authenticated = False
                initials = None
                conn.close()
                sys.exit()

        return authenticated, initials


def login_employee(conn: sqlite3.Connection, language: str,
                   company_name: str) -> Tuple[bool, str]:
    """Returns authenticated, initials."""

    initials = input("Enter initials: ")
    initials_validated = initials_in_table(conn, initials)
    if initials_validated:
        password = getpass.getpass("Enter password: ")
        password_validated = password_correct(conn, initials, password)
        if password_validated:
            return True, initials

    return False, None


def hash_password(password, salt=None):
    if not salt:
        salt = os.urandom(16)  # Generate a random salt
    password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)  # noqa
    return salt, password_hash


def initials_in_table(conn: sqlite3.Connection, initials: str) -> bool:
    with conn:
        cur = conn.cursor()
        res = cur.execute("SELECT initials FROM persons")
        res_initials = res.fetchall()
        for res in res_initials:
            abbr = ''.join(str(c) for c in res)
            if 0:
                print("res_initials: ", res_initials)
                print("abbr: ", abbr)
                print("initials: ", initials)
            if abbr == initials:
                return True
    return False


def password_correct(conn: sqlite3.Connection, initials: str, password: str) -> bool:  # noqa

    with conn:
        cur = conn.cursor()

        # Retrieve salt from database
        get_salt = "SELECT salt FROM settings WHERE initials = ?"
        cur.execute(get_salt, (initials,))
        salt_tuple = cur.fetchone()
        if salt_tuple:
            salt = salt_tuple[0]
        else:
            return False

        # Retrieve hashed password from database
        get_pw = "SELECT password_hash FROM settings WHERE initials = ?"
        cur.execute(get_pw, (initials,))
        hashed_pw_tuple = cur.fetchone()

        if hashed_pw_tuple:
            password_hash = hashed_pw_tuple[0]
        else:
            return False

        _, computed_password_hash = hash_password(password, salt)

        return computed_password_hash == password_hash
