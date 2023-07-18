# shiptor_file_executer_1
Для Поиска и ВПРа значений

Настройка:

1) запустите windows PowerShell в папке

   ![image](https://github.com/Knaifovski/shiptor_file_executer_1/assets/31153601/8518241e-cbfb-4158-80b4-99adf58719b8)

3) python -m venv venv  (установка виртуального окружения)
4) venv\Scripts\activate.ps1 (активирование окружения)
2) pip install -r requierements.txt (установка библиотек)
4) создайте файл .env
Внесите в него следующие данные

user=your_login 
password=your_password 
shiptor_standby_base_host=host.standby.shiptor 
secret_key=спросите или сгенерируйте самостоятельно  

![image](https://github.com/Knaifovski/shiptor_file_executer_1/assets/31153601/74f37360-1e8a-417b-86d4-c2d3254b6d30)

5) Создайте папку temp в папке с приложением

генерация секретного ключа:
запустите команду в открытом powershell:
1) py manage.py shell
2) from django.core.management.utils import get_random_secret_key  
3) get_random_secret_key()


Запуск через батник в папке


Ошибки:
1) выполнение сценариев отключено в этой системе.
   Решение: Открываем терминал от админа.
            Пишем и запускаем: Set-ExecutionPolicy RemoteSigned
            На вопрос отвечаем: A (Да для всех)
