import pandas as pd
from django.utils.datastructures import MultiValueDict
from loguru import logger


def get_packages_from_file(file) -> dict:
    packages = []
    try:
        xl_file = pd.ExcelFile(file)
        dfs = {sheet_name: xl_file.parse(sheet_name) for sheet_name in xl_file.sheet_names}
        for df in dfs.values():
            packages = df['packages'].values.tolist()
        packages = [str(package) for package in packages]
        return packages
    except:
        logger.error("UNEXPECTER ERROR")
        # raise Exception("ERROR")

def get_files_data(files: dict):
    PACKAGES_LIST: list
    input_file = files['input']
    extradata = pd.ExcelFile(files['extradata'])
    result = pd.read_excel(input_file)
    result.drop_duplicates(subset='result', inplace=True, ignore_index=True)
    result.sort_values(by=['SAP_WH', 'project', 'method_id', 'comment'], inplace=True, ignore_index=True)
    result_simple = result[['value', 'result', 'SAP_WH', 'shiptor_status', 'returned_at','delivered_at', 'project',
                            'comment']].copy()

    extradata_dfs = {sheet_name: extradata.parse(sheet_name) for sheet_name in extradata.sheet_names}
    result['result'] = result['result'].astype(str)
    result_simple['result'] = result['result'].astype(str)
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
