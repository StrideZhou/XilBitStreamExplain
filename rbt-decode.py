
import argparse
import sys

# Header_type = { '001':'Type1',
#                 '010':'Type2'}

opcode_format = {  
    '00':'NOOP',
    '01':'Read',
    '10':'Write',
    '11':'Reserved'
}
reg_name = {
    "00000" : "CRC",
    "00001" : "FAR",
    "00010" : "FDRI",
    "00011" : "FDRO",
    "00100" : "CMD",
    "00101" : "CTL0",
    "00110" : "MASK",
    "00111" : "STAT",
    "01000" : "LOUT",
    "01001" : "COR0",
    "01010" : "MFWR",
    "01011" : "CBC",
    "01100" : "IDCODE",
    "01101" : "AXSS",
    "01110" : "COR1",
    "10000" : "WBSTAR",
    "10001" : "TIMER",
    "10110" : "BOOTSTS",
    "11000" : "CTL1",
    "11111" : "BSPI"
}

reg_exp = {
    "00000" : "CRC register.",
    "00001" : "Frame address register.",
    "00010" : "Frame data register, input register (write configuration data).",
    "00011" : "Frame data register, output register (read configuration data).",
    "00100" : "Command register.",
    "00101" : "Control register 0.",
    "00110" : "Masking register for CTL0 and CTL1.",
    "00111" : "Status register.",
    "01000" : "Legacy output register for daisy chain.",
    "01001" : "Configuration option register 0",
    "01010" : "Multiple frame write register.",
    "01011" : "Initial CBC value register.",
    "01100" : "Device ID register.",
    "01101" : "User access register.",
    "01110" : "Configuration option register 1.",
    "10000" : "Warm boot start address register.",
    "10001" : "Watchdog timer register.",
    "10110" : "Boot history status register.",
    "11000" : "Control register 1.",
    "11111" : "BPI/SPI configuration options register."
}

cmd_code_exp = {
    "00000" : "Null command, no action.",
    "00001" : "Writes configuration data: used prior to writing \n\
configuration data to the FDRI.",
    "00010" : "Multiple frame write: used to perform a write of \n\
a single frame data to multiple frame addresses.",
    "00011" : "Last frame: Deasserts the GHIGH_B signal, activating \n\
all interconnects. The GHIGH_B signal is asserted \n\
with the AGHIGH command.",
    "00100" : "Reads configuration data: used prior to reading \n\
configuration data from the FDRO.",
    "00101" : "Begins the start-up sequence: start-up sequence \n\
begins after a successful CRC check and a DESYNC \n\
command are performed.",
    "00111" : "Resets CRC: Resets the CRC register.",
    "01000" : "Asserts the GHIGH_B signal: places all interconnect \n\
in a High-Z state to prevent contention when writing \n\
new configuration data. This command is only used \n\
in shutdown reconfiguration. Interconnect is \n\
reactivated with the LFRM command.",
    "01001" : "Switches the CCLK frequency: updates the frequency \n\
of the master CCLK based on the ECLK_EN and OSCFSEL \n\
bits in the COR0 register. ",
    "01010" : "Pulses the GRESTORE signal: sets/resets (depending \n\
on user configuration) CLB flip-flops.",
    "01011" : "Begin shutdown sequence: Initiates the shutdown \n\
sequence, disabling the device when finished. Shutdown \n\
activates on the next successful CRC check or RCRC \n\
instruction (typically an RCRC instruction).",
    "01101" : "Resets the DALIGN signal: Used at the end of configuration \n\
to desynchronize the device. After desynchronization, \n\
all values on the configuration data pins are ignored.",
    "01111" : "Internal PROG for triggering a warm boot.",
    "10000" : "When readback CRC is selected, the configuration logic \n\
recalculates the first readback CRC value after \n\
reconfiguration. Toggling GHIGH has the same effect. \n\
This command can be used when GHIGH is not toggled \n\
during the reconfiguration case.",
    "10001" : "Reload watchdog timer.",
    "10010" : "BPI/SPI re-initiate bitstream read.",
    "10011" : "Switch to negative edge clocking (configuration data \n\
capture on falling edge)"
}

