from pydantic import BaseSettings
import os

class Settings(BaseSettings):
    secret_key: str
    user: str
    password: str
    shiptor_standby_base_host: str
    FILEFOLDER = 'temp/'
    FILENAME_FIRST = FILEFOLDER + 'ShiptorData.xlsx'
    FILERESULT = FILEFOLDER + 'RESULT.xlsx'
    SAP_WAREHOUSES = [
        {'sap_wh_id': 1000, 'prefix': 12357, 'shiptor_wh_name': "Склад ФФ Москва Шарапово"},
        {'sap_wh_id': 1002, 'prefix': 58688, 'shiptor_wh_name': "Склад ФФ Воронеж-2"},
        {'sap_wh_id': 1003, 'prefix': 54858, 'shiptor_wh_name': "Склад ФФ Пушкино"},
        {'sap_wh_id': 1004, 'prefix': 60428, 'shiptor_wh_name': "Пушкино Холодная полка"},
        {'sap_wh_id': 2000, 'prefix': 58700, 'shiptor_wh_name': "Санкт-Петербург ФФ"},
        {'sap_wh_id': 2001, 'prefix': 60375, 'shiptor_wh_name': "Санкт-Петербург FMCGG"},
        {'sap_wh_id': 2002, 'prefix': 82334, 'shiptor_wh_name': "Склад ФФ Санкт-Петербург-2"},
        {'sap_wh_id': 3000, 'prefix': 74559, 'shiptor_wh_name': "Краснодар, fresh 2p, процесс СММ Холодная полка"},
        {'sap_wh_id': 3002, 'prefix': 58703, 'shiptor_wh_name': "Склад ФФ Волгоград"},
        {'sap_wh_id': 3003, 'prefix': 58709, 'shiptor_wh_name': "Склад ФФ Ростов-на-Дону"},
        {'sap_wh_id': 3004, 'prefix': 58690, 'shiptor_wh_name': "Склад ФФ Краснодар-2"},
        {'sap_wh_id': 5000, 'prefix': 58704, 'shiptor_wh_name': "Склад ФФ Уфа"},
        {'sap_wh_id': 5001, 'prefix': 58695, 'shiptor_wh_name': "Склад ФФ Самара"},
        {'sap_wh_id': 5002, 'prefix': 58710, 'shiptor_wh_name': "Склад ФФ Пермь"},
        {'sap_wh_id': 5003, 'prefix': 58698, 'shiptor_wh_name': "Нижний Новгород"},
        {'sap_wh_id': 5004, 'prefix': 58682, 'shiptor_wh_name': "Склад FMCG процесс СММ Самара-2"},
        {'sap_wh_id': 5005, 'prefix': 74557,
         'shiptor_wh_name': "NNOV-2 - Холодная полка склада ФФ СММ в Нижнем Новгороде"},
        {'sap_wh_id': 6000, 'prefix': 58693, 'shiptor_wh_name': "Склад ФФ Екатеринбург"},
        {'sap_wh_id': 6001, 'prefix': 58707, 'shiptor_wh_name': "Склад ФФ Челябинск"},
        {'sap_wh_id': 7000, 'prefix': 60376, 'shiptor_wh_name': "Склад FMCG процесс СММ Новосибирск"},
        {'sap_wh_id': 7001, 'prefix': 58684, 'shiptor_wh_name': "Склад ФФ Новосибирск-2"},
        {'sap_wh_id': 7002, 'prefix': 58689, 'shiptor_wh_name': "Красноярск"},
        {'sap_wh_id': 7003, 'prefix': 58696, 'shiptor_wh_name': "Омск"},
        {'sap_wh_id': 8000, 'prefix': 58692, 'shiptor_wh_name': "Склад ФФ Артем "},
        {'sap_wh_id': 8001, 'prefix': 58702, 'shiptor_wh_name': "Хабаровск"}
                      ]
    class Config:
        env_file = os.path.join(os.getcwd(), '.env')
