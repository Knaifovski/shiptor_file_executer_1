from datetime import datetime

import pandas as pd
from django.utils.datastructures import MultiValueDict
from loguru import logger

from core.config import Settings

settings = Settings()

def get_packages_from_file(file) -> list:
    """return list of dicts package data"""
    packages = []
    try:
        xl_file = pd.ExcelFile(file)
        dfs = {sheet_name: xl_file.parse(sheet_name) for sheet_name in xl_file.sheet_names}
        for df in dfs.values():
            packages = df['packages'].values.tolist()
        packages = [str(package) for package in packages]
        return packages
    except Exception as e:
        logger.error(f"UNEXPECTER ERROR: {e}")



def get_files_data(files: dict) -> dict:
    """Return dictionary with keys: result - merged data, extradata_dfs - extra sheets (om,vp,vvp,etc)
     result_simple - simple_sheet with minimal data"""
    PACKAGES_LIST: list
    input_file = files['input']
    extradata = pd.ExcelFile(files['extradata'])
    result = pd.read_excel(input_file, converters={'value': str, 'result': str})
    result.drop_duplicates(subset='result', inplace=True, ignore_index=True)
    result.sort_values(by=['SAP_WH', 'project', 'method_id', 'comment'], inplace=True, ignore_index=True)
    result_simple = result[['value', 'result', 'SAP_WH', 'shiptor_status', 'returned_at', 'delivered_at', 'project',
                            'comment']].copy()

    extradata_dfs = {sheet_name: extradata.parse(sheet_name) for sheet_name in extradata.sheet_names}
    for sheet in extradata_dfs:
        logger.debug(f"sheet={sheet} values: {extradata_dfs[sheet]}")
        extradata_dfs[sheet]['result'] = extradata_dfs[sheet]['result'].astype(str)
        result = result.merge(extradata_dfs[sheet], on='result', how='left')
        result_simple = result_simple.merge(extradata_dfs[sheet], on='result', how='left')

    result_simple.rename(columns={"value": "Изначальное значение", "result": "Значение для САП", "SAP_WH": "Склад САП",
                                  "shiptor_status": "Статус Шиптора", "returned_at": "Возвращено",
                                  "delivered_at": "Доставлено", "project": "Клиент",
                                  "comment": "Комментарий"}, errors='raise', inplace=True)

    return {'result': result, 'extradata_dfs': extradata_dfs, 'simple': result_simple}


def checking_first(data):
    """Check packages from database data"""
    for package in data:
        comment = []
        if package['project'] not in [101849, 232708]:
            comment.append('Не относится к СММ')
            continue

        # status check
        if package['current_status'] not in ['return_to_sender', 'returned']:
            if package['current_status'] == 'delivered':
                comment.append("Передать на ВОЗВРАТ")
            else:
                comment.append("[СКЛАД] Принят на склад вне системы")

        # easy return
        elif (str(package['external_id'])[0:2] != "RP") and (str(package['external_id']).startswith(('R', "CCS"))):
            comment.append("Легкий возврат")

        # get sap warehouse id
        try:
            if package['external_id']:
                package['SAP_WH'] = settings.SAP_WAREHOUSES[package['external_id'][0:5]]['sap_wh_id']
            else:
                package['SAP_WH'] = settings.SAP_WAREHOUSES[package['value'][0:5]]['sap_wh_id']
        except:
            package['SAP_WH'] = pd.NA

        #if external_id contain "*" then its merchant
        if str(package['external_id']).__contains__('*'):
            comment.append("Мерчант")

        # Problem checking
        if package['method_id'] in (571, 827, 672):
            package['result'] = f"RP{package['id']}"
            # Get Problem by date
            if package['delivered_at']:
                if package['delivered_at'] > datetime(year=2023, month=6, day=16):
                    comment.append('Проблема СММ(SHPTRERP-4675)')
        else:
            package['result'] = package['external_id']
            if "returned_at" in package.keys() and package['returned_at'] > datetime(year=2023, month=6, day=16):
                comment.append('Проблема СММ(SHPTRERP-4675)')
        if package['result'] is None:
            package['result'] = package['value']
            comment.append(package['comment']) #what its do?
        package['comment'] = ",".join(comment)

    return data
