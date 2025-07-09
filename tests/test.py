from main import *

session = get_db()

def test_create_user():
    test_user = create_user(login="test", password="test123", salary=314.515, upgrade_date=datetime(year=2025, month=7, day=7))
    print(type(test_user))