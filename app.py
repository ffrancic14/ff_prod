# uključujemo iz modula flask, segmente (klase i funkcionalnosti)
from random import random

from flask import Flask, render_template, request, redirect, jsonify
# ORM sustav za rad s SQLite bazom
from flask_sqlalchemy import SQLAlchemy
import requests
# nije nužno, ali ako želimo pisati SQL upite i izvršavati, funkcija text() će izvršiti njihovu "pripremu"
from sqlalchemy import text

# definiranje objekta Flask aplikacije
app = Flask(__name__)
# definicija putanje/imena do baze
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///filmovi.db'
# nije potrebna modifikacija - nebitno za projekt, ali štedi upotrebi memorije
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# ključ koji je važan radi sigurnosti sesija
# preporuča se koristiti "random" string
app.config['SECRET_KEY'] = 'fdghdftz5473#$'
# kreiranje objekta "db" za rad sa SQLite bazom
db = SQLAlchemy(app)


# definicija klasa (modela) tabela
class Jobs(db.Model):
    __tablename__ = 'jobs'  # definiranje imena tablice u bazi (klasa i naziv tabele ne trebaju biti isti)
    # definiranje polja tabele:
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    naziv = db.Column(db.String(50), nullable=False, unique=False)
    kategorija = db.Column(db.String(25), nullable=False)
    ocjena = db.Column(db.Float, nullable=False)


class Glumac(db.Model):
    __tablename__ = 'actor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ime = db.Column(db.String(50), nullable=False)
    prezime = db.Column(db.String(50), nullable=False)
    # unique = True - osigurava da ne možemo imati 2 zapisa s istom vrijednošću tog polja
    oib = db.Column(db.Integer, nullable=False, unique=False)
    datum_rodjenja = db.Column(db.DateTime, nullable=False)
    spol = db.Column(db.String(1), nullable=False)
    # jedan glumac pripada samo jednom filmu - "lakša verzija"
    film_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)


'''
# ako bismo definirali da jedna glumac može biti u više filmova
class GlumciFilmova(db.Model):
    __tablename__ = 'movie_actors'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # definicija "stranog ključa" (povezivanje 2 tabele)
    film_id = db.Column(db.Integer, db.ForeignKey('Film.id'), nullable=False)
    glumac_id = db.Column(db.Integer, db.ForeignKey('Glumac.id'), nullable=False)
    # jedinstveni index koji kombinira 2 polja
    db.UniqueConstraint('film_id', 'glumac_id', name='ndx_FilmGlumac')
'''


# definiramo rute
@app.route('/')  # ako nije definirana metoda, standardno 'GET' se dohvaća. GET metoda je poziv preko adrese
def pocetna():
    return render_template('index.html')


# pozivanje stranice za prikaz popisa svih filmova
@app.route('/jobs', methods=["GET", "POST"])
def jobs():
    jobs = []
    jobsDb = []
    callDb = request.form.get('callDb', None)
    callApi = request.form.get('callApi', None)
    if callDb is not None:
        jobs = db.session.query(Jobs).order_by(Jobs.id).all()

    if callApi is not None:
        urlJobs = 'https://jobicy.com/api/v2/remote-jobs'
        # example: https://jobicy.com/api/v2/remote-jobs?count=20&tag=python
        # jobs_api = requests.get(urlJobs.format()).json()
        apiResult = requests.get('https://jobicy.com/api/v2/remote-jobs?count=2&tag=python').json()
        jobs = apiResult['jobs']

        for i in jobs:
            i['naziv'] = i['jobTitle']

            # jobsDb.append(
                # Jobs(id=int(i["id"]), naziv=i["jobTitle"] + 'sadas', kategorija=i['jobIndustry'][0],
                #      ocjena=5))

        # db.session.add_all(jobsDb)
        # db.session.commit()

    # print("callApi: ", callApi)
    # print("call db: ", callDb)

    return render_template('jobs.html', jobs=jobs)


@app.route("/forward/", methods=['POST'])
def move_forward():
    keyword = request.form['keyword']
    location = request.form['location']
    industry = request.form['industry']
    count = request.form['count']
    print("result: ")
    print("keyword: ", keyword)
    print("location: ", location)
    print("industry: ", industry)
    print("count: ", count)

    return "super"
    # Moving forward code
    # forward_message = "Moving Forward..."
    # return forward_message


@app.route('/glumci')
def glumci():
    return 'glumci...'


@app.route('/film_brisi/<int:film_id>')
def film_brisi(film_id):
    # film=db.session.query(Film).filter_by(id=film_id).first()
    db.session.delete(film)
    db.session.commit()
    return redirect(app.url_for('jobs'))


# ovom rutom želimo prikazati obrazac
# ukoliko dobivamo ID filma, tada će se film pronaći te obrazac popuniti s podacima istog
# ukoliko je ID jednak nuli, tada to znači da unosimo novi zapis
@app.route('/film/<int:film_id>', methods=['GET', 'POST'])
def film(film_id):
    # POST metoda - ažuriramo podatke obrasca
    # vrijedi uzeti u obzir da će se poziv metodom POST ostvariti samo kod poziva iz obrasca (submit)
    if request.method == 'POST':
        # tada treba obraditi podatke iz obrasca
        if film_id == 0:
            # ako nemamo identifikator filma, znači da radimo unos novog filma
            db.session.add(
                Jobs(
                    naziv=request.form['naziv'],
                    kategorija=request.form['kategorija'],
                    ocjena=request.form['ocjena']
                )
            )
        # else:
        # imamo identifikator filma kojeg mijenjamo, pa ga prvo pronađemo
        # film=db.session.query(Film).filter_by(id=film_id).first()
        # ako mso ga našli
        # if film:
        #     # ažurirajmo njegova polja
        #     film.naziv=request.form['naziv']
        #     film.kategorija=request.form['kategorija']
        #     film.ocjena=request.form['ocjena']
        # zapisujemo sve podatke
        # napomena: nismo koristili try-exception blok radi utvrđivanja grešaka
        db.session.commit()
        # preusmjeravamo na stranicu za prikaz svih filmova
        return redirect(app.url_for('jobs'))
    else:
        # GET metoda poziva - prikazujemo obrazac
        # print(type(film_id),film_id)
        film = None
        # if film_id!=0:
        # ako ID od filma imamo, tada pronađemo film
        # film=db.session.query(Film).filter_by(id=film_id).first()
        # print(film.naziv)
        return render_template('mjesto.html', film=film)


# ruta koja služi samo da si popunimo podatke
@app.route('/popuni_bazu')
def popuni_bazu():
    # NAPOMENA: ako ti podaci postoje već u tabeli, desiti će se greška zbog duplog ključa
    # db.session.add(Film(naziv='Dune', kategorija='SCF', ocjena=9))
    # db.session.add(Film(naziv='Inspection', kategorija='Horor', ocjena=8.4))
    # db.session.add(Film(naziv='Umri muški', kategorija='Akcija', ocjena=8.1))
    db.session.commit()
    return redirect(app.url_for('jobs'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5003)
