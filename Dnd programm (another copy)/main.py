'''
Autor: Armin Kull

Alustamis kuupäev: 08.11.2024

Lõpetamise kuupäev: ...
Kirjeldus: Varasema tkinter programmi tegemine htmli abil

Kasutatud allikad:
https://devdocs.io/css/
https://developer.mozilla.org/en-US/docs/Web/HTML
https://www.postgresql.org/docs/current/sql.html
https://gist.github.com/vkotovv/6281951
'''

from flask import Flask, render_template, abort, request, redirect, session, flash
from sqlalchemy import text
import os
from Other import *
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/info.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '4@23kRrm-"#f!Ma!9&@4CvH^^+fs(=IH0"qc`6dQLQQ}`Yjz2{'
db.init_app(app)

#klassid=[i for i in fail_open_read_lines("Important/select_Class.txt")]
#taustad=[i for i in fail_open_read_lines("Important/select_BG.txt")]
#rassid=[i for i in fail_open_read_lines("Important/select_Race.txt")]
#loitsud=[i for i in fail_open_read_lines("Important/Spell_list.txt")]
#vaike_tekst=read_and_dictionary("Important/small_text.txt")

@app.route('/')
def esileht():
    return render_template('esileht.html')

@app.route('/klassid')
def klass():
    klassid = [i for i in db.session.execute(
        text('SELECT nimi, small_text FROM Klass WHERE homebrew_id IS NULL')).fetchall()]
    homebrews = [i for i in db.session.execute(
        text('SELECT Klass.nimi, Klass.small_text FROM Klass, Homebrew WHERE type=:type AND kasutaja_id=:user_id AND homebrew_id IS NOT NULL'),
        {'type': 'Class', 'user_id': session.get('user_id')}).fetchall()]
    print(klassid[0])
    return render_template('klass.html',
                           klassid=klassid,
                           homebrews=homebrews)

@app.route('/klass')
def klass_info():
    klass_nimi = request.args.get('nimi')
    klass = Klass.query.filter_by(nimi=klass_nimi).first()
    feature_names = [name.strip() for name in klass.features.split(',')]
    placeholders = ', '.join([f":name{i}" for i in range(len(feature_names))])
    params = {f"name{i}": name for i, name in enumerate(feature_names)}
    query = text(f'SELECT nimi, text FROM Features WHERE nimi IN ({placeholders})')
    results = db.session.execute(query, params).fetchall()
    levels = {}
    for i in range(1, 21):
        val = getattr(klass, f"lvl{i}", None)
        if val:
            levels[i] = val.strip()
    features = {row.nimi: row.text for row in results}
    return render_template('klass_info.html',
                           klass=klass,
                           levels=levels,
                           features=features)

@app.route('/taustad')
def taust():
    taustad = [i for i in db.session.execute(
        text('SELECT nimi FROM Taust WHERE homebrew_id IS NULL')).fetchall()]
    homebrews = [i for i in db.session.execute(
        text('SELECT nimi FROM Homebrew WHERE type=:type AND kasutaja_id=:user_id'),
        {'type': 'BG', 'user_id': session.get('user_id')}).fetchall()]
    abort(404)
    #return render_template('taust.html',
                           #taustad=taustad,
                           #homebrews=homebrews)

@app.route('/taustad/<taust_nimi>')
def taust_info(taust_nimi):
    taust=Taust.query.filter_by(nimi=taust_nimi).first()
    text = cutter(taust.text)
    skill_proficiencies = cutter2(taust.skill_proficiencies)
    abort(404)
    #return render_template('taust_info.html',
                           #text=text,
                           #choosing_text=skill_proficiencies)

@app.route('/rassid')
def rass():
    rassid = [i for i in db.session.execute(
        text('SELECT nimi FROM Rass WHERE homebrew_id IS NULL')).fetchall()]
    homebrews = [i for i in db.session.execute(
        text('SELECT nimi FROM Homebrew WHERE type=:type AND kasutaja_id=:user_id'),
        {'type': 'Race', 'user_id': session.get('user_id')}).fetchall()]
    abort(404)
    #return render_template('rass.html',
                           #rassid=rassid,
                           #homebrews=homebrews)

@app.route('/rassid/<rass_nimi>')
def rass_info(rass_nimi):
    rass=Rass.query.filter_by(nimi=rass_nimi).first()
    text = cutter(rass.text)
    ability_score_increase = cutter2(rass.ability_score_increase)
    abort(404)
    #return render_template('rass_info.html',
                           #text=text,
                           #choosing_text=ability_score_increase)


