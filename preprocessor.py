# -*- coding: utf-8 -*-

from sys import argv
import os

flags_inv = {'z': 'nz', 'nz': 'z', 'c': 'nc', 'nc': 'c', 'p': 'm', 'm': 'p',
             'pe': 'po', 'po': 'pe'}

reg_pair = {'a': 'af', 'b': 'bc', 'c': 'bc', 'd': 'de', 'e': 'de', 'h': 'hl',
            'l': 'hl', 'ixl': 'ix', 'ixh': 'ix', 'iyl': 'iy', 'iyh': 'iy',
            'bc': 'bc', 'de': 'de', 'hl': 'hl', 'ix': 'ix', 'iy': 'iy'}


def process_file(in_fname, out_fname, function):
    with open(in_fname) as in_file:
        lines = read_lines(in_file)
        lines = function(lines)
        with open(out_fname, 'w') as out_file:
            write_out_file(lines, out_file)


def read_lines(in_file):
    lines = []
    for line in in_file.readlines():
        lines.append(line)
    return lines


def write_out_file(lines, out_file):
    for line in lines:
        out_file.write(line)


def preprocessor(lines):
    lines = make_includes(lines)
    macro_data = collect_macrofunctions(lines)
    delete_definitions(lines)
    make_replaces(lines, macro_data)
    process_bool_functions(lines)
    lines = process_for_loops(lines)
    return lines


def process_for_loops(lines):
    for n in range(42):  # max loop nesting
        new_lines = process_for_loop(lines)
        if hash(tuple(new_lines)) == hash(tuple(lines)):
            break
        lines = new_lines
    return lines


def process_for_loop(lines):
    state = bracket_level = prev_level = from_val = to_val = step = 0
    reg = ''
    ans = []
    for line in lines:
        bracket_level = update_bracket_level(bracket_level, line, '{}')
        if state == 0 and line.lstrip().startswith('for'):
            state = 1
            reg, from_val, to_val, step, line = for_loop_args(line)
        if state == 1 and bracket_level == prev_level + 1:
            state = 2
            line = line.replace('{', '', 1)
            if line.strip():
                ans.append(line)
        elif state == 2:
            state = 3
            for_loop_insert_head(ans, line, reg, from_val, step)
        elif state == 3 and bracket_level == prev_level - 1:
            state = 0
            ans += for_loop_insert_tail(line, reg, to_val, step)
        else:
            ans.append(line)
        if state <= 2:
            prev_level = bracket_level
    return ans


def for_loop_insert_head(ans, line, reg, from_val, step):
    ans.append('    ' + reg + ' = ' + str(from_val) + ';\n')
    ans.append('    do {\n')
    ans.append('        push(' + reg_pair[reg] + ');\n')
    ans.append(line)


def for_loop_insert_tail(line, reg, to_val, step):
    ans = line.split('}', 1)
    ans[0] += ('\n')
    ans.append(8*' ' + 'pop(' + reg_pair[reg] + ');\n')
    ans.append(for_loop_update_counter(reg, step))
    acc = 'hl' if reg_pair[reg] == reg else 'a'
    if step > 0:
        ans.append(8*' ' + acc + ' = ' + str(to_val) + ';\n')
        ans.append(8*' ' + acc + ' -= ' + reg + ';\n')
        ans.append('    } while (flag_nc);\n')
    else:
        ans.append(8*' ' + acc + ' = ' + reg + ';\n')
        if acc != 'hl':
            ans.append(8*' ' + acc + ' -= ' + str(to_val) + ';\n')
        else:
            ans.append(8*' ' + 'push(' + reg + '); ' + reg + ' = ' +
                       str(to_val) + '; hl -= ' + reg + '; pop(' + reg + ');')
        ans.append('    } while (flag_p);\n')
    ans.append(ans.pop(1))
    return ans


def for_loop_update_counter(reg, step):
    rement = ['--', '++']
    ans = ''
    if abs(step) <= 3:
        for i in range(abs(step)):
            ans += 8*' ' + reg + rement[step > 0] + ';\n'
        return ans
    if reg_pair[reg] != reg:
        ans += 8*' ' + 'a = ' + reg + '; a += ' + str(step) + \
            '; ' + reg + ' = a;'
    else:
        if step > 0:
            ans += 8*' ' + 'hl = ' + str(step) + '; hl += ' + reg + '; ' + \
                reg + ' = hl;\n'
        else:
            ans += 8*' ' + 'hl = ' + reg + '; ' + reg + ' = ' + str(-step) + \
                '; hl -= ' + reg + '; ' + reg + ' = hl;\n'
    return ans + '\n'


