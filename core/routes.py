from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from core import db
from core.models import User, TestResult

main = Blueprint('main', __name__)

@main.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('main.login'))
    return render_template('index.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember_me = True if request.form.get('remember_me') else False

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user, remember=remember_me)
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('main.index')
            return redirect(next_page)
        else:
            flash('Неверное имя пользователя или пароль', 'error')

    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password2 = request.form['password2']

        if password != password2:
            flash('Пароли не совпадают', 'error')
            return render_template('register.html')

        if User.query.filter_by(username=username).first():
            flash('Пользователь с таким именем уже существует', 'error')
            return render_template('register.html')

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('Вы успешно зарегистрировались!', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/profile')
@login_required
def profile():
    user_results = TestResult.query.filter_by(user_id=current_user.id).order_by(TestResult.timestamp.desc()).limit(10).all()

    results_data = []
    for result in user_results:
        results_data.append({
            'id': result.id,
            'timestamp': result.timestamp.strftime('%d.%m.%Y %H:%M'),
            'average_reaction_time': result.average_reaction_time,
            'min_reaction_time': result.min_reaction_time,
            'max_reaction_time': result.max_reaction_time,
            'correct_responses': result.correct_responses,
            'total_attempts': result.total_attempts,
            'false_responses': result.false_responses,
            'previous_avg_comparison': result.previous_avg_comparison
        })
    
    return render_template('profile.html', results=results_data)

@main.route('/leaderboard')
@login_required
def leaderboard():
    top_results = db.session.query(
        User.username,
        db.func.avg(TestResult.average_reaction_time).label('avg_reaction_time'),
        db.func.count(TestResult.id).label('test_count')
    ).join(TestResult).group_by(User.id).order_by('avg_reaction_time').limit(10).all()

    return render_template('leaderboard.html', top_results=top_results)


@main.route('/rules')
def rules():
    return render_template('rules.html')