@app.route('/homebrew')
def homebrew():
    return render_template('homebrew.html')

@app.route('/homebrew/klass', methods=['GET', 'POST'])
def homebrew_klass():
    if session.get('user_id')==None:
        session['error']='Logige sisse või looge kasutaja'
        return redirect('/login')
    saving_throws = db.session.execute(
        text('SELECT saving_throw FROM Klass WHERE nimi=:nimi'),
        {'nimi': 'Class'}).fetchall()
    weapons= db.session.execute(
        text('SELECT category FROM Equipment WHERE type=:type'),
        {'type': 'Weaopn'}).fetchall()

    if request.method == 'POST':
        p_nimi = request.form['nimi']
        p_text = request.form['text']
        p_small_text = request.form['small-text']
        p_hitpoints = request.form['hitpoints']
        p_saving_throws = ', '.join(request.form.getlist('saving_throws'))
        p_armor = ', '.join(request.form.getlist('armor'))
        p_weapons = ', '.join(request.form.getlist('weapons'))
        p_tools = ', '.join(request.form.getlist('tools'))
        p_skills = ', '.join(request.form.getlist('skills'))
        p_features_json = request.form['features']
        features_raw = request.form['features']
        features_by_level = json.loads(features_raw)

        # Save the uploaded image
        file = request.files['image']
        image_path = os.path.join('static/Class_img', f'{p_nimi}.png')
        file.save(image_path)

        # Add homebrew base entry
        homebrew_entry = Homebrew(type='Class', nimi=p_nimi, kasutaja_id=session.get('user_id'))
        db.session.add(homebrew_entry)
        db.session.flush()

        homebrew_id = homebrew_entry.id

        level_features = {}
        feat_names = []

        for i in range(1, 21):
            lvl_key = f"lvl{i}"
            feats = features_by_level.get(str(i), [])
            names = [feat["name"] for feat in feats]

            level_features[lvl_key] = names
            feat_names.extend(names)

        # Add class info
        print(level_features)
        db.session.add(Klass(
            nimi=p_nimi,
            saving_throw=p_saving_throws,
            text=p_text,
            small_text=p_small_text,
            hit_points=p_hitpoints,
            proficiencies=f'Armor: {p_armor}\nWeapons: {p_weapons}\nTools: {p_tools}\nSaving Throws: {p_saving_throws}\nSkills: {p_skills}',
            homebrew_id=homebrew_id,
            features=', '.join(feat_names),
            lvl1=', '.join(level_features['lvl1']),
            lvl2=', '.join(level_features['lvl2']),
            lvl3=', '.join(level_features['lvl3']),
            lvl4=', '.join(level_features['lvl4']),
            lvl5=', '.join(level_features['lvl5']),
            lvl6=', '.join(level_features['lvl6']),
            lvl7=', '.join(level_features['lvl7']),
            lvl8=', '.join(level_features['lvl8']),
            lvl9=', '.join(level_features['lvl9']),
            lvl10=', '.join(level_features['lvl10']),
            lvl11=', '.join(level_features['lvl11']),
            lvl12=', '.join(level_features['lvl12']),
            lvl13=', '.join(level_features['lvl13']),
            lvl14=', '.join(level_features['lvl14']),
            lvl15=', '.join(level_features['lvl15']),
            lvl16=', '.join(level_features['lvl16']),
            lvl17=', '.join(level_features['lvl17']),
            lvl18=', '.join(level_features['lvl18']),
            lvl19=', '.join(level_features['lvl19']),
            lvl20=', '.join(level_features['lvl20'])
        ))
        for i, feats in features_by_level.items():
            for feat in feats:
                db.session.add(Features(
                    nimi=feat['name'],
                    text=feat['description']
                ))
        db.session.commit()
        flash("Class added!")
        return redirect('/homebrew')

    else:
        return render_template('homebrew_klass.html',
                               saving_throws=cutter2(saving_throws[0][0]),
                               weapons=weapons,)

