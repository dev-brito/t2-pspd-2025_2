#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""reducer.py - Soma contagens de palavras"""

import sys

palavra_anterior = None
count_anterior = 0

for linha in sys.stdin:
    linha = linha.strip()
    palavra, count = linha.split('\t', 1)
    
    try:
        count = int(count)
    except ValueError:
        continue
    
    if palavra == palavra_anterior:
        count_anterior += count
    else:
        if palavra_anterior:
            print('%s\t%s' % (palavra_anterior, count_anterior))
        count_anterior = count
        palavra_anterior = palavra

if palavra == palavra_anterior:
    print('%s\t%s' % (palavra_anterior, count_anterior))