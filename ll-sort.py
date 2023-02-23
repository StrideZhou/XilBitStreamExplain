import argparse
import sys
import re
import operator


contents=[]

def sort_txt(infile, outfile):
    bitaddr_regex = re.compile(r'  ([0-9]+) ')
    for line in infile.readlines():
        line = line.decode()[:-2]
        bitaddr = bitaddr_regex.search(line)
        if bitaddr:
            bitnum = int(bitaddr.group())
            contents.append([bitnum,line])
        else:
            outfile.write(line + '\n')

    contents.sort(key=operator.itemgetter(0))
    for line in contents:
        outfile.write(line[1] + '\n')


def main():
    parser = argparse.ArgumentParser(
        description='Convert a ASCII logic locationfile (.ll) file '
                    'to a format that can be read. By default read '
                    'from stdin and write to stdout.'
    )

    parser.add_argument('infile',
                        nargs='?',
                        type=argparse.FileType('rb'),
                        default=sys.stdin.buffer)
    parser.add_argument('outfile',
                        nargs='?',
                        type=argparse.FileType('w'),
                        default=sys.stdout)
    parser.add_argument('outfile2',
                        nargs='?',
                        type=argparse.FileType('w'),
                        default=sys.stdout)
    args = parser.parse_args()

    sort_txt(args.infile, args.outfile)
    

if __name__ == '__main__':
    main()

