# -*- coding: utf-8 -*-
# ВУАЛЬ — уровень У0/У3/У5 в коде: чистка, триада, эхо-проверка.
# Дом Кординапс, слово Дениса 24.10. Лицензия дома.

import re

MUSOR = [
    'ЗАКАЗ:', 'ЧЕК:', 'ЧЕРНОВИК', 'ОТПРАВЛЕН 2', 'Заметки дома', 'Текст отклика',
    '##', 'Статус отправки', 'Статус:', 'Источник:', 'Сессия:', '---',
]

TRIADA_SIGNS = [
    r'занимае\w+ именно этим',
    r'основн\w+ практик\w+|основное направление',
    r'шаблон\w+|наработк\w+|готов\w+ решени\w+',
    r'подвинуться|подвинемся|гибк\w+ в цене|10\s?[-–—]%|20\s?[-–—]%',
    r'демо|показать до оплаты',
]

def clean(text: str) -> str:
    """У0: вернуть тело письма от «Здравствуйте» до подписи «Денис»."""
    if not text:
        return ''
    lines = text.splitlines()
    start = next((i for i, l in enumerate(lines) if l.strip().startswith('Здравствуйте')), None)
    if start is None:
        return ''
    end = None
    for i in range(len(lines) - 1, start, -1):
        if re.fullmatch(r'(С уважением,?\s*)?(Денис)(\s+Бусыгин)?[!.]?', lines[i].strip()):
            end = i
            break
    if end is None:
        end = len(lines) - 1
    body = '\n'.join(l.rstrip() for l in lines[start:end + 1]).strip()
    body = '\n'.join(l for l in body.splitlines() if not any(m in l for m in MUSOR))
    return body.strip()

def has_musor(text: str) -> list:
    return [m for m in MUSOR if m in text]

def is_clean(text: str) -> bool:
    if not text:
        return False
    hi = text.lstrip().startswith('Здравствуйте')
    sign = bool(re.search(r'\n\s*(С уважением,?\s*)?Денис(\s+Бусыгин)?[!.]?\s*$', text))
    return hi and sign and not has_musor(text) and 300 <= len(text) <= 5000

def triada_score(text: str) -> int:
    """У3: сколько из трёх элементов триады присутствует (0–3+)."""
    low = text.lower()
    practice = bool(re.search(TRIADA_SIGNS[0], low) or re.search(TRIADA_SIGNS[1], low))
    templates = bool(re.search(TRIADA_SIGNS[2], low))
    price = bool(re.search(TRIADA_SIGNS[3], low))
    demo = bool(re.search(TRIADA_SIGNS[4], low))
    return sum([practice, templates, price]) + (1 if demo else 0)

def passes_veil(text: str, require_triada: bool = False) -> tuple:
    """Стоп-вуаль: (вердикт, причины). Триада — мягкое правило (уместность), жёсткие — мусор/подпись/длина."""
    fails = []
    c = clean(text)
    if not c:
        fails.append('нет тела (Здравствуйте…Денис)')
    if c and not is_clean(c):
        if not c.lstrip().startswith('Здравствуйте'):
            fails.append('нет приветствия')
        if not re.search(r'Денис', c):
            fails.append('нет подписи')
        if has_musor(c):
            fails.append('мусор: ' + ', '.join(has_musor(c)))
        if len(c) < 300:
            fails.append(f'коротко: {len(c)} < 300')
        if len(c) > 5000:
            fails.append(f'длинно: {len(c)} > 5000')
    if require_triada and triada_score(c) < 2:
        fails.append(f'триада слабая: {triada_score(c)}/4 (нужно ≥2)')
    return (not fails, fails)

def echo_ok(sent_text: str, intended_text: str) -> tuple:
    """У5: живое эхо — отправленное совпадает с задуманным (без служебного)."""
    a, b = clean(sent_text), clean(intended_text)
    return (a == b and bool(a), 'совпадает' if a == b and a else 'расхождение')
