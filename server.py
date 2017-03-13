from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash, redirect, send_file
from urllib.parse import urlparse, urljoin
import json

from itsdangerous import URLSafeTimedSerializer
from flask_recaptcha import ReCaptcha
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
app.config['RECAPTCHA_ENABLED'] = True
app.config['RECAPTCHA_SITE_KEY'] = "6LemXRYUAAAAABgJiRvPpJg8QCt2P94xabA0pWQl" # Localhost
app.config['RECAPTCHA_SECRET_KEY'] = "6LemXRYUAAAAAGVJHRdRqKFsDyt1DJg3EjnSKXWg" # Localhost

#login_manager = LoginManager()
#login_manager.init_app(app)
#login_manager.login_view = "log_in_user"
#login_manager.session_protection = "Basic"
#login_serializer = URLSafeTimedSerializer(app.secret_key)

recaptcha = ReCaptcha()
recaptcha.init_app(app)


def admin_requierd(myFunc):
    @wraps(myFunc)
    def wrapper(*args, **kwargs):
        if current_user.auth_level == 2:
            return myFunc(*args, **kwargs)
        else:
            return render_template("fel.html", error_list = ["403. Du har inte behörighet!"])
    return wrapper


def login_required(myFunc):
    @wraps(myFunc)
    def wrapper(*args, **kwargs):
        print(request.headers.get('id'))
        print(request.headers.get('token'))
        exhibitor = Exhibitor.get_exhibitor(request.headers.get('id'))
        if exhibitor:
            if exhibitor.is_authenticated(request.headers.get('token')):
                return myFunc(*args, **kwargs)
            else:
                abort(404)
        else:
            abort(404)
    return wrapper


@app.route('/utstallare/', methods=['GET'])
@login_required
def admin():
    exhibitor = Exhibitor.get_exhibitor(current_user.id)
    labels = exhibitor.get_labels()
    return render_template("utstallare_inloggad.html", lables = labels)

@app.route('/utstallare/qr', methods=['GET'])
@login_required
def qr():
    exhibitor = Exhibitor.get_exhibitor(current_user.id)
    labels = exhibitor.get_labels()
    return render_template("Web QR.html", labels = labels)

@app.route('/attendant/<front_end_id>/<user_id>', methods=['POST'])
@login_required
def connect(front_end_id, user_id):
    exhibitor = Exhibitor.get_exhibitor(current_user.id)
    attendant = Attendant.get_user_multi(front_end_id, user_id)
    if attendant:
        if exhibitor.got_connection(attendant.get_id()):
            connection = Connection.get_connection_by_users(exhibitor.get_id(), attendant.get_id())
            data = connection.get_data()
            labels = get_all_labels()
            connection_info = {'connections':data, 'labels':labels}
            return json.dumps(connection_info)
        else:
            global session
            session = Session()
            connection = Connection(exhibitor.get_id(), attendant.get_id())
            session.add(connection)
            session.commit()
            connection_data = connection.get_data()
            session.expunge_all()
            labels = get_all_labels()
            session.close()
            connection_info = {'connections':connection_data, 'labels':labels}
            return json.dumps(connection_info)
    else:
        return json.dumps(False)

@app.route('/attendant/<front_end_id>/', methods=['GET'])
@login_required
def connect_by_frontend_id(front_end_id):
    attendants = Attendant.get_from_front_id(front_end_id)
    if len(attendants) == 0:
        return json.dumps(False)
    else:
        return json.dumps(attendants)



@app.route('/connection/<connection_id>', methods=['POST'])
@login_required
def uppdate_conection(connection_id):
    connection = Connection.get_connection(connection_id)
    if connection:
        if connection.get_exhibitor() == current_user.id:
            label_nrs = request.form.getlist('label_nrs')
            print (label_nrs)
            comment = request.form.get('comment')
            Label_to_Connection.remove(connection_id)
            for label_nr in label_nrs:
                label = Label.get_label(label_nr)
                if label.get_exhibitor() == current_user.id:
                    connection.add_label(label)
                else:
                    return json.dumps({'status':False, 'error':'Du har inte behörighet'})
            connection.add_comment(comment)
            return json.dumps(True)
        else:
            return json.dumps({'status':False, 'error':'Du har inte behörighet'})
    else:
        return json.dumps({'status':False, 'error':'Hittades inte'})

