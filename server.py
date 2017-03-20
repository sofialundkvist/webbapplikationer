from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, redirect, send_file
from urllib.parse import urlparse, urljoin
import json

from itsdangerous import URLSafeTimedSerializer
from modules.attendant import Attendant
from modules.user import User
from modules.exhibitor import Exhibitor
from modules.db_connector import *
from modules.connection import Connection
from modules.connection import Label_to_Connection
from modules.label import Label
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

def createSession():
    global session
    session = Session()

current_user = None

class Current_user():
    def __init__(self, id):
        self.id = int(id)

def login_required(myFunc):
    @wraps(myFunc)
    def wrapper(*args, **kwargs):
        createSession()
        print(request.headers.get('id'))
        print(request.headers.get('token'))
        exhibitor = Exhibitor.get_exhibitor(session, request.headers.get('id'))
        if exhibitor:
            print('Utställaren finns')
            if exhibitor.is_authenticated(request.headers.get('token')):
                print('Utställaren är autensierad')
                global current_user
                current_user = Current_user(request.headers.get('id'))
                return myFunc(*args, **kwargs)
            else:
                print('Utställaren är inte autensierad')
                session.close()
                abort(404)
        else:
            print('Utställaren finns inte')
            session.close()
            abort(404)
    return wrapper

@app.route('/attendant/',methods=['POST'])
def create_attendant():
    createSession()
    created, returned_data = create_new_attendant()
    session.expunge_all()
    session.close()
    if created:
        return json.dumps({'attend':'True', 'url':'/thanks/'+str(returned_data['front_end_id'])+'/'+str(returned_data['id'])})
    else:
        return json.dumps({'attend':'False','errors':returned_data})

@app.route('/anmalan')
def welcome():
    return render_template('index.html')

@app.route('/email_check', methods=["POST"])
def check_email():
    createSession()
    email = request.form['mejl']
    email = json.loads(email)
    response = {}
    response['email'] = Attendant.is_attending(session, email)
    session.expunge_all()
    session.close()
    return json.dumps(response)

def create_new_attendant():
    contact_info = {}
    contact_info['first_name'] = request.form.get('firstName')
    contact_info['surname'] = request.form.get('surName')
    contact_info['email'] = request.form.get('email')
    contact_info['month'] = request.form.get('month')
    contact_info['day'] = request.form.get('day')
    contact_info['school'] = request.form.get('whichSchool')
    contact_info['commune'] = request.form.get('municipality')
    contact_info['profession'] = request.form.get('profession')
    list_of_subjects = request.form.getlist('subjects')
    contact_info['list_subjects'] = list_of_subjects
    list_of_teaching_years = request.form.getlist('years')
    contact_info['list_years'] = list_of_teaching_years

    created, returned_data = Attendant.create(session, contact_info)

    return created, returned_data

@app.route('/thanks/<front_end_id>/<user_id>', methods=['GET'])
def thanks(front_end_id, user_id):
    createSession()
    attendant = Attendant.get_user_multi(session, front_end_id, user_id)
    session.expunge_all()
    session.close()
    if attendant:
        return render_template('tack.html', name=attendant.first_name, qrUrl=attendant.qr, front_end_id=attendant.front_end_id)
    else:
        return abort(404)


@app.route('/utstallare/', methods=['GET'])
@login_required
def admin():
    exhibitor = Exhibitor.get_exhibitor(session, current_user.id)
    labels = exhibitor.get_labels(session)
    session.expunge_all()
    session.close()
    return render_template("utstallare_inloggad.html", lables = labels)

@app.route('/utstallare/qr', methods=['GET'])
@login_required
def qr():
    exhibitor = Exhibitor.get_exhibitor(session, current_user.id)
    labels = exhibitor.get_labels(session)
    session.expunge_all()
    session.close()
    return render_template("Web QR.html", labels = labels)