@app.route('/homebrew/rass', methods=['GET', 'POST'])
def homebrew_rass():
    if session.get('user_id')==None:
        session['error']='Logige sisse või looge kasutaja'
        return redirect('/reg')
    ability_score_increases = db.session.execute(
        text('SELECT ability_score_increase FROM Rass WHERE nimi=:nimi'),
        {'nimi': 'Select Race'}).fetchall()
    if request.method == 'POST':
        p_nimi = request.form['nimi']
        p_choosing_text = ', '.join(request.form.getlist('checkbox'))
        p_text = request.form['text']
        file = request.files["image"]
        file.save(os.path.join('static/Race_img', f'{p_nimi}.png'))
        db.session.add(Homebrew(type='Race',
                                nimi=p_nimi,
                                kasutaja_id=session.get('user_id')))
        db.session.flush()
        homebrew_id = db.session.execute(
            text('SELECT id FROM Homebrew WHERE nimi=:nimi'),
            {'nimi': p_nimi}).fetchall()
        db.session.add(Rass(nimi=p_nimi,
                             ability_score_increase=p_choosing_text,
                             text=p_text,
                             homebrew_id=homebrew_id[0][0]))
        db.session.commit()
        return redirect('/homebrew')
    else:
        abort(404)
        #return render_template('homebrew_rass.html',
                           #ability_score_increases=cutter2(ability_score_increases[0][0]))

@app.route('/homebrew/taust', methods=['GET', 'POST'])
def homebrew_taust():
    if session.get('user_id') == None:
        session['error'] = 'Logige sisse või looge kasutaja'
        return redirect('/reg')
    skill_proficiencies = db.session.execute(
        text('SELECT skill_proficiencies FROM Taust WHERE nimi=:nimi'),
        {'nimi': 'Select Background'}).fetchall()
    print(skill_proficiencies)
    if request.method == 'POST':
        p_nimi = request.form['nimi']
        p_choosing_text = ', '.join(request.form.getlist('checkbox'))
        p_text = request.form['text']
        file = request.files["image"]
        file.save(os.path.join('static/BG_img', f'{p_nimi}.png'))
        features_json = request.form.get("features")
        features_by_level = json.loads(features_json)
        db.session.add(Homebrew(type='BG',
                                nimi=p_nimi,
                                kasutaja_id=session.get('user_id')))
        db.session.flush()
        homebrew_id = db.session.execute(
            text('SELECT id FROM Homebrew WHERE nimi=:nimi'),
            {'nimi': p_nimi}).fetchall()
        db.session.add(Taust(nimi=p_nimi,
                            skill_proficiencies=p_choosing_text,
                            text=p_text,
                            homebrew_id=homebrew_id[0][0]))
        db.session.commit()
        return redirect('/homebrew')
    else:
        abort(404)
        #return render_template('homebrew_taust.html',
                               #skill_proficiencies=cutter2(skill_proficiencies[0][0]))

@app.route('/loitsud')
def loits():
    loitsud = [i for i in Loits.query.all()]
    return render_template('loitsud.html',
                           loitsud=loitsud)

@app.route('/loits')
def loits_info():
    loits_nimi = request.args.get('nimi')
    loits = Loits.query.filter_by(nimi=loits_nimi).first()
    return render_template('loitsud_info.html', loits=loits)

@app.route('/login', methods=['POST', 'GET'])
def reg():
    error = session.pop('error', None)
    if 'register' in request.form:
        p_nimi = request.form.get('reg_nimi')
        p_text = request.form.get('reg_text')
        p_mail = request.form.get('reg_mail')

        if not p_nimi or not p_text or not p_mail:
            error = "Kõik väljad peavad olema täidetud!"
        else:
            existing_user = Kasutajad.query.filter_by(nimi=p_nimi).first()
            existing_email = Kasutajad.query.filter_by(mail=p_mail).first()

            if existing_user:
                flash("Selline kasutajanimi juba eksisteerib!")
            elif existing_email:
                flash("See email on juba kasutusel!")
            elif not is_valid_email(p_mail):
                flash("Email ei ole korrektne")
            else:
                hashed_password = generate_password_hash(p_text)
                new_user = Kasutajad(nimi=p_nimi,
                                     parool=hashed_password,
                                     mail=p_mail)
                db.session.add(new_user)
                db.session.commit()
                flash("Olete registreerunud!")
                session['user_id'] = new_user.id
                return redirect("/")

    elif 'login' in request.form:
        p_nimi = request.form.get('login_nimi')
        p_text = request.form.get('login_text')

        if not p_nimi or not p_text:
            flash("Kasutajanimi ja parool peavad olema täidetud!")
        else:
            user = Kasutajad.query.filter_by(nimi=p_nimi).first()

            if user and check_password_hash(user.parool, p_text):
                session['user_id'] = user.id
                flash("Olete sisse logitud!")
                return redirect("/")
            else:
                flash("Vale kasutajanimi või parool!")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session['error'] = 'Olete välja logitud'
    return redirect("/login")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

if __name__ == '__main__':
    #with app.app_context():
        #clear_data(db.session)
        #db.create_all()
        #lisa(klassid, taustad, rassid, loitsud, vaike_tekst)
        #db.session.commit()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
