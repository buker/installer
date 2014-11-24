#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = 'lzulnowski'

import sys
import argparse
import xml.etree.ElementTree as etree
import logging
import subprocess


from datetime import datetime as date
##########LOGOWANIE############
logging.basicConfig(format='%(asctime)s [%(levelname)s] - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='installer.log', filemode='w', level=logging.DEBUG, stream=sys.stdout )
###########################
def main():
    logging.info('Rozpoczynam prace instalatora')
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
    msg = "Instalator został uruchomiony z parametrami env=%(env)s, app=%(app), file=%(file)s" % {'env': env, 'app': app, 'files': files}
    logging.debug(msg)

    #parsowanie configa
    logging.info('Sprawdzanie czy plik konfiguracyjny istnieje')
    try:
        tree = etree.parse('./installer.conf')
    except:
        logging.exception('Brak pliku konfiguracyjnego')
    logging.info('Rozpoczynam parsowanie pliku konfiguracyjnego')
    root = tree.getroot()
    ###./ENV[@value='env']/APP[@value='app']/SERVER
    pattern = "./ENV[@value=\'%(env)s\']/APP[@value=\'%(app)s\']/SERVER" % {'env': env, 'app': app}
    server_list = root.findall(pattern)
    logging.info("Plik konfiguracyjny sparsowany")
    for server in server_list:
        msg = "Rozpoczynam wysyłanie zatrzymywanie usługi %(app)s na %(server)s" % {'app': app, 'server': server.text}
        logging.info(msg)
        print(msg)
        ######Zatrzymywanie usługi
        path_server = "jboss7@%(server)s" % {'server': server.text}
        path_app = "bash /opt/kontakt/apps/%(app)s/%(app)s.sh stop" % {'app': app}
        stop = subprocess.Popen(["ssh", path_server, path_app], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = stop.communicate()
        if output[0].decode('utf8') == []:
            logging.error(output[1].decode('utf8'))
            print(output[1].decode('utf8'))
        else:
            logging.info(output[0].decode('utf8'))
            print(output[0].decode('utf8'))

        ##Wysyłka plików.
        for file in files:
            msg = 'Wysyłam plik', file, 'na', server.text
            logging.info(msg)
            print(msg)
            path_bii = "jboss7@%(server)s:/opt/kontakt/apps/%(app)s/backup-install/install" % {'server': server.text, 'app': app}
            logging.debug(path_bii)
            file_t = './'+file
            send = subprocess.Popen(['scp', file_t, path_bii], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = send.communicate()
            if output[0].decode('utf8') == []:
                logging.error(output[1].decode('utf8'))
                print(output[1].decode('utf8'))
            else:
                logging.info(output[0].decode('utf8'))
                print(output[0].decode('utf8'))
        #######Odpalanie backup install

            print('Odpalam backup-install.sh dla pliku', file, 'na serwerze', server.text)
            path_file = "./backup-install/install/%(file)s" % {'file': file}
            print(path_file)
            if env == 'ins':
                path_env = 'ST'
            elif env == 'uat':
                path_env = 'QA'
            elif env == 'prd':
                path_env = 'PRD'
            path_backup_sh = "cd /opt/kontakt/apps/%(app)s/; bash /opt/kontakt/apps/%(app)s/backup-install.sh -A ./ -e linux,%(path_env)s,linux/%(path_env)s %(path_file)s" % {'app': app, 'path_file': path_file, 'path_env': path_env}
            backup_install = subprocess.Popen(['ssh', path_server, path_backup_sh], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = backup_install.communicate()
            if output[0].decode('utf8') == []:
                logging.error(output[1].decode('utf8'))
                print(output[1].decode('utf8'))
            else:
                logging.info(output[0].decode('utf8'))
                print(output[0].decode('utf8'))

        ##########Odpalanie configure
        path_configure = "cd /opt/kontakt/apps/%(app)s/; bash configure.sh" % {'app': app}
        configure = subprocess.Popen(['ssh', path_server,  path_configure], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = configure.communicate()
        if output[0].decode('utf8') == []:
            logging.error(output[1].decode('utf8'))
            print(output[1].decode('utf8'))
        else:
            logging.info(output[0].decode('utf8'))
            print(output[0].decode('utf8'))

        #######Odpalanie usługi
        path_app = "bash /opt/kontakt/apps/%(app)s/%(app)s.sh start" % {'app': app}
        start = subprocess.Popen(['ssh', path_server, path_app], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = start.communicate()
        if output[0].decode('utf8') == []:
            logging.error(output[1].decode('utf8'))
            print(output[1].decode('utf8'))
        else:
            logging.info(output[0].decode('utf8'))
            print(output[0].decode('utf8'))
main()
