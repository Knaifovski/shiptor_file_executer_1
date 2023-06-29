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
        # for package in packages:
        #     package = str(package).rstrip()
        packages = [str(package).rstrip().lstrip() for package in packages]
        return packages
    except:
        logger.error("UNEXPECTER ERROR")
        # raise Exception("ERROR")

def get_files_data(files: MultiValueDict):
    PACKAGES_LIST: list
    input_file = files['input']
    result = pd.read_excel(input_file)

    del files['input']

    for file in files.values():
        file_data = pd.read_excel(file.temporary_file_path())
        file_data['external'] = file_data['external'].astype(str)
        result['value']=result['value'].astype(str)
        result = pd.merge(result, file_data, on='external', how='left')
    return result
