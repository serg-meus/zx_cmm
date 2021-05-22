# -*- coding: utf-8 -*-

from sys import argv
from re import sub
from preprocessor import process_file


def optimize_z80_asm(lines):
    lines = strip_comments(lines)
    delete_unused_functions(lines)
    auto_inline(lines)
    lines = replace_instructions(lines)
    return lines


def auto_inline(lines):
    label_data = collect_calls_data(lines)
    find_functions_to_inline(label_data)
    replace_calls(lines, label_data)


def collect_calls_data(lines):
    label_data = {}
    for line in lines:
        update_label_data(label_data, line.strip().split())
    count_len_of_functions(lines, label_data)
    return label_data


def update_label_data(label_data, splited_line):
    if splited_line[0] != 'call':
        return
    if splited_line[1] in label_data:
        label_data[splited_line[1]][0] += 1
    else:
        label_data[splited_line[1]] = [1, 0]  # num of occurences, len of func


def find_functions_to_inline(label_data):
    labels_to_delete = []
    for label in label_data:
        if label_data[label][0] > 1 and label_data[label][1] > 3:
            labels_to_delete.append(label)
    delete_labels(label_data, labels_to_delete)


def delete_labels(label_data, labels_to_delete):
    for label in labels_to_delete:
        del label_data[label]


def count_len_of_functions(lines, label_data):
    for lb in label_data:
        state = 0
        for i, line in enumerate(lines):
            if state == 0 and not line.startswith(lb + ':'):
                continue
            elif state == 0:
                state = 1
                ans = 0
            elif state == 1 and line.strip() != ('ret'):
                ans += 1
                continue
            elif state == 1:
                label_data[lb][1] = ans
                state = 0
                break


def replace_calls(lines, label_data):
    for label in label_data:
        if label_data[label][1] > 0:  # len of func
            foo_lines = copy_func_body(lines, label, label_data[label][1])
            insert_func_bodies(lines, label, foo_lines, label_data[label][0])
            delete_function(lines, label)


def copy_func_body(lines, label, len_of_func_body):
    for i, line in enumerate(lines):
        if line.startswith(label + ':'):
            return lines[i + 1: i + len_of_func_body + 1]


def insert_func_bodies(lines, label, foo_lines, num_of_occurencies):
    for n in range(num_of_occurencies):
        for n_line, line in enumerate(lines):
            if insert_body(lines, line, n_line, label, foo_lines):
                break


def insert_body(lines, line, n_line, label, foo_lines):
    if line.split()[0] == 'call' and line.split()[1] == label:
        del(lines[n_line])
        lines[n_line:n_line] = foo_lines
        return True
    return False


def delete_function(lines, label):
    state = 0
    lines_to_delete = []
    for i, line in enumerate(lines):
        if state == 0 and line.startswith(label + ':'):
            state = 1
            lines_to_delete.append(i)
        elif state == 1 and line.split()[0] != 'ret':
            lines_to_delete.append(i)
        elif state == 1:
            lines_to_delete.append(i)
            break
    for i in sorted(lines_to_delete, reverse=True):
        del(lines[i])


def strip_comments(lines):
    new_lines = []
    for line in lines:
        if not line.strip().startswith(';'):
            new_lines.append(line)
    return new_lines


def delete_unused_functions(lines):
    labels = collect_labels(lines)
    called_labels = collect_calls_data(lines)
    unused_labels = find_unused(labels, called_labels)
    delete_functions(lines, unused_labels)


def find_unused(labels, called_labels):
    unused_labels = []
    for label in labels:
        if label not in called_labels:
            unused_labels.append(label)
    return unused_labels


def delete_functions(lines, unused_labels):
    for label in unused_labels:
        delete_function(lines, label)


def collect_labels(lines):
    labels = []
    for line in lines:
        if line[0] != ' ' and line[-2] == ':' and not is_auto_label(line):
            labels.append(line.strip()[:-1])
    return labels


def is_auto_label(line):
    return (line[0] == 'l' and line[1:-2].isnumeric()) or line == 'main:\n'


def replace_instructions(lines):
    replaces = {r'ld\s+a,\s+0': 'sub  a',
                r'dec\s+b\n\s+j[rp]\s+nz,\s+(\w+)': r'djnz \1',
                r'call\s+(\w+)\n\s+ret': r'jp  \1',
                r'\s+jp\s+(\w+)\n\1:': r'\n\1:',
                r'jp\s+(l\d+)': r'IF \1 - $ < 127\n        jr \1\n' +
                r'    ELSE\n        jp \1\n    ENDIF',
                r'jp\s+([n]?[zc],\s+)(l\d+)': r'IF \2 - $ < 127\n' +
                r'        jr \1\2\n    ELSE\n        jp \1\2\n    ENDIF'}
    text = connect_lines(lines)
    for replace in replaces:
        text = sub(replace, replaces[replace], text)
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
    process_file(argv[1], argv[2], optimize_z80_asm)
