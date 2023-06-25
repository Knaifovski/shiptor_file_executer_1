# shiptor_file_executer_1
Для Поиска и ВПРа значений

Настройка:

1) запустите windows PowerShell в папке

   ![image](https://github.com/Knaifovski/shiptor_file_executer_1/assets/31153601/8518241e-cbfb-4158-80b4-99adf58719b8)

3) python venv venv  (установка виртуального окружения)
4) venv\Scripts\activate.ps1 (активирование окружения)
2) pip install -r requirements.txt (установка библиотек)
4) создайте файл .env 
Внесите в него следующие данные

user=your_login 
password=your_password 
shiptor_standby_base_host=host.standby.shiptor 
secret_key=спросите или сгенерируйте самостоятельно  

![image](https://github.com/Knaifovski/shiptor_file_executer_1/assets/31153601/74f37360-1e8a-417b-86d4-c2d3254b6d30)


генерация секретного ключа:
запустите команду в открытом powershell:
1) django-admin shell
2) from django.core.management.utils import get_random_secret_key  
3) get_random_secret_key()


Запуск через батник в папке
