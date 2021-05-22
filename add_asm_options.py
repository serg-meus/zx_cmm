# -*- coding: utf-8 -*-

from sys import argv
from preprocessor import process_file


class options_c:
    def __init__(self):
        self.out_bin = False
        self.out_tap = False
        self.out_hob = False
        self.org = None
        self.device = None
        self.project_name = None


def add_options(lines):
    options = fill_options_struct(lines)
    write_start_end_labels(lines)
    write_options(lines, options)
    return lines


def fill_options_struct(lines):
    options = options_c()
    for arg in argv[3:]:
        process_arg(arg.strip(), options)
    return options


def process_arg(arg, options):
    (add_output if arg.startswith('+') else add_org_or_device)(arg, options)


def add_output(arg, options):
    assert(hasattr(options, 'out_' + arg[1:]))
    exec('options.out_' + arg[1:] + ' = True')


def add_org_or_device(arg, options):
    name_and_val = [s.strip() for s in arg.split('=')]
    assert(hasattr(options, name_and_val[0]))
    exec('options.' + name_and_val[0] + ' = "' + name_and_val[1] + '"')


def write_start_end_labels(lines):
    lines.insert(0, 'StartOfProg:\n')
    lines.append('EndOfProg:\n')


def write_options(lines, options):
    if options.org:
        lines.insert(0, '    ORG ' + options.org + '\n')
    if options.device:
        lines.insert(0, '    DEVICE ' + options.device.upper() + '\n')
    write_save_project_options(lines, options)


def write_save_project_options(lines, options):
    beg_len = ', StartOfProg, EndOfProg - StartOfProg\n'
    prj = '"' + options.project_name
    dct = {'out_hob': '    SAVEHOB ' + prj + '.$c", ' + prj + '.C"' + beg_len,
           'out_tap': '    EMPTYTAP ' + prj + '_c.tap"\n' +
           '    SAVETAP ' + prj + '_c.tap"' + ', CODE, ' + prj +
           '"' + beg_len,
           'out_bin': '    SAVEBIN ' + prj + '.bin"' + beg_len}
    for opt_name in dct:
        if hasattr(options, opt_name) and getattr(options, opt_name):
            lines.append(dct[opt_name])


if __name__ == '__main__':
    process_file(argv[1], argv[2], add_options)
