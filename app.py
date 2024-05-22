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
    sifra_posla = db.Column(db.String(50), nullable=False, unique=False)
    naslov_posla = db.Column(db.String(50), nullable=False)
    naziv_tvrtke = db.Column(db.String(50), nullable=False)
    url_posla = db.Column(db.String(50), nullable=False)
    industrija = db.Column(db.String(50), nullable=False)
    lokacija = db.Column(db.String(50), nullable=False)
    strucna_sprema = db.Column(db.String(50), nullable=False)
    opis_posla = db.Column(db.String(50), nullable=False)
    datum_objave = db.Column(db.Date, nullable=False)


# class Location(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(80), nullable=False)


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
        #  jobs_api = requests.get(urlJobs.format()).json()
        apiResult = requests.get('https://jobicy.com/api/v2/remote-jobs?count=10&tag=python').json()
        jobs = apiResult['jobs']

        for i in jobs:
            i['naslov_posla'] = (i['jobTitle'],
                                Jobs(id=int(i["id"]), sifra_posla=i["jobSlug"],
                                naslov_posla=i['companyName'],
                                naziv_tvrtke=i['companyName'][0],
                                url_posla=i['url'],
                                industrija=i['jobIndustry'],
                                lokacija=i['jobGeo'],
                                strucna_sprema=i['jobLevel'],
                                opis_posla=i['jobExcerpt'],
                                datum_objave=i['pubDate']))


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


@app.route('/locations')
def locations():
    return 'locations...'


@app.route('/industries')
def industries():
    return 'industries...'

@app.route('/api')
def api():
    return 'api...'

# @app.route('/api/locations', methods=['GET'])
# def get_locations():
#     locations = Location.query.all()
#     return jsonify([{'id': loc.id, 'name': loc.name} for loc in locations])
#
# @app.route('/api/locations', methods=['POST'])
# def add_location():
#     data = request.json
#     if not data or not 'name' in data:
#         new_location = Location(name=data['name'])
#     db.session.add(new_location)
#     db.session.commit()
#     return jsonify({'id': new_location.id, 'name': new_location.name}), 201
#
# @app.route('/api/locations/<int:id>', methods=['PUT'])
# def update_location(id):
#     data = request.json
#     if not data or not 'name' in data:
#         location = Location.query.get(id)
#     if location is None:
#         location.name = data['name']
#     db.session.commit()
#     return jsonify({'id': location.id, 'name': location.name})
#
# @app.route('/api/locations/<int:id>', methods=['DELETE'])
# def delete_location(id):
#     location = Location.query.get(id)
#     if location is None:
#         db.session.delete(location)
#     db.session.commit()
#     return '', 204
#
# @app.route('/api/locations/import', methods=['POST'])
# def import_locations():
#     # Pretpostavljamo da Jobicy API vraća listu lokacija
#     jobicy_api_url = 'https://api.jobicy.com/locations'  # Zamenite sa stvarnim URL-om API-ja
#     response = requests.get(jobicy_api_url)
#
#     external_data = response.json()
#     for data in external_data:
#         existing_location = Location.query.filter_by(name=data['name']).first()
#         if not existing_location:
#             new_location = Location(name=data['name'])
#             db.session.add(new_location)
#     db.session.commit()
#     return '', 204
#

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
