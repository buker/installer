#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = 'Łukasz Żułnowski'
__version__ = '1'

#Importowanie bibliotek
import sys
import argparse
import xml.etree.ElementTree as etree
import logging
import subprocess

#Konfiguracja logowania
logging.basicConfig(format='%(asctime)s [%(levelname)s] - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename='installer.log', filemode='w', level=logging.DEBUG, stream=sys.stdout )
#Główna funkcja
def main():
    msg = 'Rozpoczynam prace instalatora'
    logging.info(msg)
    #Obsługa argumentów
    parser = argparse.ArgumentParser()
    parser.add_argument('env', choices=['ins', 'uat', 'prd'], help='Podaj środowisko')
    parser.add_argument('app', choices=['ksms', 'nsp', 'sp2k'],help='Podaj nazwe aplikacji aplikacjep')
    parser.add_argument('file', nargs='*', help='Podaj ścieżki plików. Można podać kilka.')
    args = parser.parse_args()
    #Generowanie zmiennych
    env = args.env
    app = args.app
    files = args.file
    msg = "Instalator został uruchomiony z parametrami env=%(env)s, app=%(app)s, files=%(files)s" % {'env': env, 'app': app, 'files': files}
    logging.debug(msg)

    #parsowanie configa
    msg = 'Sprawdzanie czy plik konfiguracyjny istnieje'
    logging.info(msg)
    print(msg)
    try:
        tree = etree.parse('./installer.conf')
    except:
        msg = 'Brak pliku konfiguracyjnego'
        logging.exception(msg)
        print(msg)
    msg = 'Rozpoczynam parsowanie pliku konfiguracyjnego'
    logging.info(msg)
    root = tree.getroot()
    pattern = "./ENV[@value=\'%(env)s\']/APP[@value=\'%(app)s\']/SERVER" % {'env': env, 'app': app}
    msg = "Takim patternetm szukam w configu: "+pattern
    logging.debug(msg)
    server_list = root.findall(pattern)
    msg= "Plik konfiguracyjny sparsowany"
    logging.info(msg)
    print(msg)
    for server in server_list:
        msg = "Rozpoczynam wysyłanie zatrzymywanie usłuGi %(app)s na %(server)s" % {'app': app, 'server': server.text}
        logging.info(msg)
        print(msg)
        #Zatrzymywanie usługi
        path_server = "jboss7@%(server)s" % {'server': server.text}
        path_app = "bash /opt/kontakt/apps/%(app)s/%(app)s.sh stop" % {'app': app}
        logging.debug(path_server)
        logging.debug(path_app)
        stop = subprocess.Popen(["ssh", path_server, path_app], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = stop.communicate()
        if output[0].decode('utf8') == []:
            logging.error(output[1].decode('utf8'))
            print(output[1].decode('utf8'))
        else:
            logging.info(output[0].decode('utf8'))
            print(output[0].decode('utf8'))

        #Wysyłka plików.
        for file in files:
            msg = 'Wysyłam plik '+file+' na '+server.text+' dla aplikacji '+app
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
                msg = "Plik został wysłany z powodzeniem"
                logging.info(msg)
                print(msg)

        #Odpalanie backup install
            msg= 'Uruchamiam backup-install.sh dla pliku '+file+' na serwerze '+server.text
            print(msg)
            path_file = "./backup-install/install/%(file)s" % {'file': file}
            logging.debug(path_file)
            if env == 'ins':
                path_env = 'ST'
            elif env == 'uat':
                path_env = 'QA'
            elif env == 'prd':
                path_env = 'PRD'
            path_backup_sh = "cd /opt/kontakt/apps/%(app)s/; bash /opt/kontakt/apps/%(app)s/backup-install.sh -A ./ -e linux,%(path_env)s,linux/%(path_env)s %(path_file)s" % {'app': app, 'path_file': path_file, 'path_env': path_env}
            logging.debug(path_backup_sh)
            backup_install = subprocess.Popen(['ssh', path_server, path_backup_sh], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            output = backup_install.communicate()
            if output[0].decode('utf8') == []:
                logging.error(output[1].decode('utf8'))
                print(output[1].decode('utf8'))
            else:
                logging.info(output[0].decode('utf8'))
                print(output[0].decode('utf8'))

        #Odpalanie configure
        msg= "Uruhamiam configure.sh dla aplikacji %(app)s na serwerze %(server)s" % {'app': app, 'server': server.text}
        print(msg)
        logging.info(msg)
        path_configure = "cd /opt/kontakt/apps/%(app)s/; bash configure.sh" % {'app': app}
        logging.debug(path_configure)
        configure = subprocess.Popen(['ssh', path_server,  path_configure], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = configure.communicate()
        if output[0].decode('utf8') == []:
            logging.error(output[1].decode('utf8'))
            print(output[1].decode('utf8'))
        else:
            logging.info(output[0].decode('utf8'))
            print(output[0].decode('utf8'))

        #Odpalanie usługi
        msg= "Uruchamiam aplikacje %(app)s na serwerze %(server)s" % {'app': app, 'server': server.text}
        print(msg)
        logging.info(msg)
        path_app = "bash /opt/kontakt/apps/%(app)s/%(app)s.sh start" % {'app': app}
        logging.debug(path_app)
        start = subprocess.Popen(['ssh', path_server, path_app], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        output = start.communicate()
        if output[0].decode('utf8') == []:
            logging.error(output[1].decode('utf8'))
            print(output[1].decode('utf8'))
            msg= ("Nie udało się uruchomić aplikacji")
            print(msg)
            logging.exception(msg)
        else:
            logging.info(output[0].decode('utf8'))
            print(output[0].decode('utf8'))
            msg = "Aplikacja została uruchomiona"
            print(msg)
            logging.info(msg)
        msg= "Działanie instalatora zostało zakończone"
        print(msg)
        logging.info(msg)
main()
