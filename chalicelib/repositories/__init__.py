# Created in June 15, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template microservice repository definition module.

Defines the repository interface along with patterns applied.
Repository Layer gives you additional level of abstraction over data access.
"""


# MySQL Translator or common shared features to use with
from chalicelib.repositories.repository import Repository
from chalicelib.repositories.mysql_repository import BaseRepository
from chalicelib.repositories.mysql_statement import MySQLStatement
from chalicelib.repositories.mysql_translator import mysql_translator
