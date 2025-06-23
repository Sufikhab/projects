from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from forms import LoginForm, RegisterForm
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///notes.db'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(150))
    encryption_key = db.Column(db.String(44))  # base64 encoded 32-byte key

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        self.encryption_key = base64.urlsafe_b64encode(password.encode('utf-8').ljust(32)[:32]).decode()

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_fernet(self):
        return Fernet(self.encryption_key.encode())


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    encrypted_content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.before_request
def create_tables():
    db.create_all()


# Routes
@app.route('/')
@login_required
def index():
    notes = Note.query.filter_by(user_id=current_user.id).all()
    f = current_user.get_fernet()
    decrypted_notes = [f.decrypt(n.encrypted_content.encode()).decode() for n in notes]
    return render_template('notes.html', notes=decrypted_notes)


@app.route('/add_note', methods=['POST'])
@login_required
def add_note():
    content = request.form.get('note')
    f = current_user.get_fernet()
    encrypted = f.encrypt(content.encode()).decode()
    note = Note(encrypted_content=encrypted, user_id=current_user.id)
    db.session.add(note)
    db.session.commit()
    flash('Note saved securely!')
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registered! Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out.')
    return redirect(url_for('login'))
