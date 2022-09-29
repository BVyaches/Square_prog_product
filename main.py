from math import sqrt
from cmath import sqrt as csqrt
from re import fullmatch
from googletrans import Translator, LANGCODES
from sympy import sqrt as ssqrt

trans = Translator()
database = {}


def simple_sqrt(num):
    return '+-' + str(sqrt(float(num)))


def complex_sqrt(num):
    return str(csqrt(complex(num))).replace('(', '').replace(')', '')


def simplify_sqrt(num):
    if 'sin' in num:
        return '|cos(x)|'
    if 'cos' in num:
        return '|sin(x)|'
    if '**' in num or '^' in num:
        new_form = num.replace('**', '^').split('^')
        try:
            if len(new_form) == 2:
                if new_form[1] == '2':
                    if new_form[0].replace('-', '').isdigit():
                        if '.' not in new_form[0]:
                            return f'{abs(int(new_form[0]))}'
                        else:
                            return f'{abs(float(new_form[0]))}'
                    else:
                        return f'|{new_form[0]}|'
                else:
                    if int(new_form[1]) % 2 == 0 and int(new_form[1]) == float(new_form[1]):
                        return f'{new_form[0]}**{int(new_form[1])//2}'

        except :
            pass
    try:
        let = num.replace('^', '**').split('**')
        x = 1
        result = ssqrt(int(let[0]) ** x)
        if 'sqrt' not in result.__str__():
            return f'{result}**{let[-1]}'
        return False
    except:
        return False


def sfu_sqrt(values):
    return f'|{values[0]} {values[2]} {values[1]}|'


def set_accuracy(result, sign):
    if '.' not in result:
        return result
    try:
        before_dot, after_dot = result.split('.')
        after_dot = '.' + after_dot[:sign]
        if 'j' in result and 'j' not in after_dot:
            after_dot += 'j'

        return before_dot + after_dot
    # Для комплексных чисел
    except ValueError:
        return result


def auto_check_type(message):
    if message == '0':
        return '0'
    message = message.replace(',', '.').replace('i', 'j')
    # Стандартная форма целого или вещественного числа с или без экспоненты
    num_re = r'((\d+\.\d+)|\d+)\s*(\s*\*\s*|\s*)(((E|e)\s*\+\s*\d|(E|e)\d)|\s*)'
    number = fullmatch(num_re, message)
    complex_num = fullmatch(rf'\-{num_re}', message)
    # Проверка на комплексное число
    if fullmatch(rf'{num_re}j', message):
        complex_num = True
    # Проверка на степенные выражения и следствие основного тригонометрического тождества
    simplify_num = fullmatch(r'(\w|\d+)((\^)|(\*\*))\d+', message) or fullmatch(r'\(*(\d+)\)*(\*\*|^)(\w|\d+)',
                                                                                message) \
                   or fullmatch(r'1\s*-\s*(sin|cos)(\*\*|\^)2\s*\((\w|\d+)\)', message)
    # Проверка числа на соотвестие формуле a^2+2ab+b^2
    sfu_num = fullmatch(r'(\w|\d+)((\^)|(\*\*))2 \s* (\+|\-) \s* 2(\s*|\s*\*\s*) '
                        r'((\d+\s*\*\s*\d+)|(\w(\s*|\s*\*\s*)\w)) \s* (\+) \s* (\w|\d+)((\^)|(\*\*))2'.replace(' ', ''),
                        message)

    if number:
        return simple_sqrt(message)
    if complex_num:
        return complex_sqrt(message)
    if simplify_num:
        return simplify_sqrt(message)
    if sfu_num:
        # Проверяем, есть ли аргументы a и b в ab
        if sfu_num[7] in [sfu_num[1] + sfu_num[12], sfu_num[1] + '*' + sfu_num[12], sfu_num[1] + ' * ' + sfu_num[12]]:
            return sfu_sqrt((sfu_num[1], sfu_num[12], sfu_num[5]))

    return False


def translate_to_users_lang(answer_text, message):
    user_id = message.from_user.id
    users_lang = message.from_user.language_code

    try:
        # Если язык уже указывал язык принудительно, переводим на него
        if database.get(user_id):
            result = trans.translate(answer_text, dest=database.get(user_id), src='ru').text
        else:
            # Иначе, переводим на язык, по которому зарегистрирован аккаунт пользователя
            result = trans.translate(answer_text, dest=users_lang, src='ru').text
    except ValueError:
        return False

    return result

print(simplify_sqrt('25**15'))