cmd_code_name = {
    "00000" : "NULL",
    "00001" : "WCFG",
    "00010" : "MFW",
    "00011" : "DGHIGH/LFRM",
    "00100" : "RCFG",
    "00101" : "START",
    "00111" : "RCRC",
    "01000" : "AGHIGH",
    "01001" : "SWITCH",
    "01010" : "GRESTORE",
    "01011" : "SHUTDOWN",
    "01101" : "DESYNC",
    "01111" : "IPROG",
    "10000" : "CRCC",
    "10001" : "LTIMER",
    "10010" : "BSPI_READ",
    "10011" : "FALL_EDGE"
}

reg_name_code = {v: k for k, v in reg_name.items()} # reverse dict
cmd_name_code = {v: k for k, v in cmd_code_name.items()}
opcode_name = {v: k for k, v in opcode_format.items()}

def decode(rbtfile, outfile, outfile2, outputhex):
    data_word = 0

    for bitstream in rbtfile.readlines():
        bitstream = bitstream.decode()[:-2]
        exp = ""
        isCFGdata = 0
        if data_word != 0:
            if reg_addr == reg_name_code.get('CMD'):
                cmd = bitstream[-5:]
                exp += cmd
                exp += "\t" + cmd_code_name.get(cmd)
                exp += "\n" + cmd_code_exp.get(cmd)

                if (cmd == cmd_name_code.get('WCFG') )& outputhex: 
                    isCFGdata = 1
                    CFGaddr = FAR
                    hex = '\n@%08X' % CFGaddr
                    sys.stdout.write('@CFGaddr%d\n' % CFGaddr)

            elif reg_addr == reg_name_code.get('FDRI'): 
                if outputhex: hex = "%08X" % int(bitstream,2)  

            elif reg_addr == reg_name_code.get('FAR'): 
                exp += "%08X" % int(bitstream,2)   
                FAR = int(bitstream,2)
                sys.stdout.write('@FAR%d\n' % FAR)

            else:
                exp += "%08X" % int(bitstream,2)        

            data_word -= 1

        elif bitstream.isdigit() :
            if bitstream[:3] == "001": # type1
                exp += "Type1" + "\t" + opcode_format.get(bitstream[-29:-27])
                if bitstream[-29:-27] != opcode_name.get('NOOP') : 
                    reg_addr = bitstream[-18:-13]
                    exp += "\t" + reg_addr
                    #输出名称
                    try:
                        exp += "\t" + reg_name.get(reg_addr)
                    except :
                        exp += "\t" + "UNKNOWN ADDR"

                    data_word = int(bitstream[-11:],2)
                    exp += "\t" + "%d" % data_word + "word"
                    #输出解释
                    try:
                        exp += "\t" + reg_exp.get(reg_addr)
                    except :
                        exp += "\t" + "---------UNKNOWN ADDR--------"
                    if data_word > 1: sys.stdout.write('got word %d\n' % data_word) 

            elif bitstream[:3] == "010": # type2
                exp += "Type2" + "\t" + opcode_format.get(bitstream[-29:-27])
                if bitstream[-29:-27] != opcode_name.get('NOOP') : 
                    data_word = int(bitstream[-27:],2)
                    exp += "\t" + "%d" % data_word + "word"

                    sys.stdout.write('got word %d\n' % data_word)    

            else : exp += "%08X" % int(bitstream,2)
        

        if isCFGdata == 0: 
            outfile.write( bitstream + " " + exp + '\n')    
        elif outputhex:
            outfile2.write( hex + '\n') 
            


def main():
    parser = argparse.ArgumentParser(
        description='Convert a rbt file to a format that can be read. '
                    'By default read from stdin and write to stdout.'
                    'eg: '
                    'CMD> for %i in (*.rbt) do (python .\\rbt-decode.py --h %i %i.data > %i.log) '
    )

    parser.add_argument('--h', 
                        action='store_true',
                        default=False, 
                        help='output pure hex for cfg chain.')

    parser.add_argument('rbtfile',
                        nargs='?',
                        type=argparse.FileType('rb'),
                        default=sys.stdin.buffer)
    # parser.add_argument('outfile',
    #                     nargs='?',
    #                     type=argparse.FileType('w'),
    #                     default=sys.stdout)
    parser.add_argument('hexfile',
                        nargs='?',
                        type=argparse.FileType('w'),
                        default=sys.stdout)
    args = parser.parse_args()

    txtfile = open(args.rbtfile.name[:-4] + '.txt' ,'w')

    decode(args.rbtfile, txtfile, args.hexfile, args.h )


if __name__ == '__main__':
    main()
