import hashlib
import datetime

pwd = input('Skriv in ditt lösenord:')
print('Hashat: ' + hashlib.sha256(pwd.encode('utf-8')).hexdigest())
print(datetime.datetime.now())
