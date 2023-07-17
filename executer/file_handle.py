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

    extradata_dfs = {sheet_name: extradata.parse(sheet_name) for sheet_name in extradata.sheet_names}
    result['result'] = result['result'].astype(str)
    for sheet in extradata_dfs:
        extradata_dfs[sheet]['result'] = extradata_dfs[sheet]['result'].astype(str)
        result = result.merge(extradata_dfs[sheet], on='result', how='left')
    return result


