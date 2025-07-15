import argparse
import struct
import sys
import os

import shutil
import subprocess

board_list = [
    #board name, MCU, relative path of NuLinkTool 
    ['NuMaker-M467HJ', 'M467', 'NuLink_M460_M2L31.exe'],
    ['NuMaker-M55M1', 'M55M1', 'M55M1_M5531\\NuLink.exe'],
]

def main(argv=None):
    def formatter(prog): 
        return argparse.HelpFormatter(prog, max_help_position=60)
    
    parser = argparse.ArgumentParser(description="Flash SDS recording firmware",
                                     formatter_class=formatter)

    required = parser.add_argument_group("required")
    required.add_argument("--board", help="specify target board name", default='NuMaker-M55M1', required=True)
    required.add_argument("--binary_file", help="specify project binary file", required=True)

    args = parser.parse_args(argv)

    binary_file_abspath = os.path.abspath(args.binary_file)

    board_found = False
    for board_info in board_list:
        if board_info[0] == args.board:
            board_found = True
            break
    if board_found is False:
        print("board not support")
        return 2
    
    #check nulink in the system's PATH env
    nulink_util = shutil.which(board_info[2])

    if nulink_util is None:
        nulink_util = os.path.join(os.path.dirname(__file__), '..', 'tools', 'NuLink Command Tool', board_info[2])
        if not os.path.isfile(nulink_util):
            print('nulink not found')
            return 3

    print(f"NuLink tool: {nulink_util}")
    nulink_util_dir = os.path.dirname(nulink_util)
    cur_dir = os.getcwd()
    os.chdir(nulink_util_dir)

    nulink_connect_cmd = [nulink_util, '-C']
    nulink_write_cmd = [nulink_util, '-W', 'APROM', binary_file_abspath, '1']
    nulink_reset_cmd = [nulink_util, '-S']

    # connect
    try:
        ret = subprocess.run(nulink_connect_cmd, shell=True, check=True)
        if ret.returncode == 0:
            print('Connect to MCU successfully')
        else:
            os.chdir(cur_dir)
            print('Unable connect to MCU')
            return 4
    except subprocess.CalledProcessError as e:
        print(f'Error connecting to MCU: {e}')
    except Exception as e:
        print(f'Unexpected error: {e}') 
    
    # erase + write APROM
    try:
        print(f'start program target MCU: {binary_file_abspath}')
        ret =subprocess.run(nulink_write_cmd, shell=True)
        if ret.returncode == 0:
            print('program MCU done')
        else:
            os.chdir(cur_dir)
            print('unable program MCU')
            return 5
    except subprocess.CalledProcessError as e:
        print(f'Error programming MCU: {e}')
    except Exception as e:
        print(f'Unexpected error: {e}')    

    # connect + reset
    try:
        print('reset target')
        ret =subprocess.run(nulink_connect_cmd, shell=True)
        if ret.returncode == 0:
            print('connect MCU done')
        else:
            os.chdir(cur_dir)
            print('unable connect MCU')
            return 6
    except subprocess.CalledProcessError as e:
        print(f'Error connecting to MCU for reset: {e}')
    except Exception as e:
        print(f'Unexpected error during reset: {e}')
    try:        
        ret =subprocess.run(nulink_reset_cmd, shell=True, check=True)
        if ret.returncode == 0:
            print('reset MCU done')
        else:
            os.chdir(cur_dir)
            print('reset erase MCU')
            return 7
    except subprocess.CalledProcessError as e:
        print(f'Error resetting MCU: {e}')
    except Exception as e:
        print(f'Unexpected error during reset: {e}')    
    

    os.chdir(cur_dir)
    return 0

    

# if __name__ == "__main__":
# for Pystand
def start(argv=None):
    return main(argv)