@app.route('/attendant/<front_end_id>/<user_id>', methods=['POST'])
@login_required
def connect(front_end_id, user_id):
    print('Skapar connection')
    print(current_user.id)
    exhibitor = Exhibitor.get_exhibitor(session, current_user.id)
    attendant = Attendant.get_user_multi(session, front_end_id, user_id)
    if attendant:
        if exhibitor.got_connection(session, attendant.get_id(session)):
            connection = Connection.get_connection_by_users(session, exhibitor.get_id(), attendant.get_id(session))
            data = connection.get_data(session)
            labels = get_all_labels(session)
            connection_info = {'connections':data, 'labels':labels}
            session.expunge_all()
            session.close()
            return json.dumps(connection_info)
        else:
            connection = Connection(exhibitor.get_id(), attendant.get_id(session))
            session.add(connection)
            session.commit()
            connection_data = connection.get_data(session)
            session.expunge_all()
            labels = get_all_labels(session)
            session.close()
            connection_info = {'connections':connection_data, 'labels':labels}
            return json.dumps(connection_info)
    else:
        session.close()
        return json.dumps(False)

@app.route('/attendant/<front_end_id>/', methods=['GET'])
@login_required
def connect_by_frontend_id(front_end_id):
    attendants = Attendant.get_from_front_id(session, front_end_id)
    session.expunge_all()
    session.close()
    if len(attendants) == 0:
        return json.dumps(False)
    else:
        return json.dumps(attendants)


@app.route('/connection/<connection_id>', methods=['POST'])
@login_required
def uppdate_conection(connection_id):
    connection = Connection.get_connection(session, connection_id)
    if connection:
        if connection.get_exhibitor() == current_user.id:
            label_nrs = request.form.getlist('label_nrs')
            comment = request.form.get('comment')
            Label_to_Connection.remove(session, connection_id)
            for label_nr in label_nrs:
                label = Label.get_label(session, label_nr)
                if label.get_exhibitor() == current_user.id:
                    connection.add_label(session, label)
                else:
                    session.close()
                    return json.dumps({'status':False, 'error':'Du har inte behörighet'})
            connection.add_comment(session, comment)
            session.close()
            return json.dumps(True)
        else:
            session.close()
            return json.dumps({'status':False, 'error':'Du har inte behörighet'})
    else:
        session.close()
        return json.dumps({'status':False, 'error':'Hittades inte'})


def get_all_labels(session):
    exhibitor = Exhibitor.get_exhibitor(session, current_user.id)
    labels = exhibitor.get_labels(session)
    return json.dumps(labels)

@app.route('/label/<label_id>', methods=["GET"])
@login_required
def get_label(label_id):
    exhibitor = Exhibitor.get_exhibitor(session, current_user.id)
    label = Label.get_label(session, label_id)
    if label:
        if label.get_exhibitor() == exhibitor.get_id():
            session.close()
            return json.dumps(label.get_data())
        else:
            session.close()
            return 'Ej behörighet'
    else:
        session.close()
        return 'Taggen finns inte'

@app.route('/label/<label_id>', methods=["PUT"])
@login_required
def update_label(label_id):
    exhibitor = Exhibitor.get_exhibitor(session, current_user.id)
    label = Label.get_label(session, label_id)
    if label:
        if label.get_exhibitor() == exhibitor.get_id():
            response = label.update(session, 'Ny text', '#fff')
            session.close()
            return 'Taggen är uppdaterad!'
        else:
            session.close()
            return 'Ej behörighet'
    else:
        session.close()
        return 'Taggen finns inte'

@app.route('/label/', methods=["POST"])
@login_required
def create_label():
    exhibitor = Exhibitor.get_exhibitor(session, current_user.id)
    labelText = request.form.get('labelName')
    if len(labelText) > 0:
        label = Label(exhibitor, labelText, '#FFF')
        session.add(label)
        session.commit()
        label_data = label.get_data()
        session.close()
        return json.dumps(label_data)
    else:
        session.close()
        return json.dumps(False)

