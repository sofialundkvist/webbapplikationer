import qrcode
import random, string
import os.path
from PIL import Image

front_end_id = input('Skriv in front end id: ')
user_id = input('Skirv in id: ')
img = qrcode.make('https://doltishkey.pythonanywhere.com/attendant/'+front_end_id+'/'+user_id)

img.filename = str(''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(16)))+'.png'
while os.path.isfile('static/img/qr/' + img.filename) == True:
    img.filename = str(''.join(random.choice(string.ascii_uppercase + string.digits) for i in range(16)))+'.png'
save_path = "static/img/qr"
file_path = "{path}/{file}".format(path=save_path, file=img.filename)
img.save(file_path)
session.query(Attendant).filter_by(id = user_id).update({'qr':img.filename})
