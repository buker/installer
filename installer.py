#!/usr/bin/python3

__author__ = 'lzulnowski'

import sys
import argparse
import getpass
import getopt
#CONF
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--env', choices=['ST','INS', 'UAT', 'QA', 'PRD'], help='Podaj środowisko: ST/INS, UAT/QA, PRD')
    parser.add_argument('-a', '--app', choices=['ksms', 'nsp,', 'sp'],help='Podaj aplikacje ksms, sp, nsp')
    parser.add_argument('-f', '--file')
    args = parser.parse_args()



if __name__ == "__main__":
    main()