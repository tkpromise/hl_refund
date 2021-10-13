import os
import uuid
import click
import sqlite3
import urllib.request
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, url_for, render_template,current_app, g
from flask.cli import with_appcontext

UPLOAD_FOLDER = 'static/uploads/'

app = Flask(__name__)
app.secret_key='secret key'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['DATABASE'] = os.path.join(app.instance_path, 'hl.sqlite3')

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def random_filename(filename):
    ext = os.path.splitext(filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename

# 数据库操作
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/', methods=['GET', 'POST'])
def upload_form():
	return render_template('upload.html')

@app.route('/hl', methods=['GET', 'POST'])
def hl():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('请上传身份证件')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('请选择有效图片')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            new_filename = random_filename(file.filename)
            filename = secure_filename(new_filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            uuid = os.path.splitext(filename)[0]
            meb_name = request.form['mebName']
            phone_num = request.form['phoneNum']
            bank_name = request.form['bankName']
            bank_address = request.form['bankAddress']
            bank_number = request.form['bankNumber']
            id_name = filename

            db = get_db()
            try:
                db.execute(
                    "INSERT INTO user (uuid, meb_name, phone_num, bank_name, bank_address, bank_number, id_name) VALUES(?,?,?,?,?,?,?)",
                    (uuid, meb_name, phone_num, bank_name, bank_address, bank_number, id_name)
                )
                db.commit()
            except:
                flash('提交异常')
            else:
                return redirect(url_for('success'))

    return render_template('hl.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/ad')
def ad():
    db = get_db()
    users = db.execute(
        'select * from user'
    ).fetchall()
    return render_template('ad.html', users=users)

@app.route('/edit/<uuid>')
def edit(uuid):
    return uuid

@app.route('/', methods=['POST'])
def upload_image():
	if 'file' not in request.files:
		flash('No file part')
		return redirect(request.url)
	file = request.files['file']
	if file.filename == '':
		flash('No image selected for uploading')
		return redirect(request.url)
	if file and allowed_file(file.filename):
		filename = secure_filename(file.filename)
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		#print('upload_image filename: ' + filename)
		flash('Image successfully uploaded and displayed below')
		return render_template('upload.html', filename=filename)
	else:
		flash('Allowed image types are -> png, jpg, jpeg, gif')
		return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
	#print('display_image filename: ' + filename)
	return redirect(url_for('static', filename='uploads/' + filename), code=301)
