import sqlite3
import uuid
import requests
import flask
from flask import render_template, url_for
from flask import request, redirect
from werkzeug.utils import secure_filename

app = flask.Flask(__name__)

DB_NAME = 'portfolio.db'

tool_icons = {
        'Python': '🐍',"Falsk": '🌳', 'HTML': '📄', 'CSS': '🎨',
        'HTML/CSS': '🖌️', 'Git': '🔧', 'GitHub': '🦀', 'Telegram': '✈️',
        'Телеграм': '✈️', 'SQL': '📔', 'SQLite': '📘', 'JavaScript': '⚡',
        'JS': '⚡', 'Jinja': '🧩'
    }

def test_user():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM portfolio')
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.execute('''INSERT INTO portfolio (uuid, name, biography, github, telegram, avatar, skills ) VALUES (?,?,?,?,?,?,?)
        ''', (
            '1234',
            'Test',
            'Програмирует на Python',
            'Alexandr',
            '@Noname_nn',
            'placeholder.png',
            'Python'
        ))

        conn.commit()
        conn.close()

@app.route('/portfolio/<uuid>')
def view_portfolio(uuid):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM portfolio WHERE uuid = ?', (uuid,))
    user = cursor.fetchone()
    conn.close()

    _,__,name,biography,github,telegram,avatar,skills = user
    if not user:
        return'Портфолио не найдено', 404

    skills= skills.split(',')

    projects = []

    try:
        github = github

        url = f'https://api.github.com/users/{github}/repos'

        response = requests.get(url)

        if response.ok:
            repos = response.json()[:6]

            for repo in repos:
                projects.append({ 'title': repo['name'],'description': repo['description'] or 'Без описания','link': repo['html_url']})

    except Exception:
        projects = []





    return render_template('portfolio.html',name=name,bio=biography,github=github,telegram=telegram,avatar=avatar, skills=skills, projects=projects, tool_icons=tool_icons)


@app.route('/generate', methods=['POST'])
def generate():
    form = request.form
    avatar = request.files.get('avatar')

    uid = str(uuid.uuid4())

    avatar_filename = ''

    if avatar and avatar.filename:
        filename = secure_filename(f'{uuid}_{avatar.filename}')
        avatar_path = f'static/uploads/{filename}'
        avatar.save(avatar_path)
        avatar_filename = avatar_path.replace('static/', '')

    github = form['github'].strip() \
        .replace('https://github.com/', '') \
        .replace('/', '')

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO portfolio (uuid, name, biography, github, telegram, avatar, skills )VALUES (?,?,?,?,?,?,?)''',
              (uid, form['name'], form['bio'], github, form['telegram'], avatar_filename, form['skills']))
    conn.commit()
    conn.close()

    return redirect(url_for('all_portfolios'))



@app.route('/form')
def form():
    return render_template('form.html')


@app.route('/')
def all_portfolios():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('Select uuid, name, biography, avatar, skills FROM portfolio')
    raw_data = c.fetchall()
    conn.close()

    filter_skill = request.args.get('skill')
    if filter_skill:
        filter_skill = filter_skill.strip().lower()

    else:
        filter_skill = None

    portfolios = []

    for uuid, name, bio, avatar, skills_str in raw_data:

        skills = []
        for s in skills_str.split(','):
            s = s.strip()
            if s:
                skills.append(s)

        skills_lower = []
        for s in skills:
            skills_lower.append(s.lower())

        if filter_skill is None or filter_skill in skills_lower:
            portfolios.append((uuid, name, bio, avatar, skills))

    return render_template('all_portfolios.html', portfolios=portfolios, tool_icons=tool_icons, current_skill=filter_skill or '')



if __name__ == '__main__':
    app.run()