import socket

sock = socket.socket()
sock.connect(('192.168.0.5', 9044))
print('Версия клиента: v1.1-release. Соединение с принт-сервером установлено.')

receipt_title = input('Введите заголовок для чека...\n')
sock.send(str(len(receipt_title)).encode('Windows-1251'))
response = sock.recv(16).decode('Windows-1251')
if response == 'ENTER TITLE':
    sock.send(receipt_title.encode('Windows-1251'))
    print('Заголовок успешно отправлен на сервер.')
else:
    print('Произошла ошибка: сервер не дал ответа о готовности. Программа завершает свою работу.')

receipt_body = input('Хорошо. Теперь введите тело чека, для переноса строки используйте символ "`"...\n')
sock.send(str(len(receipt_body)).encode('Windows-1251'))
response = sock.recv(16).decode('Windows-1251')
if response == 'ENTER BODY':
    sock.send(receipt_body.encode('Windows-1251'))
    print('Тело чека успешно отправлено на сервер.')
else:
    print('Произошла ошибка: сервер не дал ответа о готовности. Программа завершает свою работу.')

response = sock.recv(16).decode('Windows-1251') #после отправки тела чека ждём от сервера вопрос о концовке
if response == 'NEED FOOTER?':
	need_of_body = input('Печатать концовку чека будем? [Y/N]\n')
	if need_of_body == 'Y' or need_of_body == 'y':
		print('...будем')
		sock.send(str('Y').encode('Windows-1251'))
		receipt_footer = input('Введите концовку для чека...\n')
		sock.send(str(len(receipt_footer)).encode('Windows-1251'))
		response = sock.recv(16).decode('Windows-1251')
		if response == 'ENTER FOOTER':
			sock.send(receipt_footer.encode('Windows-1251'))
			print('Концовка чека успешно отправлена на сервер.')
		else:
			print('Произошла ошибка: сервер не дал ответа о готовности. Программа завершает свою работу.')
	else:
		print('...не будем')
		sock.send(str('N').encode('Windows-1251'))
else:
	print('Произошла ошибка: сервер не спросил о необходимости печати концовки. Программа завершает свою работу.')

print('Задание печати успешно создано! Ожидайте чек.')
