#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""mapper.py - Conta ocorrências de palavras"""

import sys

for linha in sys.stdin:
    linha = linha.strip()
    palavras = linha.split()
    for palavra in palavras:
        print('%s\t%s' % (palavra, 1))