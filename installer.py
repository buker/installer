#!/usr/bin/python3

__author__ = 'lzulnowski'

import sys
import argparse
import xml.etree.ElementTree as etree
import logging
from datetime import datetime as date
##########LOGOWANIE############
logging.basicConfig(format='%(asctime)s [%(levelname)s] - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='installer.log', filemode='w', level=logging.DEBUG)
###########################
def main():
    #Obsługa argumentów
    parser = argparse.ArgumentParser()
    parser.add_argument('env', choices=['ST','INS', 'UAT', 'QA', 'PRD'], help='Podaj środowisko: ST/INS, UAT/QA, PRD')
    parser.add_argument('app', choices=['KSMS', 'NSP,', 'SP'],help='Podaj nazwe aplikacji aplikacjep')
    parser.add_argument('file', nargs='*', help='Podaj ścieżki plików. Można podać kilka.')
    args = parser.parse_args()
    ##Generowanie zmiennych
    env = args.env
    if env == 'ST':
        env = "INS"
    elif env == 'QA':
        env = "UAT"
    app = args.app
    files = args.file

    #parsowanie configa
    logging.info('Sprawdzanie czy plik konfiguracyjny istnieje')
    try:
        tree = etree.parse('./installer.conf')
    except:
        logging.exception('Brak pliku konfiguracyjnego')
    logging.info('Rozpoczynam parsowanie pliku konfiguracyjnego')
    root = tree.getroot()
    server_list = root.findall("./ENV[@value='INS']/APP[@value='KSMS']/SERVER")
    for server in server_list:
        for file in files:
            print('Łącze się do server')











if __name__ == "__main__":
    main()