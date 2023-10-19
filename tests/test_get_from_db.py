import pytest

from core.config import Settings
from databases.databases import Standby_Shiptor_database


settings = Settings()
db = Standby_Shiptor_database(host=settings.shiptor_standby_base_host,
                                   database='shiptor',
                                   user=settings.user,
                                   password=settings.password)

# def test_multiplace():
    # data = db.get_packages_by_id(packages=['RP561584425'])
    # assert data['id'] ==