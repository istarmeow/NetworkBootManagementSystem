@echo off
title = Shell
if %computername% == LIURUI-HOMEPC (
	echo '����ĵ���'
	python3 manage.py shell
) else (
	echo '��˾�ĵ���'
	python manage.py shell
)

pause