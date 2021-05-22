# -*- coding: utf-8 -*-

from sys import argv


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
    macro_data = collect_macrofunctions(lines)
    delete_definitions(lines)
    make_replaces(lines, macro_data)
    return lines


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
    return ans[0], ans[1]


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


def get_new_body(macro, given_tokens):
    if not macro.arg_names:
        return macro.body
    update_arg_values(given_tokens, macro)
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


if __name__ == '__main__':
    process_file(argv[1], argv[2], preprocessor)
