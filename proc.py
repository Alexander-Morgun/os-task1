import argparse
import random
import re
import json


def dump():
    print("""
POH = {0}
IR = {1}
IP = {2}
    """.format('|'.join([str(int(i)) for i in РОН]), ИР, IP))
    print('\n'.join([('%04X: ' % s) + ' '.join(['%02X' % i for i
          in memory[s:s + 16]]) for s in range(0, 100, 16)]))

parser = argparse.ArgumentParser(description=' Copyright (C) Alexander Morgun'
                                 ' <Alexander_Morgun@e1.ru>')
parser.add_argument('file', type=argparse.FileType('r'), nargs=1,
                    help='File with program for processor')
parser.add_argument('-d', action='store_true',
                    help='Print memory dump after each command')
args = parser.parse_args()
config = json.loads(open('config', mode='r').read())
t = 0
memory = [random.randrange(255) for i in range(65535)]
for i in re.findall('(\w{2})', args.file[0].read(-1)):
    memory[t] = int(i, base=16)
    t += 1
IP = 0
# флаг Пр 0x, флаг Пр x0, СУМ
РОН = [random.randrange(255) for i in range(3)]
ИР = random.randrange(255)
пуск = config['пуск'] and True
while (пуск):
    КОП = config['КОП'] and memory[IP]
    Адрес = config['А'] and (memory[IP + 1] * 256 + memory[IP + 2])
    ОП = КОП // 16
    перех = 0
    if (ОП == 15):
        П = 4
        И = 1
        if (КОП % 16 == 14):
            перех = 1
        elif (КОП % 16 != 15):
            перех = РОН[КОП % 16]
    else:
        П = int(КОП % 16) % 4
        И = (КОП % 16) // 4
    перех = config['перех'] and перех
    пуск = config['пуск'] and КОП != 255
    взап1 = config['взап1'] and П == 3
    зам1 = config['зам1'] and П == 1
    зам2 = config['зам2'] and П != 3
    чист = config['чист'] and not (П == 2 or П == 3)
    выб = config['выб'] and И
    запп = config['запп'] and П == 0
    # print("{0}:{1} {2} {3} {4}".format(КОП, ОП, И, П, Адрес))
    ИНД = config['ИНД'] and ИР
    ИА = config['ИА'] and (ИНД + Адрес)
    СП = memory[ИА] * 256 + memory[ИА + 1]
    АЛУ_вход0 = [СП, ИА, ИНД][выб]
    # print("[{0} {1} {2}][{3}]".format(СП, ИА, ИНД, выб))
    СУМ = config['СУМ'] and РОН[2]
    АЛУ_вход1 = СУМ
    РЕЗ1 = config['РЕЗ1'] and {
        0: lambda x, y: y,  # WTF?!
        1: lambda x, y: x,
        2: lambda x, y: x + y,
        3: lambda x, y: y - x,
        15: lambda x, y: y,  # WTF?!
    }[ОП](АЛУ_вход0, АЛУ_вход1)
    ПР = [config['ПР'] and РЕЗ1 == 0, config['ПР'] and РЕЗ1 > 0]
    if (args.d):
        dump()
    if (зам1):
        РОН[:2] = ПР
        РОН[2] = РЕЗ1
    if (зам2):
        ИР = [РЕЗ1, 0][чист]
    if (запп):
        memory[ИА] = (РЕЗ1 // 256) % 256
        memory[ИА + 1] = РЕЗ1 % 256
    IP += 3
    if (пуск):
        IP = [IP, ИА][перех]
dump()
