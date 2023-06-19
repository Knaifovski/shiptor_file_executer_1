# Developed by NickolaQ Trekov
import logging

import psycopg2
from psycopg2._psycopg import OperationalError

from core import config

logger = logging.getLogger(__name__)
settings = config.Setting()


class Database_stock:
    """
    Database base
    """

    def __init__(self, host: str, database: str, user: str, password: str):
        try:
            # self.con = psycopg2.connect(host=host, database=database, user=user, password=password)
            self.database = database
            self.host = host
            self.user = user
            self.password = password
            # self.cur = self.con.cursor()
        except:
            logger.error(f'DB: {database}|ERROR| CONNECT TO DATABASE')

    def commit(self, query):
        try:
            connection = psycopg2.connect(host=self.host, database=self.database,
                                          user=self.user, password=self.password, connect_timeout=5)
            with connection.cursor() as cursor:
                cursor.execute(query)
                if cursor.rowcount < 10:
                    connection.commit()
                    logger.warning(
                        'DB: {}|COMMIT|executed transaction:\n{}\ncommit count:{}'.format(self.database, query,
                                                                                          cursor.rowcount))
                    if cursor.rowcount == 0:
                        return None
                    return cursor.rowcount
                else:
                    logger.error('DB: {}|COMMIT| COMMIT PROTECT(>10)\ntransaction:\n{}\ncommit count:{}'.format(
                        self.database, query, cursor.rowcount))
                connection.close()
        except OperationalError as e:
            logger.error(f"The error '{e}' occurred")
            return None
        except TimeoutError:
            logger.error(f"DB: {self.database}| TIMEOUT ERROR")
            return None

    def get(self, query):
        try:
            connection = psycopg2.connect(host=self.host, database=self.database,
                                          user=self.user, password=self.password, connect_timeout=5)
            with connection.cursor() as cursor:
                cursor.execute(query)
                logger.warning('DB: {}|GET|executed get transaction:\n {}'.format(self.database, query))
                result = cursor.fetchall()
                colnames = [desc[0] for desc in cursor.description]
                dict_ = []
                if result:
                    for row in result:
                        dict_.append(dict(zip(colnames, row)))
                    logger.warning('DB: {}|GET|response data:\n{}'.format(self.database, dict_))
                    return dict_
            connection.close()
        except OperationalError as e:
            logger.error(f"DB: {self.database}|GET| Error: {e}")
            return None
        except TimeoutError:
            logger.error(f"DB: {self.database}| TIMEOUT ERROR")
            return None

    def get_one(self,query):
        result = self.get(query)
        if result != 0 and result != None:
            return result[0]
        else:
            return result


Shiptor_Database = Database_stock(host=settings.shiptor_base_host,
                                  database="shiptor",
                                  user=settings.user,
                                  password=settings.password)

Stage_Shiptor_database = Database_stock(host= settings.shiptor_standby_base_host,
                                        database='shiptor',
                                        user=settings.user,
                                        password=settings.password)