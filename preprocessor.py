# -*- coding: utf-8 -*-


from sys import argv
import os
from re import sub, search

flags_inv = {'z': 'nz', 'nz': 'z', 'c': 'nc', 'nc': 'c', 'p': 'm', 'm': 'p',
             'pe': 'po', 'po': 'pe'}

reg_pair = {'a': 'af', 'b': 'bc', 'c': 'bc', 'd': 'de', 'e': 'de', 'h': 'hl',
            'l': 'hl', 'ixl': 'ix', 'ixh': 'ix', 'iyl': 'iy', 'iyh': 'iy',
            'bc': 'bc', 'de': 'de', 'hl': 'hl', 'ix': 'ix', 'iy': 'iy'}

common_replaces = {r'(\s)([bcdehl]{1}) ([\+\-\^&|]{1})= ([a-zA-z0-9]+)':
                   r'\1a = \2; a \3= \4; \2 = a',
                   r'(\s)([bcdehl]{1}) ([<>]{2})= ([a-zA-z0-9]+)':
                   r'\1a = \2; a \3= \4; \2 = a',
                   }


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
    lines = format_code(lines)
    replace_brackets(lines)
    move_variables_to_end(lines)
    macro_data = collect_macrofunctions(lines)
    delete_definitions(lines)
    make_replaces_macro(lines, macro_data)
    process_bool_functions(lines)
    lines = process_for_loops(lines)
    check_function_args(lines)
    lines = make_replaces_common(lines)
    return lines


def format_code(lines):
    lines = format_carriage_return(lines)
    lines = split_by_semicolon(lines)
    lines = format_braces(lines)
    # lines = format_indent(lines)
    return lines


def format_braces(lines):
    new_lines = []
    for line in lines:
        ix = find_signifficant_symbols(line, '{}')
        if not ix:
            new_lines.append(line)
            continue
        new_lines += split_by_indices(line, ix, separate=True)
    return new_lines


def split_by_indices(line, indices, keep_separators=True, separate=False):
    if keep_separators:
        ix = [0] + [x + (0 if separate else 1) for x in indices]
        ans = [line[i:j] for i, j in zip(ix, ix[1:] + [None]) if line[i:j]]
        line_nums_to_delete = []
        for i, lin in enumerate(ans):
            if lin == '\n':
                line_nums_to_delete.append(i)
            elif lin[-1] != '\n':
                ans[i] += '\n'
        delete_lines(ans, line_nums_to_delete)
        return ans
    elif indices:
        ix = [0] + indices
        ans = [line[i:j-1] for i, j in zip(ix, ix[1:] + [None]) if line[i:j-1]]
        return ans
    else:
        return [line]


def find_signifficant_symbols(line, symbols):
    pos = []
    prev_sym = ''
    state = 0
    for i, sym in enumerate(line):
        if state == 0 and sym == prev_sym == '/':
            break
        elif state == 0 and sym == '"':
            state = 1
            continue
        elif state == 1 and sym == '"':
            state = 0
            continue
        elif state == 0 and sym == "'":
            state = 2
            continue
        elif state == 2 and sym == "'":
            state = 0
            continue
        elif state == 0 and sym in symbols:
            pos.append(i)
        prev_sym = sym
    return pos


def format_carriage_return(lines):
    lines_to_delete = []
    for i, line in enumerate(lines):
        st = line.split('//')[0].strip()
        if i == 0 or not st or lines[i - 1].rstrip().endswith('\\') or \
                st.startswith(('#', '{', 'void', 'bool', '//')) or \
                st.endswith((';', '{', '}')):
            continue
        if lines[i + 1].strip() not in ('break;', 'continue;'):
            lines_to_delete.append(i + 1)
    for i in sorted(lines_to_delete, reverse=True):
        lines[i - 1] = lines[i - 1].rstrip() + ' ' + lines[i].lstrip()
        del(lines[i])
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
            reg, from_val, to_val, step, not_push = for_loop_args(line)
            line = ''
        if state == 1 and bracket_level == prev_level + 1:
            state = 2
            line = line.replace('{', '', 1)
            if line.strip():
                ans.append(line)
        elif state == 2:
            state = 3
            for_loop_insert_head(ans, line, reg, from_val, step, not_push)
        elif state == 3 and bracket_level == prev_level - 1:
            state = 0
            ans += for_loop_insert_tail(line, reg, to_val, step, not_push)
        else:
            ans.append(line)
        if state <= 2:
            prev_level = bracket_level
    return ans


def for_loop_insert_head(ans, line, reg, from_val, step, not_push):
    ans.append('    ' + reg + ' = ' + str(from_val) + ';\n')
    ans.append('    do {\n')
    if not not_push:
        ans.append('        push(' + reg_pair[reg] + ');\n')
    ans.append(line)


