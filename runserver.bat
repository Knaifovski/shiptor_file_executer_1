@echo off
chcp 65001 > NUL
echo Проверка виратуального окружения
IF EXIST "venv" (
	echo Виртуальное окружение установлено
	goto 2
) ELSE (
	echo Виртуальное окружение устанавливается
	start cmd.exe /c "python -m venv venv"
	echo Виртуальное окружение установлено
	goto 2
)
:2
echo Проверка файла подключения
IF EXIST ".env" (
	echo Файл логина создан
	goto 3
) ELSE (	
echo user=your_login > .env
echo password=your_password >> .env
echo shiptor_standby_base_host=host.standby.shiptor >> .env
echo secret_key=ВАШ_СЕКРЕТНЫЙ_КЛЮЧ >> .env
echo Заполните файл .env в соответсвии с данными для подключения - иначе корректная работа приложения невозможна
pause
)
:3
start cmd.exe /c  "git fetch https://github.com/Knaifovski/shiptor_file_executer_1.git master & cd venv\Scripts & activate & cd .. & cd .. & pip install -r requierements.txt & python manage.py runserver"

