__author__ = 'sfranky'

import os
from itertools import takewhile, dropwhile



def get_line(fin, verbatim=False, SEPARATOR=None):
    """
    Yields a list per line read, of the following form:
    [indentation_change, line up to first space, line after first space if exists]
    Comment lines are omitted.
    Lines where comments exist at the end are stripped off their comment.
    Indentation is calculated with respect to the previous line.
    1: line is further indented
    0: same indentation
    -1: line is unindent
    Empty lines only return the indentation change.
    Where the line splits depends on SEPARATOR (default is first space)
    """
    indent = 0
    for line in fin:
        if line.lstrip().startswith('#'):
            continue
        elif ' #' in line :
            line = line.split(' #', 1)[0]

        prev_indent = indent
        indent = len(line) - len(line.lstrip(' '))
        if indent - prev_indent > 0:
            d_indent = 1
        elif indent == prev_indent:
            d_indent = 0
        else:
            d_indent = -1
        line = line.rstrip()
        list_line = verbatim and [d_indent, line] or [d_indent] + line.split(None or SEPARATOR, 1)
        if len(list_line) > 1:
            if list_line[1].startswith('"') or list_line[1].startswith("'"):
                list_line[1] = list_line[1][1:-1]
        else:
            pass
        yield list_line


def read_yaml_config(fn):
    raw_key_values = {}
    with open(fn, mode='r') as fin:
        get_lines = get_line(fin)
        line = next(get_lines)
        while line:
            block = dict()
            block, line = read_yaml_config_block(line, fin, get_lines, block)
            # for key in block:
            #     print key
            #     print '\t' + str(block[key])
            raw_key_values.update(block)

        config_dict = dict([(key, value) for key, value in raw_key_values.items()])
        return config_dict


def read_yaml_config_block(line, fin, get_lines, block):
    last_empty_container = block

    if len(line) > 1:  # non-empty line
        key_value, last_empty_container = process_line(line, fin, get_lines, last_empty_container)
        for (k, v) in key_value.items():
            block[k] = v

    while len(line) == 1:  # skip empty lines
        try:
            line = next(get_lines)
        except StopIteration:  # EO(config)F
            return {}, ''

    while len(line) > 1:  # as long as a blank line is not reached (i.e. block is not complete)
        if line[0] == 0:  # same level
            key_value, container = process_line(line, fin, get_lines, last_empty_container)
            for k in key_value:
                if k == '-':
                    if isinstance(container, str):
                        _list.append(container)
                    elif isinstance(key_value[k], list):
                        _list.extend(key_value[k])
                else:
                    last_empty_container[k] = key_value[k]  # fill up parent container with new value
                    last_empty_container = container  # point towards latest container (key_value's value)

        elif line[0] > 0:  # nesting
            key_value, container = process_line(line, fin, get_lines, last_empty_container)
            for k in key_value:
                # insert list into parent. Others should follow
                last_empty_container[k] = key_value[k]
                if k == '-':
                    # keep ref of above list here  #TODO
                    # _list = last_empty_container[k]
                    _list = last_empty_container[k] if isinstance(last_empty_container[k], list) else [last_empty_container[k]]
                last_empty_container = container  # next line needs this IF it is nested...

        elif line[0] < 0:  # go up one level
            key_value, container = process_line(line, fin, get_lines, last_empty_container)
            for k in key_value:
                if k == '-':
                    _list.extend(key_value[k])
                last_empty_container = container

        line = next(get_lines)
    return block, line


# def process_line(line, fin, get_lines, parent_container, container_stack, stack):
#     container_stack.append(parent_container)
#     if line[1].endswith(':'):
#         key, container = process_key_value_line(line, fin, get_lines)
#         parent_container[key] = container
#     elif line[1] == '-':
#         container_stack.append(parent_container)
#         container, stack = process_list_item_line(line, fin, stack, parent_container)
#         # (container is {list_out_by_name_pattern: dict()})
#         parent_container.setdefault('-',[]).append(container)
#     return container  # want to return a {} here for by_name_pattern


def process_line(list_line, fin, get_lines, last_empty_container):
    key = list_line[1]

    if len(list_line) == 2:  # key-only, so what's in the line following should be written in a new container
        container = {}
        return {key: container}, container

    elif len(list_line) == 3:
        container = list_line[2]

        if container.endswith(':'):  # key: '-'           - testkey:
            parent_key = key
            key = container
            new_container = {}
            return {parent_key: [{key: new_container}]}, new_container

        elif ': ' in container:  # key: '-'               - testkey: testvalue
            parent_key = key
            key, container = container.split(None, 1)
            return {parent_key: [{key: container}]}, last_empty_container

        else:  # simple value, e.g. testkey: testvalue
            if key == '-':  # i.e.  - testvalue
                last_empty_container = container  # TODO: why show a value?
                return {key: [container]}, last_empty_container
            else:
                # print 'testkey: testvalue here. %s: %s'  % (key, container)  # DEBUG
                return {key: container}, last_empty_container
    else:
        raise ValueError("Didn't anticipate that!")


def process_code(fin):
    # line = next(get_lines)
    # code = line[1]
    # while line[0] != -1:
    #     code += ' ' + line[-1]
    #     line = next(get_lines)
    # return code
    get_code = get_line(fin, verbatim=True)
    line = next(get_code)
    code = []
    while line[0] != -1:
        code.append(' ' + line[-1])
        line = next(get_code)
    return ' '.join(code.strip())


#### MAIN ###############

# with open(conf_file, mode='r') as fin:
#     prev_indent = 0
#     for line in takewhile(lambda x: True, get_line(fin)):
#         print line

if __name__ == '__main__':
    conf_file = '/home/sfranky/.local/qtop/qtopconf.yaml'
    stuff = read_yaml_config(conf_file)
    for key in stuff:
        print key
        print stuff[key]
        print