def for_loop_insert_tail(line, reg, to_val, step, not_push):
    ans = line.split('}', 1)
    ans[0] += ('\n')
    if not not_push:
        ans.append(8*' ' + 'pop(' + reg_pair[reg] + ');\n')
    ans.append(for_loop_update_counter(reg, step))
    acc = 'hl' if reg_pair[reg] == reg else 'a'
    if step > 0:
        ans.append(8*' ' + acc + ' = ' + str(to_val) + ';\n')
        if acc == 'hl':
            ans.append(8*' ' + 'asm("    sbc hl, ' + reg + '");\n')
        else:
            ans.append(8*' ' + acc + ' -= ' + reg + ';\n')
        ans.append('    } while (flag_nc);\n')
    elif step != -1 or to_val != 1:
        ans.append(8*' ' + acc + ' = ' + reg + ';\n')
        if acc == 'a':
            ans.append(8*' ' + acc + ' -= ' + str(to_val) + ';\n')
        elif acc == 'hl':
            ans.append(8*' ' + 'push(' + reg + '); ' + reg + ' = '
                       + str(to_val) + '; asm("    sbc hl, ' + reg +
                       '"); pop(' + reg + ');')
        ans.append('    } while (flag_p);\n')
    elif step == -1 and to_val == 1:
        if acc == 'hl':
            ans.append(8*' ' + '(a = ' + reg[1] + ') |= ' + reg[0] + ';\n')
        ans.append('    } while (flag_nz);\n')

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
    from_val = int(splt[0].strip().split('=')[-1], 0)
    to_val = int(splt[1].strip().split()[0], 0)
    step = int(splt[2].strip().split()[0], 0) if len(splt) == 3 else \
        (1 if to_val > from_val else -1)
    assert sgn(to_val - from_val) == sgn(step), 'Wrong step in for loop'
    not_push = len(splt) == 4 and \
        splt[3].strip().lower().startswith('not_push')
    return reg, from_val, to_val, step, not_push


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
    com_ix = fname.rfind('.')
    name_and_ext = fname[:com_ix], fname[com_ix + 1:]
    if len(name_and_ext) > 0 and name_and_ext[1].lower() == 'h' and \
            os.path.exists(name_and_ext[0] + '.c'):
        lines.append('#include "' + name_and_ext[0] + '.c"')


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
            fill_macro_data(connect_macro_lines(lines[i:]), macro_data)
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


def connect_macro_lines(lines):
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
    if macro.body[0] == '(':
        macro.body = '[' + macro.body[1:-1] + ']'


def make_replaces_macro(lines, macro_data):
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
        if tok == ')':
            break
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
        if len(splt) > 0 and splt[0] == 'return':
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
                foo_call = line.split('(', 1)[1].strip()[:-1].lstrip('!')
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


def check_function_args(lines):
    data = function_defs(lines)
    for func_name in data:
        check_func(lines, func_name, data[func_name])


def function_defs(lines):
    ans = {}
    for line in lines:
        splt = line.strip().split()
        if len(splt) == 0 or splt[0] not in ('void', 'bool'):
            continue
        ans[splt[1].split('(')[0]] = func_arg_registers(''.join(splt[1:]))
    return ans


def func_arg_registers(line):
    ans = []
    splt = line.split('(', 1)[1].split(')', 1)[0].split(',')
    for reg in splt:
        ans.append(reg)
    return ans


def check_func(lines, func_name, regs):
    for line in lines:
        splt = line.strip().split('(', maxsplit=1)
        if len(splt) == 0 or splt[0] != func_name or \
                line.strip().startswith('asm('):
            continue
        args = func_arg_registers(line[line.find(func_name):])
        args = [x.split('=')[0].strip() for x in args]
        assert sorted(''.join(args)) == sorted(''.join(regs)), \
            'Error: wrong arguments in function call: ' + line.lstrip()


def split_by_semicolon(lines):
    new_lines = []
    for line in lines:
        ix = find_signifficant_symbols(line, ';')
        new_lines += split_by_indices(line, ix, keep_separators=True)
    return new_lines


def move_variables_to_end(lines):
    tail = []
    deleted_nums = []
    state = 0
    for line_num, line in enumerate(lines):
        splt = line.strip().split()
        if len(splt) > 1 and splt[1].startswith('main('):
            break
        if state == 0 and len(splt) > 0 and (splt[0].startswith('int') or
                                             splt[0].startswith('uint')):
            tail.append(line)
            deleted_nums.append(line_num)
            if ';' not in line:
                state = 1
        elif state == 1:
            tail.append(line)
            deleted_nums.append(line_num)
            if ';' in line:
                state = 0
    for num in deleted_nums[::-1]:
        del(lines[num])
    lines += tail


def replace_brackets(lines):
    for i, line in enumerate(lines):
        if not (res := search(r'\w+\s*[\+\-/\*&|^!]?=\s*\(', line)):
            continue
        pos1 = res.span()[1] - 1
        pos2 = find_closing_bracket(line, pos1 + 1)
        assign = ('+=', '-=', '>>=', '<<=', '&=', '|=', '^=')
        if not any([x in line[pos1 + 1:pos2] for x in assign]):
            line = line[:pos1] + '[' + line[pos1 + 1:]
            lines[i] = line[:pos2] + ']' + line[pos2 + 1:]


def find_closing_bracket(line, pos, bracket_sym='()'):
    level = 1
    for i, sym in enumerate(line[pos:]):
        if sym == bracket_sym[0]:
            level += 1
        elif sym == bracket_sym[1]:
            level -= 1
            if level == 0:
                break
    return pos + i


def sgn(x):
    return -1 if x < 0 else (1 if x > 0 else 0)


def make_replaces_common(lines):
    text = connect_lines(lines)
    for replace in common_replaces:
        text = sub(replace, common_replaces[replace], text)
    return split_text(text)


def connect_lines(lines):
    text = ''
    for line in lines:
        text += line
    return text


def split_text(text):
    lines = text.split('\n')
    for i, line in enumerate(lines):
        lines[i] += '\n'
    return lines


if __name__ == '__main__':
    process_file(argv[1], argv[2], preprocessor)
