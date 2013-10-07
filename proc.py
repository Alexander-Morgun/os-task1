import argparse
from random import randrange as rand
import re
import json


def dump():
    print("""
Flags = {0} {1}
POH = {2}
IR = {3}
IP = {4}
    """.format(РОН[0], РОН[1], РОН[2], ИР, IP))
    print('\n'.join([('%04X: ' % s) + ' '.join(['%02X' % i for i
          in memory[s:s + 16]]) for s in range(0, 100, 16)]))


def decode(КОП):
    ОП = wires['КОП'] >> 4
    opt = wires['КОП'] & 15
    if (ОП == 15):
        П = 4
        И = 1
        if (opt == 14):
            set_wire('перех', 1)
        elif (opt != 15):
            set_wire('перех', РОН[opt])
    else:
        П = opt & 3
        И = opt >> 2
        set_wire('перех', 0)
    return [ОП, И, П]


def read_word(addr):
    return memory[addr] << 8 | memory[addr + 1]


def set_wire(wire, value):
    wires[wire] = config[wire] and value


def choose_wire(*input, key):
    return [wires[i] for i in input][wires[key]]


parser = argparse.ArgumentParser(description=' Copyright (C) Alexander Morgun'
                                 ' <Alexander_Morgun@e1.ru>')
parser.add_argument('file', type=argparse.FileType('r'), nargs=1,
                    help='File with program for processor')
parser.add_argument('-d', action='store_true',
                    help='Print memory dump after each command')
args = parser.parse_args()
config = json.loads(open('config', mode='r').read())
t = 0
memory = [rand(255) for i in range(65535)]
for i in re.findall('(\w{2})', args.file[0].read(-1)):
    memory[t] = int(i, base=16)
    t += 1
IP = 0
wires = {'0': 0}
# флаг Пр 0x, флаг Пр x0, СУМ
РОН = [rand(255) for i in range(3)]
ИР = rand(255)
set_wire('пуск', True)
while (wires['пуск']):
    set_wire('КОП', memory[IP])
    set_wire('Адрес', read_word(IP + 1))
    [ОП, И, П] = decode(wires['КОП'])
    set_wire('пуск', wires['КОП'] != 255)
    set_wire('взап1', П == 3)
    set_wire('зам1', П == 1)
    set_wire('зам2', П != 3)
    set_wire('чист', not (П == 2 or П == 3))
    set_wire('выб', И)
    set_wire('запп', П == 0)
    set_wire('ИНД', ИР)
    set_wire('ИА', wires['ИНД'] + wires['Адрес'])
    set_wire('СП', read_word(wires['ИА']))
    set_wire('СУМ', РОН[2])
    АЛУ_вход0 = choose_wire('СП', 'ИА', 'ИНД', key='выб')
    АЛУ_вход1 = wires['СУМ']
    set_wire('РЕЗ1', {
        0: lambda x, y: y,  # WTF?!
        1: lambda x, y: x,
        2: lambda x, y: x + y,
        3: lambda x, y: y - x,
        15: lambda x, y: y,  # WTF?!
    }[ОП](АЛУ_вход0, АЛУ_вход1))
    set_wire('ПР', (wires['РЕЗ1'] == 0) << 2 | (wires['РЕЗ1'] > 0))
    if (args.d):
        dump()
    if (wires['зам1']):
        РОН = [wires['ПР'] >> 2, wires['ПР'] & 3, wires['РЕЗ1']]
    if (wires['зам2']):
        ИР = choose_wire('РЕЗ1', '0', key='чист')
    if (wires['запп']):
        memory[wires['ИА']] = wires['РЕЗ1'] >> 8
        memory[wires['ИА'] + 1] = wires['РЕЗ1'] & 255
    set_wire('АДРКОМ', IP + 3)
    if (wires['пуск']):
        IP = choose_wire('АДРКОМ', 'ИА', key='перех')
dump()
