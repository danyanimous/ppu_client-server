import serial
import time
from datetime import datetime
import socket

ppu = serial.Serial('COM1', 19200) #подключаемся к принтеру по COM-порту
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#КОМАНДЫ
fullcut = b'\x1D\x56\x00'
printfeed = b'\x1B\x4A\x00'
init = b'\x1B\x40'
font_a = b'\x1B\x4D\x49'
normal_size = b'\x1D\x21\x00' #максимум символов в строке (включая пробелы) - 51
title_size = b'\x1D\x21\x11' #максимум символов в строке (включая пробелы) - 24
underline_on = b'\x1B\x2D\x02'
underline_off = b'\x1B\x2D\x00'

#ЗАГОТОВКИ
asterisks = b'**************************************************\x0d\x0a'
nextline = b'\x0d\x0a'


#СЛОВАРЬ ДЛЯ КАСТОМНОГО ШРИФТА. Значит, мы представляем каждое русское (кириллическое) слово (будь то наименование товара или ФИО кассира) как массив,
#после чего ищем каждую его букву в первом массиве, получаем её индекс и добавляем в сообщение непосредственно для принтера то, что стоит под тем же
#индексом во втором массиве
dict_cyr = ["А", "Б", "В", "Г", "Д", "Е", "Ё", "Ж", "З", "И", "Й", "К", "Л", "М", "Н", "О",
            "П", "Р", "С", "Т", "У", "Ф", "Х", "Ц", "Ч", "Ш", "Щ", "Ъ", "Ы", "Ь", "Э", "Ю",
            "Я", "а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м", "н",
            "о", "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э",
            "ю", "я"] #массив из кириллических букв
dict_hex = [b'\x80', b'\x81', b'\x82', b'\x83', b'\x84', b'\x85', b'\x86', b'\x87', b'\x88', b'\x89', b'\x8a', b'\x8b', b'\x8c', b'\x8d', b'\x8e', b'\x8f',
                      b'\x90', b'\x91', b'\x92', b'\x93', b'\x94', b'\x95', b'\x96', b'\x97', b'\x98', b'\x99', b'\x9a', b'\x9b', b'\x9c', b'\x9d', b'\x9e', b'\x9f',
                      b'\xa0', b'\xa1', b'\xa2', b'\xa3', b'\xa4', b'\xa5', b'\xa6', b'\xa7', b'\xa8', b'\xa9', b'\xaa', b'\xab', b'\xac', b'\xad', b'\xae', b'\xaf',
                      b'\xb0', b'\xb1', b'\xb2', b'\xb3', b'\xb4', b'\xb5', b'\xb6', b'\xb7', b'\xb8', b'\xb9', b'\xba', b'\xbb', b'\xbc', b'\xbd', b'\xbe', b'\xbf',
                      b'\xc0', b'\xc1'] #массив из тех же букв, закодированых для кастомного шрифта

print('Вас приветствует POS принт-сервер v1.1-release!')
ppu.write(init)
time.sleep(0.2)
ppu.write(font_a)
sock.bind(('', 9044))
sock.listen(1)
print('Принтер проинициализирован. Сервер готов к работе.')

def cyrhex(sentence):
    for letter in list(sentence): #представляем наименование как массив и берём по букве оттуда
        if letter == " ": #если попался пробел, то отправляем его на принтер как есть
            ppu.write(b" ")
        elif letter == "`": #если попалась вот такая поеба, то переносим строку
            ppu.write(nextline)
        elif letter in dict_cyr: #если букву удалось найти в кириллическом словаре
            indx = dict_cyr.index(letter) #узнаём, на какой позиции (индексе) в словаре эта буква находится
            ppu.write(dict_hex[indx]) #а затем отправляем на принтер байт под таким же индексом
        else: #если символ оказался НЕ пробелом и НЕ был найден среди кириллических, то вероятнее всего это латынь либо цифры
            ppu.write(str.encode(str(letter))) #отправляем на принтер их как есть