@app.route('/label/', methods=["GET"])
@login_required
def get_all_labels():
    exhibitor = Exhibitor.get_exhibitor(current_user.id)
    labels = exhibitor.get_labels()
    return json.dumps(labels)

@app.route('/label/<label_id>', methods=["GET"])
@login_required
def get_label(label_id):
    exhibitor = Exhibitor.get_exhibitor(current_user.id)
    label = Label.get_label(label_id)
    if label:
        if label.get_exhibitor() == exhibitor.get_id():
            return json.dumps(label.get_data())
        else:
            return 'Ej behörighet'
    else:
        return 'Taggen finns inte'

@app.route('/label/<label_id>', methods=["PUT"])
@login_required
def update_label(label_id):
    exhibitor = Exhibitor.get_exhibitor(current_user.id)
    label = Label.get_label(label_id)
    if label:
        if label.get_exhibitor() == exhibitor.get_id():
            response = label.update('Ny text', '#fff')
            return 'Taggen är uppdaterad!'
        else:
            return 'Ej behörighet'
    else:
        return 'Taggen finns inte'

@app.route('/label/', methods=["POST"])
@login_required
def create_label():
    exhibitor = Exhibitor.get_exhibitor(current_user.id)
    labelText = request.form.get('labelName')
    if len(labelText) > 0:
        global session
        session = Session()
        label = Label(exhibitor, labelText, '#FFF')
        session.add(label)
        session.commit()
        label_data = label.get_data()
        session.close()
        return json.dumps(label_data)
    else:
        return json.dumps(False)

@app.route('/label/<label_id>', methods=["DELETE"])
@login_required
def delte_label(label_id):
    exhibitor = Exhibitor.get_exhibitor(current_user.id)
    label = Label.get_label(label_id)
    if label:
        if label.get_exhibitor() == exhibitor.get_id():
            response = label.delete()
            if response:
                return json.dumps(True)
            else:
                return json.dumps(False)
        else:
            return json.dumps(False)
    else:
        return json.dumps(False)

@app.route('/administrator/addexhibitor/')
@login_required
@admin_requierd
def admin_startpage():
    return render_template('admin.html')

@app.route('/administrator/listexhibitors/')
@login_required
@admin_requierd
def admin_list_exhibitors():
    exhibitors = Exhibitor.get_all_exhibitors()
    exhibitors_list = []
    for exhibitor in exhibitors:
        exhibitors_list.append(exhibitor.get_data())

    statistik = {
    'Utställare': len(Exhibitor.get_all_exhibitors()),
    'Besökare': len(Attendant.get_all_attendants()),
    'Kontaktutbyten':len(Connection.get_every_connection())
    }

    newlist = sorted(exhibitors_list, key=lambda k: k['company'].lower(), reverse=False)

    return render_template('admin_utstallare.html', exhibitors = newlist, statistik = statistik)

@app.route('/administrator/listattendants/')
@login_required
@admin_requierd
def admin_list_attendants():
    attendants = Attendant.get_all_attendants()
    attendants_list = []
    for attendant in attendants:
        attendants_list.append(attendant.get_data())

    statistik = {
    'Utställare': len(Exhibitor.get_all_exhibitors()),
    'Besökare': len(Attendant.get_all_attendants()),
    'Kontaktutbyten':len(Connection.get_every_connection())
    }

    newlist = sorted(attendants_list, key=lambda k: k['first_name'].lower(), reverse=False)

    return render_template('admin_besokare.html', attendants = newlist, statistik = statistik)

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
    ''' Call log_in user and return template depending on user level '''
    email = request.form.get('username')
    user_psw = request.form.get('password')
    hashed = User.hash_password(user_psw)
    user = User.get_user(email)
    if user:
        if user.get_password() == hashed:
            return json.dumps({'logged_in':True, 'id':user.id, 'key':user.generate_key() })
        else:
            return json.dumps({'logged_in':False})
    else:
        return json.dumps({'logged_in':False})





def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@app.route('/logout/')
@login_required
def logout():
    ''' Logs out user '''
    current_user.log_out()
    logout_user()
    return redirect('/login/')

@app.route('/save_to_excel/')
@login_required
def save_to_excel():
    exhibitor = Exhibitor.get_exhibitor(current_user.id)
    excel_file = exhibitor.create_excel()
    return send_file('excel/kontaktuppgifter' + str(current_user.id) + '.xlsx', as_attachment=True, attachment_filename='kontaktuppgifter.xlsx')

