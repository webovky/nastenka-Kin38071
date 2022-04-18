"""
# from datetime import datetime
from pony.orm import PrimaryKey, Required, Optional, Database, Set


db = Database()
db.bind(provider="sqlite", filename="./database.sqlite", create_db=True)

class User(db.Entity):
    nick = PrimaryKey(str)
    passwd = Required(str)

db.generate_mapping(create_tables=True)
"""