def print_header(header_contents):
    time.sleep(0.5)
    ppu.write(title_size) #задаём большой размер букав
    time.sleep(0.2)
    spaces = int(24 - len(header_contents)) // 2 #вычисляем, сколько пробелов нужно вставить перед заголовком, чтобы он получился по центру: макс. ширина - длина заголовка / 2 (окр. в меньш. стор.)
    i = 0
    while i < spaces: #если при делении получится отрицательное число (длина заголовка не влазит на одну строку), то отступа просто не будет
        ppu.write(b' ')
        i += 1
    cyrhex(header_contents) #переводим заголовок в понятные для принтера байты
    ppu.write(nextline)
    time.sleep(0.2)
    ppu.write(normal_size) #поскольку мы хорошие парни, возвращаем размер букав обратно на обычный
    ppu.write(asterisks) #и фигачим строку, полную звёздочек
    #ppu.write(nextline) #после себя оставляем порядок и переносим каретку на новую строку

def print_body(body_contents):
    cyrhex(body_contents) #переводчик
    ppu.write(nextline) #после себя оставляем порядок и переносим каретку на новую строку

def print_footer(footer_contents):
    time.sleep(0.5)
    ppu.write(normal_size) #на всякий случай, задаём снова обычный размер букв
    ppu.write(asterisks) #и фигачим строку, полную звёздочек
    #ppu.write(nextline)
    ppu.write(title_size) #далее, идём на новую строку и задаём большой размер букав для самой концовки
    time.sleep(0.3)
    spaces = int(24 - len(footer_contents)) // 2 #вычисляем, сколько пробелов нужно вставить перед текстом, чтобы он получился по центру: макс. ширина - длина концовки / 2 (окр. в меньш. стор.)
    i = 0
    while i < spaces: #если при делении получится отрицательное число (длина концовки не влазит на одну строку), то отступа просто не будет
        ppu.write(b' ')
        i += 1
    cyrhex(footer_contents) #переводим концовку в понятные для принтера байты

def finish_job(): #прокатываем и отрезаем бумагу
    ppu.write(nextline) #на всякий случай хуярим ещё несколько строк, поскольку принтер любит отрезать чек раньше нужного
    ppu.write(nextline)
    ppu.write(nextline)
    ppu.write(printfeed) #только после этой команды весь текст из буфера будет напечатан (хотя если буфер был переполнен, то текст печатается сразу для его очистки)
    ppu.write(fullcut) #отрезаем чек и (на уровне прошивки принтера) выдаём его
    print('Задание успешно выполнено!')

while True: #циклично принимаем соединения, получаем данные и печатаем их всех
    print('Ожидается подключение по TCP на порту 9044...')
    client, addr = sock.accept()
    print('Установлено подключение с клиентом', addr,'. Ожидается заголовок чека.')
    header_len = client.recv(4).decode('Windows-1251')
    client.send(str('ENTER TITLE').encode('Windows-1251'))
    print('Клиент отправляет заголовок чека длиной', header_len, 'символов...')
    header = client.recv(int(header_len)).decode('Windows-1251')
    print('Заголовок получен. Ожидается тело чека.')
    body_len = client.recv(4).decode('Windows-1251')
    client.send(str('ENTER BODY').encode('Windows-1251'))
    print('Клиент отправляет тело чека длиной', body_len, 'символов...')
    body = client.recv(int(body_len)).decode('Windows-1251')
    print('Тело чека получено. Ожидается концовка чека.')
    client.send(str('NEED FOOTER?').encode('Windows-1251')) #спрашиваем, нужно ли печатать концовку
    need_of_footer = client.recv(1).decode('Windows-1251') #ждём либо Y либо N
    if need_of_footer == 'Y':
        footer_len = client.recv(4).decode('Windows-1251') #узнаём длину концовки и просим выслать её
        client.send(str('ENTER FOOTER').encode('Windows-1251'))
        print('Клиент отправляет концовку чека длиной', footer_len, 'символов...')
        footer = client.recv(int(footer_len)).decode('Windows-1251') #получаем концовку заранее указанной длины
        print('Концовка чека получена. Соединение с клиентом закрыто.')
    else:
        print('Клиент отказался от печати концовки чека. Соединение с клиентом закрыто')
    client.shutdown(socket.SHUT_WR)
    print('Задание печати отправлено на принтер, ожидается его выполнение...')
    print_header(header)
    print_body(body)
    if need_of_footer == 'Y':
        print_footer(footer)
    else:
        pass
    finish_job()
