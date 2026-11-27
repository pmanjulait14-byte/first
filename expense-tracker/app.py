from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import request, redirect
from werkzeug.security import generate_password_hash
from flask_login import LoginManager
from flask_login import UserMixin
import os
from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
    UserMixin
)
from werkzeug.security import check_password_hash

app = Flask(__name__)

login_manager = LoginManager(app)

app.config['SECRET_KEY'] = 'my-super-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.getenv('DATABASE_URL')
    or 'sqlite:///expense.db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)

@app.route('/')
def home():
    category = request.args.get('category')
    return "Hello"

@app.route('/login',
methods=['GET','POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(
            email=email
        ).first()
        print("--------------",user)
        print("--------------",user.password)
        print("--------------",check_password_hash(
                user.password,
                password
            ))

        if user and check_password_hash(
            user.password,
            password
        ):
            login_user(user)
            return redirect('/dashboard')

    return render_template(
        'login.html'
    )

@app.route('/dashboard')
@login_required
def dashboard():

    category = request.args.get('category')

    if category:
        expenses = Expense.query.filter_by(
            category=category,
            user_id=current_user.id
        ).all()
    else:
        expenses = Expense.query.filter_by(
            user_id=current_user.id
        ).all()

    total_expense = sum(
        expense.amount
        for expense in expenses
    )

    return render_template(
        'dashboard.html',
        expenses=expenses,
        total=total_expense
    )

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(
            request.form['password']
        )

        user = User(
            username=username,
            email=email,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        return redirect('/')

    return render_template('register.html')

@app.route(
'/expense/add',
methods=['GET','POST']
)
@login_required
def add_expense():

    if request.method == 'POST':

        expense = Expense(
            title=request.form['title'],
            amount=float(
                request.form['amount']
            ),
            category=request.form['category'],
            date=request.form['date'],
            user_id=current_user.id
        )

        db.session.add(expense)
        db.session.commit()

        return redirect('/dashboard')

    return render_template(
        'add_expense.html'
    )

@app.route(
    '/expense/edit/<int:id>',
    methods=['GET','POST']
)
@login_required
def edit_expense(id):

    expense = Expense.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    if request.method == 'POST':

        expense.title = request.form['title']
        expense.amount = float(
            request.form['amount']
        )

        expense.category = request.form['category']

        db.session.commit()

        return redirect('/dashboard')

    return render_template(
        'edit_expense.html',
        expense=expense
    )

@app.route(
    '/expense/delete/<int:id>'
)
@login_required
def delete_expense(id):

    expense = Expense.query.filter_by(
        id=id,
        user_id=current_user.id
    ).first_or_404()

    db.session.delete(expense)

    db.session.commit()

    return redirect('/dashboard')

@app.route('/export/csv')
def export_csv():

    expenses = Expense.query.all()

    data = []

    for e in expenses:

        data.append({
            "Title":e.title,
            "Amount":e.amount,
            "Category":e.category
        })

    df = pd.DataFrame(data)

    df.to_csv(
        'expenses.csv',
        index=False
    )

    return "CSV Created"

@app.route('/export/pdf')
def export_pdf():

    pdf = canvas.Canvas(
        "report.pdf"
    )

    pdf.drawString(
        100,
        800,
        "Expense Report"
    )

    pdf.save()

    return "PDF Generated"

class User(db.Model, UserMixin):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )


class Expense(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    title = db.Column(
        db.String(200)
    )

    amount = db.Column(
        db.Float
    )

    category = db.Column(
        db.String(100)
    )

    date = db.Column(
        db.String(50)
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('user.id')
    )



with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


if __name__ == '__main__':
    app.run(debug=True)
