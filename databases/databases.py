# Developed by NickolaQ Trekov
import logging
import re

import psycopg2
from psycopg2._psycopg import OperationalError
from core.logging import logger

from core import config

settings = config.Settings()


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

    def get(self, query):
        TRYIES = 0
        while TRYIES <= 5:
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
                    else:
                        return []
                connection.close()
            except OperationalError as e:
                logger.error(f"DB: {self.database}|GET| Error: {e}")
                TRYIES +=1
                # return None
            except TimeoutError:
                logger.error(f"DB: {self.database}| TIMEOUT ERROR")
                TRYIES += 1
                # return None
            except Exception as e:
                logger.error(f"DB {self.database}| Error = {e}")
                TRYIES+=1
        return []


    def get_one(self, query):
        result = self.get(query)
        if result != 0 and result != None:
            return result[0]
        else:
            return result


class Standby_Shiptor_database(Database_stock):

    def get_query(self, field:str, packages: str, join="", extfields="", extrawhere: list = None):
        query = """select p.id, external_id,sm.name as "method_name", p.current_status,p.returned_at, previous_id,
                 pj.name as "project", return_id, pb.main, pb.surrogate {extfields} from package p
                 join package_departure pd on p.id = pd.package_id
                 join project pj on p.project_id = pj.id
                 join package_barcode pb on p.id=pb.package_id
                 join shipping.method_tariff smt on pd.shipping_method_tariff_id = smt.id
                 join shipping.method sm on smt.shipping_method_slug = sm.slug
                 {join}
                where {field} in ({packages})""".format(field=field, packages=packages,join=join, extfields=extfields)
        if extrawhere:
            for where in extrawhere:
                query += f" and {where['condition']} {where['operator']} ({where['values']})"
        return query

    def shiptor_data_dict(self, value, id=None, external_id=None, surrogate=None, main=None, method_name=None,
                          current_status=None, returned_at=None, return_id=None, reception_warehouse_id=None,
                          project=None,comment=None, previous_id=None) -> dict:
        return {'value': value, 'id': id, 'external_id': external_id, 'surrogate': surrogate, 'main': main,
                'method': method_name, 'shiptor_status': current_status, 'returned_at': returned_at, 'return_id': return_id,
                'reception_warehouse_id': reception_warehouse_id, 'project': project, 'previous_id':previous_id,
                'comment': comment}

    def get_packages(self, packages: list):
        rps, externals, barcodes, full_data = [], [], [], []
        for package in packages:
            if str(package).upper()[0:2] == 'RP':
                rps.append(f"{package[2:]}")
            else:
                externals.append(f"'{str(package).upper()}'")
        #  logging
        logger.debug(f"packages(input) count: {len(packages)}")
        logger.debug(f"package_id(rps) count: {len(rps)} ({len(rps) / len(packages) * 100}%)")
        logger.debug(f"package_id(externals) count: {len(externals)} ({len(externals) / len(packages) * 100}%)")
        if (len(externals) + len(rps)) < len(packages):
            logger.error(f"lost packages count {len(packages) - (len(externals) + len(rps))}")
        #########################################################################################

        if len(rps) == 0:
            rps_e = []
        rps_e = self.get_packages_by_id(rps)
        if len(externals) == 0:
            rps_e = []
        externals_e = self.get_packages_by_external(externals)
        logger.debug(f"all = {rps_e+externals_e}")
        full_data = rps_e+externals_e
        for package in full_data:
            if "ВОЗВРАТ" in str(package['method']).upper():
                package['result'] = f"RP{package['id']}"
            else:
                package['result'] = package['external_id']
        return full_data

    def get_packages_by_id(self, packages: list, field="p.id", extrawhere: list = None) -> list:
        result, packages_string, previouses = [], [], []
        logger.debug(f"packages: {packages}")
        packages_string = ",".join(packages)
        query = self.get_query(field, packages_string, extrawhere=extrawhere)
        logger.debug(f"query= {query}")
        data = self.get(query)
        for package in packages:
            for line in data:
                if int(package) == line['id']:
                    if line['previous_id']:
                        previouses.append(f"{line['previous_id']}")
                        break
                    else:
                        result.append(self.shiptor_data_dict(package, **line))
                        break
            else:
                result.append(self.shiptor_data_dict(package, comment="Not found in shiptor"))
        if previouses:
            logger.debug(f"Start get previouses. Previous = {previouses}")
            # conditions = [{'condition': "p.previous_id", 'operator': "is", 'values': "null"}]
            previouses = self.get_packages_by_id(previouses)
            logger.debug(f"Finish get prviouses")
            result += previouses
        logger.debug(f"result len = {len(result)}")
        return result

    def get_packages_by_external(self, externals: list) -> list:
        result, packages_string, barcodes = [], [], []
        packages_string = ",".join(externals)
        query = self.get_query("UPPER(p.external_id)", packages_string)
        data = self.get(query)
        logger.debug(f"externals shiptor len = {len(data)}")
        for package in externals:
            for line in data:
                if package[1:-1] == line['external_id']:
                    result.append(self.shiptor_data_dict(package[1:-1], **line))
                    break
            else:
                barcodes.append(package)

        barcodes = self.get_packages_by_barcode(barcodes)
        result += barcodes
        logger.debug(f"ext len={len(result)}")
        return result

    def get_packages_by_barcode(self, barcodes: list) -> list:
        result, packages_string = [], []
        packages_string = ",".join(barcodes)
        query = self.get_query("UPPER(pb.surrogate)", packages_string)
        data = self.get(query)
        logger.debug(f"externals shiptor = {data}")
        for package in barcodes:
            package=package[1:-1]
            for line in data:
                logger.debug(f"{line['surrogate']} = {package}")
                if package == line['surrogate']:
                    result.append(self.shiptor_data_dict(package, **line))
                    break
            else:
                result.append(self.shiptor_data_dict(package, comment="Not found in shiptor"))
        logger.debug(f"ext len={len(result)}")
        return result
