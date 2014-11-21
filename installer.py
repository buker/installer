#!/usr/bin/python3

__author__ = 'lzulnowski'

import sys
import argparse
import xml.etree.ElementTree as etree
import logging
import subprocess
from datetime import datetime as date
##########LOGOWANIE############
logging.basicConfig(format='%(asctime)s [%(levelname)s] - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='installer.log', filemode='w', level=logging.DEBUG)
###########################
def main():
    #Obsługa argumentów
    parser = argparse.ArgumentParser()
    parser.add_argument('env', choices=['ins', 'uat', 'prd'], help='Podaj środowisko')
    parser.add_argument('app', choices=['ksms', 'nsp,', 'sp2k'],help='Podaj nazwe aplikacji aplikacjep')
    parser.add_argument('file', nargs='*', help='Podaj ścieżki plików. Można podać kilka.')
    args = parser.parse_args()
    ##Generowanie zmiennych
    env = args.env
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
    ###./ENV[@value='env']/APP[@value='app']/SERVER


    pattern = "./ENV[@value=\'%(env)s\']/APP[@value=\'%(app)s\']/SERVER" % {'env': env, 'app' : app}
    server_list = root.findall(pattern)

    for server in server_list:

        ######Zatrzymywanie usługi
        path_server = "jboss7@%(server)s" % {'server': server.text}
        path_app = "\"/opt/kontakt/apps/%(app)s/%(app)s.sh stop\"" % {'app': app}
        stop = subprocess.Popen(['ssh', path_server ,path_app], stdout=subprocess.PIPE)
        out = stop.communicate()[0].decode('utf8')
        print(out)

        ##Wysyłka plików.
        for file in files:
            path_bii = "jboss7@%(server)s:/opt/kontakt/apps/%(app)s/backup-install/install" % {'server': server.text, 'app': app}
            send = subprocess.Popen(['scp', file, path_bii], stdout=subprocess.PIPE)
            out = send.communicate()[0].decode('utf8')
            print(out)



        #######Odpalanie backup install
        for file in files:
            path_file = "./backup-install/install/%(file)s" % {'file': file}
            if env == 'ins':
                path_env = 'ST'
            elif env == 'uat':
                path_env = 'QA'
            elif env == 'prd':
                path_env = 'PRD'

            path_backup_sh = "/opt/kontakt/apps/%(app)s/backup-install.sh -A ./ -e linux,%(path_env)s,linux/%(path_env)s $(file)" % {'app': app, 'file': path_file, 'path_env': path_env}
            backup_install = subprocess.Popen(['ssh', path_server, path_backup_sh], stdout=subprocess.PIPE)
            out = backup_install.communicate()[0].decode('utf8')

        ##########Odpalanie configure
        path_configure = "/opt/kontakt/apps/%(app)s/configure.sh" % {'app': app}
        configure = subprocess.Popen(['ssh', path_configure, '"start'], stdout=subprocess.PIPE)
        out = configure.communicate()[0].decode('utf8')
        print(out)

        #######Odpalanie usługi
        start = subprocess.Popen(['ssh', path_app, '"start'], stdout=subprocess.PIPE)
        out = stop.communicate()[0].decode('utf8')
        print(out)

    main()