@app.route('/label/<label_id>', methods=["DELETE"])
@login_required
def delte_label(label_id):
    exhibitor = Exhibitor.get_exhibitor(session, current_user.id)
    label = Label.get_label(session, label_id)
    if label:
        if label.get_exhibitor() == exhibitor.get_id():
            response = label.delete(session)
            if response:
                session.close()
                return json.dumps(True)
            else:
                session.close()
                return json.dumps(False)
        else:
            session.close()
            return json.dumps(False)
    else:
        session.close()
        return json.dumps(False)


@app.route('/login_ajax/', methods=['POST'])
def log_in():
    ''' For ajax validation of login information '''
    email = request.form.get('username')
    user_psw = request.form.get('password')
    remember_me = request.form.get('remember')
    hashed = User.hash_password(user_psw)
    the_user = User.log_in(email, hashed)
    if the_user:
        if remember_me:
            login_user(the_user, remember=True)
        else:
            login_user(the_user)
        flash('Logged in successfully.')

        if (the_user.auth_level == 1) or (the_user.auth_level == "1"):
            exhibitor = Exhibitor.get_exhibitor(the_user.id)
            last_logged_in = exhibitor.get_last_logged_in()

            if last_logged_in is None:
                exhibitor.set_last_logged_in()
                return json.dumps({'logged_in': True, 'url':'/nytt_losenord/'})

            exhibitor.set_last_logged_in()
            return json.dumps({'logged_in': True, 'url':'/utstallare/'})

        return json.dumps({'logged_in': True, 'url':'/administrator/addexhibitor'})
    else:
        return json.dumps({'logged_in': False})


@app.route('/login/', methods=['POST'])
def log_in_user():
    ''' Call log_in user and return True or False if logged in or not '''
    createSession()
    email = request.form.get('username')
    user_psw = request.form.get('password')
    hashed = User.hash_password(user_psw)
    user = User.get_user(session, email)
    if user:
        if user.get_password() == hashed:
            key = user.generate_key(session)
            user_id = user.id
            session.expunge_all()
            session.close()
            return json.dumps({'logged_in':True, 'id':user_id, 'key':key })
        else:
            session.close()
            return json.dumps({'logged_in':False})
    else:
        session.close()
        return json.dumps({'logged_in':False})

@app.route('/save_to_excel/')
@login_required
def save_to_excel():
    exhibitor = Exhibitor.get_exhibitor(session, current_user.id)
    excel_file = exhibitor.create_excel(session)
    session.expunge_all()
    session.close()
    return send_file('excel/kontaktuppgifter' + str(current_user.id) + '.xlsx', as_attachment=True, attachment_filename='kontaktuppgifter.xlsx')


'''@app.route('/attendant/',methods=['GET'])
def get_attendants():
    attendants = Attendant.get_all_attendants()
    attendants_list = []
    for attendant in attendants:
        attendants_list.append(attendant.get_data())
    return json.dumps(attendants_list)'''

@app.route('/exhibitor/contacts', methods=['GET'])
@login_required
def get_exhibitor_contacts():
    connections = Connection.get_all_connections(session, current_user.id)
    connection_data = []
    for connection in connections:
        connection_data.append(connection.get_data(session))
    labels = get_all_labels(session)
    labels = {'connections':connection_data, 'labels':labels}
    session.expunge_all()
    session.close()
    return json.dumps(labels)


@app.errorhandler(405)
def page_not_found(e):
    return render_template("fel.html", error_list = ["405. Sidan hittades inte."])

@app.errorhandler(404)
def page_not_found(e):
    return render_template("fel.html", error_list = ["404. Sidan hittades inte."])

@app.errorhandler(400)
def page_not_found(e):
    return render_template("fel.html", error_list = e)


if __name__ == '__main__':
    app.run()
