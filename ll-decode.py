import argparse
import sys
import re

def decode(infile, outfile, outfile2):
    lastaddr = ''
    firstloop = 1
    count = 1
    addr_regex = re.compile(r'(0x[0-f]{8})')
    raddr_max = 0
    caddr_max = 0
    maddr_max = 0
    offset_max = 0
    for llline in infile.readlines():
        llline = llline.decode()[:-2] #去掉换行
        hexaddr = addr_regex.search(llline)
        if hexaddr:
            bitnum = int(llline.split()[1])
            binaddr = bin(int(hexaddr.group(),16))[2:].zfill(32*4) #提取hex字符串,转为bin字符串,并对齐
            btype = binaddr[-27:-24] 
            raddr = int(binaddr[-24:-18], 2)
            caddr = int(binaddr[-18:-8], 2)
            maddr = int(binaddr[-8:], 2)
            # print(hexaddr.group())
            # print(binaddr)
            # print('%d\t%d\t%d' % (raddr,caddr,maddr))
            offset = int(llline.split()[3])
            if offset > offset_max : offset_max = offset
            if raddr > raddr_max : raddr_max = raddr
            if caddr > caddr_max : caddr_max = caddr
            if maddr > maddr_max : maddr_max = maddr

            #! 在 hexaddr.end() + 1 处加入 (raddr,caddr,maddr)
            lllist = list(llline)
            lllist.insert(hexaddr.end() + 1, btype + ' %d %d %d ' % (raddr,caddr,maddr) )
            llline = ''.join(lllist)

            rawline = '%d\t' % bitnum + btype + '\t%d\t%d\t%d\t%d' % (raddr,caddr,maddr,count) + '\n'

            #写ll_raw
            if firstloop == 0:
                if lastaddr != binaddr :
                    outfile2.write(lastrawline)   
                    count = 1
                else:
                    count += 1
            else:
                firstloop = 0
                count += 1
            lastaddr = binaddr 
            lastrawline = rawline
            
        outfile.write( llline + '\n')    
    outfile2.write(rawline)  
    print('\trow_max=%d\tcol_max=%d\tmin_max=%d\toffset_max=%d' % (raddr_max,caddr_max,maddr_max,offset_max) + '\n')



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

    decode(args.infile, args.outfile, args.outfile2)


if __name__ == '__main__':
    main()
