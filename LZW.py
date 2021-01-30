import argparse
from pathlib import Path
import numpy as np
import csv

def dec_to_bin(value, length):
    return format(value, '0' + str(length) + 'b')

def compress(path):
    # Open filename_LZWtable.csv
    f_table = open(path.stem + '_LZWtable.csv', 'w')
    f_table_writer = csv.writer(f_table, delimiter=',')
    f_table_writer.writerow(['Buffer', 'Input', 'New sequence',
                             'Address', 'Output'])

    # Open input file
    f_input = open(path, 'r')
    content = f_input.read()
    f_input.close()

    # Initialize dictionary and variables
    dictionary = ['%']
    for c in content:
        if c not in dictionary and c != '\n':
            dictionary.append(c)
    dictionary.sort()

    tmp_buffer = []
    res = ""
    encoding_size = int(np.ceil(np.log2(len(dictionary))))
    start_encoding_size = encoding_size

    # Save dictionary in filename_dico.csv
    out_dico = open(path.stem + '_dico.csv', 'w')
    out_dico.write(','.join(dictionary) + '\n')
    out_dico.close()

    # Main loop
    for c in content:
        table_row = [None] * 5
        table_row[0] = ''.join(tmp_buffer)

        n = "" if tmp_buffer == [] else tmp_buffer.pop()

        if c == '\n':
            table_row[4] = '@[{}]={}'.format(n, dictionary.index(n))
            res += dec_to_bin(dictionary.index(n), encoding_size)
            f_table_writer.writerow(table_row)
            break

        table_row[1] = c
        n_c = n + c

        if n_c in dictionary:
            tmp_buffer.insert(0, n_c)
            if len('{0:b}'.format(dictionary.index(n_c))) > encoding_size:
                table_row[4] = '@[{}]={}'.format('%', dictionary.index('%'))
                res += dec_to_bin(dictionary.index('%'), encoding_size)
                encoding_size += 1
        else:
            dictionary.append(n_c)
            tmp_buffer.insert(0, c)
            res += dec_to_bin(dictionary.index(n), encoding_size)

            table_row[2] = n_c
            table_row[3] = len(dictionary) - 1
            table_row[4] = '@[{}]={}'.format(n, dictionary.index(n))

        f_table_writer.writerow(table_row)

    f_table.close()

    start_size = (len(content) - 1) * start_encoding_size
    end_size = len(res)
    compression_ratio = round(end_size / start_size, 3)
    out = [res,
           'Size before LZW compression: {} bits'.format(start_size),
           'Size after LZW compression: {} bits'.format(end_size),
           'Compression ratio: {}'.format(compression_ratio)]
    out_lzw = open(path.stem + '.lzw', 'w')
    out_lzw.write('\n'.join(out) + '\n')
    out_lzw.close()

def uncompress(path):
    # Load dictionary
    f_dict = open(path.parent.joinpath(path.stem + '_dico.csv'))
    csv_reader = csv.reader(f_dict, delimiter=',')
    dictionary = list(csv_reader)[0]
    f_dict.close()
    encoding_size = int(np.ceil(np.log2(len(dictionary))))

    # Open input file
    f_input = open(path, 'r')
    content = f_input.read()
    f_input.close()

    # Main loop
    res = ""
    tmp_buffer = []
    i = 0
    while i < len(content):
        if content[i] == '\n':
            res += ("" if tmp_buffer == [] else tmp_buffer.pop())
            break

        # Get address of length encoding_size
        addr = content[i:i+encoding_size]
        c = dictionary[int(addr, 2)]
        i += encoding_size

        if c == '%':
            encoding_size += 1
            continue

        n = "" if tmp_buffer == [] else tmp_buffer.pop()
        n_c = n + c[0]

        if n_c in dictionary:
            tmp_buffer.insert(0, n_c)
        else:
            dictionary.append(n_c)
            res += n
            tmp_buffer.insert(0, c)

    # Write output
    out_txt = open(path.stem + '.txt', 'w')
    out_txt.write(res + '\n')
    out_txt.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", help="compress", action="store_true")
    parser.add_argument("-u", help="uncompress", action="store_true")
    parser.add_argument("-p", help="path of input file")
    args = parser.parse_args()

    input_filename = Path(args.p)
    if args.c:
        compress(input_filename)
    elif args.u:
        uncompress(input_filename)