@app.route('/exhibitor/', methods=['POST'])
@login_required
@admin_requierd
def create_exhibitor():
    company_name = request.form.get('businessName')
    email = request.form.get('businessMail')
    status, message = Exhibitor.create(company_name, email)
    if status:
        return json.dumps({'status':status})
    else:
        return json.dumps({'status':status, 'error':message})

@app.route('/exhibitor/<id>', methods=['DELETE'])
@login_required
def delte_exhibitor(id):
    if current_user.id == id or current_user.auth_level ==2:
        exhibitor = Exhibitor.get_exhibitor(id)
        if exhibitor:
            exhibitor.delete()
            if current_user.id == id:
                return redirect('/logout')
            else:
                return json.dumps(True)
        else:
            return json.dumps(False)
    else:
        return json.dumps(False)

@app.route('/exhibitor/', methods=['GET'])
@login_required
@admin_requierd
def get_exhibitors():
    exhibitors = Exhibitor.get_all_exhibitors()
    exhibitors_list = []
    for exhibitor in exhibitors:
        exhibitors_list.append(exhibitor.get_data())
    return json.dumps(exhibitors_list)

@app.route('/attendant/',methods=['GET'])
def get_attendants():
    attendants = Attendant.get_all_attendants()
    attendants_list = []
    for attendant in attendants:
        attendants_list.append(attendant.get_data())
    return json.dumps(attendants_list)

@app.route('/admin/contacts', methods=['GET'])
def list_contacts():
    return render_template('utstallare_inloggad.html')

@app.route('/exhibitor/contacts', methods=['GET'])
@login_required
def get_exhibitor_contacts():
    connections = Connection.get_all_connections(current_user.id)
    connection_data = []
    for connection in connections:
        connection_data.append(connection.get_data())
    labels = get_all_labels()
    labels = {'connections':connection_data, 'labels':labels}
    return json.dumps(labels)

@app.route('/exhibitor/<id>/sendemail/', methods=['POST'])
@login_required
@admin_requierd
def exhibitor_send_email(id):
    exhibitor = Exhibitor.get_exhibitor(id)
    if exhibitor:
        exhibitor.send_new_email()
        return json.dumps(True)
    else:
        return json.dumps(False)

@app.route('/nytt_losenord/', methods=['GET', 'POST'])
def create_new_password():
    ''' Create new password for exhibitor first time they log in '''
    if request.method == 'GET':
        return render_template("reset_password.html")
    else:
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        if password == confirm_password:
            current_user.set_password(password)
            return render_template("new_password_saved.html")
        else:
            return "Lösenorden du fyllde i stämde inte överrens."

@app.route('/glomt_losenord/', methods=['GET'])
def forgot_password_template():
    return render_template('email_to_change_pw.html')

@app.route('/glomt_losenord/', methods=['POST'])
def forgotten_password():
    mejl = request.form.get('username')
    user = User.get_user(mejl)
    if user:
        user.forgotten_password()
    return render_template('email_is_sent.html')

@app.route('/glomt_losenord/<wild_card>', methods=['GET', 'POST'])
def update_password(wild_card):
    if request.method == 'GET':
        user = User.get_user_by_url(wild_card)
        if user:
            return render_template('change_password.html', wild_card = wild_card)
        else:
            return render_template('fel.html', error_list = ["Ogiltig url."])
    else:
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        if password1 == password2:
            user = User.get_user_by_url(wild_card)
            if user:
                if user.validate_url_time():
                    user.set_password(password1)
                    user.deactivte_url()
                    return render_template('changed_pw_true.html')
                else:
                    return render_template('fel.html', error_list = ["Det gick tyvärr inte att uppdatera ditt lösenord."])
            else:
                return 'Ogiltig url'
        else:
            return 'Ogiltig url'

@app.errorhandler(405)
def page_not_found(e):
    return render_template("fel.html", error_list = ["405. Sidan hittades inte."])

@app.errorhandler(404)
def page_not_found(e):
    return render_template("fel.html", error_list = ["404. Sidan hittades inte."])

@app.errorhandler(400)
def page_not_found(e):
    return render_template("fel.html", error_list = e)

'''@login_manager.user_loader
def load_user(session_token):
    session = Session()
    user = session.query(User).filter_by(session_token=session_token).first() # eller hämta via id
    return user'''

if __name__ == '__main__':
    app.run(host='0.0.0.0')