def update_bracket_level(bracket_level, line, symbols='()'):
    state = 0
    prev_chr = ''
    for chr in line:
        if state == 0 and chr == symbols[0]:
            bracket_level += 1
        elif state == 0 and chr == symbols[1]:
            bracket_level -= 1
        elif state == 0 and chr == "'":
            state = 1
        elif state == 1 and chr == "'" and prev_chr != '\\':
            state = 0
        if state == 0 and chr == '"':
            state = 2
        elif state == 2 and chr == '"' and prev_chr != '\\':
            state = 0

        prev_chr = chr
    return bracket_level


def for_loop_args(line):
    reg = line.split('=')[0].split()[-1]
    assert reg not in ('a', 'hl'), 'Wrong loop counter'
    splt = line.split(':')
    from_val = int(splt[0].strip().split('=')[-1])
    to_val = int(splt[1].strip().split()[0])
    step = int(splt[2].strip().split()[0]) if len(splt) == 3 else \
        (1 if to_val > from_val else -1)
    assert sgn(to_val - from_val) == sgn(step), 'Wrong step in for loop'
    new_line = remove_for_loop(line)
    return reg, from_val, to_val, step, new_line


def remove_for_loop(line):
    last_arg = line.rfind(':')
    for i, x in enumerate(line[last_arg + 1:].lstrip()):
        if x == '-' or x.isdigit():
            continue
        return line[last_arg + i + 2:]
    return []


def make_includes(lines):
    new_lines = []
    for line in lines:
        if line.lstrip().startswith('#include'):
            fname = line.split('"')[1]
            add_source_include(lines, fname)
            with open(fname) as file:
                add_lines = read_lines(file)
                for add_line in add_lines:
                    new_lines.append(add_line)
        else:
            new_lines.append(line)
    return new_lines


def add_source_include(lines, fname):
    S = fname.split('.')
    if len(S) > 0 and S[1].lower() == 'h' and os.path.exists(S[0] + '.c'):
        lines.append('#include "' + S[0] + '.c"')


class macro_params:
    def __init__(self, name='', body=''):
        self.name = name
        self.arg_names = []
        self.arg_values = []
        self.body = body


def collect_macrofunctions(lines):
    macro_data = []
    for i, line in enumerate(lines):
        if line.strip() and is_define_or_enum(line):
            fill_macro_data(connect_lines(lines[i:]), macro_data)
    return macro_data


def is_define_or_enum(line):
    return line.strip() and split_str(line.strip())[0] in ('#define', '#enum')


def fill_macro_data(line, m_data):
    fill_define(line, m_data) if '#def' in line else fill_enum(line, m_data)


def fill_define(line, macro_data):
    macro = fill_macro_name(line)
    fill_macro_args_and_defaults(line, macro)
    fill_macro_body(line, macro)
    macro_data.append(macro)


def fill_enum(line, macro_data):
    names, values = get_args_and_values(line)
    complete_enum_values(values)
    for name, val in zip(names, values):
        macro_data.append(macro_params(name=name, body=val))


def complete_enum_values(values):
    for i, val in enumerate(values):
        if val == '':
            values[i] = 0 if i == 0 else str(int(values[i - 1]) + 1)


def connect_lines(lines):
    connected = ''
    for line in lines:
        connected += line[:-1]
        if connected[-1] != '\\':
            return connected.replace('\\', '').strip()


def fill_macro_name(line):
    ans = macro_params()
    ans.name = line.replace('(', ' ').split()[1]
    return ans


def fill_macro_args_and_defaults(line, macro_data):
    macro_data.arg_names, macro_data.arg_values = get_args_and_values(line)


def get_args_and_values(line):
    raw_arg_list = line.partition('(')[2].partition(')')[0].split(',')
    ans = []
    for raw_arg in raw_arg_list:
        ans.append([x.strip() for x in raw_arg.partition('=')[::2]])
    ans = tuple(map(list, zip(*ans)))  # transpose list of lists
    return ans[0] if ans[0] != [''] else [], ans[1] if ans[1] != [''] else []


def fill_macro_body(line, macro):
    T = split_str(line, ' ()')
    macro.body = line.partition(')')[2].strip() if ')' in T else ''.join(T[4:])


def make_replaces(lines, macro_data):
    for macro in macro_data:
        replace_in_text(lines, macro)


def replace_in_text(lines, macro):
    for i, line in enumerate(lines):
        lines[i] = replace_in_line(split_str(line), macro)


def replace_in_line(tokens, macro):
    for i, tok in enumerate(tokens):
        if tok == macro.name:
            tokens[i] = get_new_body(macro, tokens[i + 1:])
            if macro.arg_names:
                delete_parentheses(tokens, i + 1)
    return ''.join(tokens)


