#!/usr/bin/python
# -*- coding: UTF-8 -*-
##
# Some package requirements (RPi/stretch)
# deb: libnfc5 python-rpi.gpio python-mysqldb
# pip: nfcpy (>=0.13.2)
##

import time
import os
import datetime
import config
import MySQLdb

hostname=config.DATABASE_CONFIG['hostname']
database=config.DATABASE_CONFIG['database']
username=config.DATABASE_CONFIG['username']
password=config.DATABASE_CONFIG['password']
nametag=config.PROG_CONFIG['nametag']
relay=config.PROG_CONFIG['relay']

class bcolors:
    OKGREENBG = '\033[42m'
    FAILREDBG = '\033[41m'
    ENDC = '\033[0m'

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

import nfc
from nfc.clf import RemoteTarget
clf = nfc.ContactlessFrontend()

while True:
    clf.open('tty:AMA0:pn532')
    print bcolors.ENDC
    os.system('cls' if os.name == 'nt' else 'clear')
    os.system('setterm -cursor off')
    timestamp = datetime.datetime.now().strftime('%d-%m-%Y %H:%M')
    print ''
    print u'{0: ^24}'.format(nametag).encode('utf-8')
    print u'{0: ^24}'.format(timestamp).encode('utf-8')
    print ''
    target = clf.sense(RemoteTarget('106A'), RemoteTarget('106B'), RemoteTarget('212F'), RemoteTarget('424F'))
    if target:
        tag = nfc.tag.activate(clf, target)
        uid = str(tag.identifier).encode('hex').upper()
        clf.close()
        # Verify
        db = MySQLdb.connect(read_default_file="./config.ini",db=database)
        cur = db.cursor()
        sql = "SELECT cards.uid,cards.owner,owner.house,owner.apartment,owner.name FROM cards RIGHT JOIN owner ON cards.owner = owner.id WHERE cards.uid = %s AND cards.active = 1 LIMIT 1"
        cur.execute(sql, [uid])
        if not cur.rowcount:
            # Fail
            sql = "INSERT INTO poller (poller.uid) VALUES (%s)"
            cur.execute(sql, [uid])
            db.commit()
            print bcolors.FAILREDBG
            os.system('cls' if os.name == 'nt' else 'clear')
            print ''
            print u'{0: ^24}'.format(nametag).encode('utf-8')
            print u'{0: ^24}'.format(timestamp).encode('utf-8')
            print ''
            print u'{0: ^24}'.format('Unkown tag!').encode('utf-8')
            print u'{0: ^24}'.format(uid).encode('utf-8')
            print ''
            print bcolors.ENDC
            time.sleep(5)
        else:
            # OK
            for row in cur.fetchall():
                owner = row[1]
                name = str(row[2]) + "/" + str(row[3]) + " (" + str(row[4]) + ")"
            print bcolors.OKGREENBG
            os.system('cls' if os.name == 'nt' else 'clear')
            print ''
            print u'{0: ^24}'.format(nametag).encode('utf-8')
            print u'{0: ^24}'.format(timestamp).encode('utf-8')
            print ''
            print u'{0: ^24}'.format('Known tag, OK!').encode('utf-8')
            print u'{0: ^24}'.format(uid).encode('utf-8')
            print ''
            print u'{0: ^24}'.format(name).encode('utf-8')
            print ''
            print bcolors.ENDC
            GPIO.setup(relay, GPIO.OUT)
            cur = db.cursor()
            sql = "INSERT INTO poller (poller.uid,poller.owner) VALUES (%s,%s)"
            cur.execute(sql,(uid,name))
            db.commit()
            time.sleep(5)
            GPIO.setup(relay, GPIO.IN)
        db.close()
    clf.close()
    time.sleep(1)
