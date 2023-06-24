# shiptor_file_executer_1
Для Поиска и ВПРа значений

Настройка:

1) запустите командную строку в папке
2) python venv venv
3) создайте файл .env
Внесите в него следующие данные

user=your_login 
password=your_password 
shiptor_standby_base_host=host.standby.shiptor 
secret_key=спросите или сгенерируйте самостоятельно  

генерация секретного ключа:
запустите команду в cmd:
1) django-admin shell
2) from django.core.management.utils import get_random_secret_key  
3) get_random_secret_key()