def get_new_body(macro, tokens):
    if not macro.arg_names:
        return macro.body
    update_arg_values(tokens, macro)
    body_tokens = split_str(macro.body)
    return replace_tokens(macro, body_tokens)


def delete_parentheses(tokens, index):
    for i, tok in enumerate(tokens):
        if i < index or tok != ')':
            continue
        break
    del(tokens[index: i + 1])


def replace_tokens(macro, body_tokens):
    for arg_i, arg in enumerate(macro.arg_names):
        for tok_i, tok in enumerate(body_tokens):
            if tok == arg:
                body_tokens[tok_i] = macro.arg_values[arg_i]
    return ''.join(body_tokens)


def update_arg_values(tokens, macro):
    for i, tok in enumerate(tokens):
        for arg_i, arg in enumerate(macro.arg_names):
            if tok == arg and tokens[i + 1] == '=':
                macro.arg_values[arg_i] = tokens[i + 2]


def delete_definitions(lines):
    lines_nums = get_line_nums_to_delete(lines)
    delete_lines(lines, lines_nums)


def get_line_nums_to_delete(lines):
    state = 0
    lines_to_delete = []
    for i, line in enumerate(lines):
        if state == 0 and is_define_or_enum(line):
            lines_to_delete.append(i)
            if line.strip().endswith('\\'):
                state = 1
        elif state == 1:
            lines_to_delete.append(i)
            if not line.strip().endswith('\\'):
                state = 0
    return lines_to_delete


def delete_lines(lines, line_nums):
    for line_num in line_nums[::-1]:
        del(lines[line_num])


def split_str(line, separators='\t .,;+-*/=[](){}'):
    ans = []
    new_line = line
    while new_line:
        new_line = split_str_loop(new_line, separators, ans)
    return ans


def split_str_loop(new_line, separators, ans):
    (before, sep, after) = partition_str(new_line, separators)
    ans += [sep] if not before else [before, sep] if sep else [before]
    return after


def partition_str(line, separators):
    for i, char in enumerate(line):
        for sep in separators:
            if char == sep:
                return (line[:i], line[i], line[i+1:])
    return (line, None, None)


def process_bool_functions(lines):
    foo_data = collect_func_data(lines)
    replace_bool_func_ifs(lines, foo_data)
    replace_bool_with_void(lines)
    delete_bool_returns(lines)


def collect_func_data(lines):
    ans = {}
    for num, line in enumerate(lines):
        splt = line.split()
        if splt == [] or splt[0] not in ('void', 'bool'):
            continue
        return_type = '' if splt[0] == 'void' else get_return_type(lines, num)
        ans[splt[1].split('(')[0]] = (splt[0], return_type)
    return ans


def get_return_type(lines, first_line_num):
    ans = ''
    last_num = last_line_num(lines, first_line_num)
    for i in range(last_num, first_line_num, -1):
        splt = lines[i].split()
        if splt[0] == 'return':
            ans = splt[1].split(';')[0]
    return ans


def last_line_num(lines, first_line_num):
    brace_level = 0
    for i, line in enumerate(lines[first_line_num::]):
        for char in line:
            if char == '{':
                brace_level += 1
            elif char == '}' and brace_level == 1:
                break
            elif char == '}':
                brace_level -= 1
        if char == '}' and brace_level == 1:
            break
    return i + first_line_num


def replace_bool_func_ifs(lines, foo_data):
    for num, line in enumerate(lines):
        if line.split() != [] and line.split()[0].startswith('if'):
            foo_name = line.split('(')[1].lstrip('!')
            if foo_name in foo_data:
                n_spaces = len(line) - len(line.lstrip()) if num > 0 else 0
                foo_call = line.split('(', 1)[1][:-2].lstrip('!')
                reverse = line.split('(')[1].startswith('!')
                flag = foo_data[foo_name][1]
                if reverse:
                    flag = flags_inv[flag]
                lines[num] = ' ' * n_spaces + foo_call + ';\n' + \
                    ' ' * n_spaces + 'if(flag_' + flag + ')\n'


def replace_bool_with_void(lines):
    for num, line in enumerate(lines):
        if line.startswith('bool'):
            lines[num] = 'void' + line[4:]


def delete_bool_returns(lines):
    for num, line in enumerate(lines):
        sp = line.split()
        if len(sp) > 1 and sp[0] == 'return' and \
                sp[1].split(';')[0] in flags_inv:
            lines[num] = '\n'


def sgn(x):
    return -1 if x < 0 else (1 if x > 0 else 0)


if __name__ == '__main__':
    process_file(argv[1], argv[2], preprocessor)
