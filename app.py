
from flask import Flask, render_template, request, jsonify
# ORM sustav za rad s SQLite bazom
from flask_sqlalchemy import SQLAlchemy
import requests
from datetime import date, datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jobs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'fdghdftz5473#$'
db = SQLAlchemy(app)


# definicija klasa (modela) tabela
class Jobs(db.Model):
    __tablename__ = 'jobs'
    # definiranje polja tabele:
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sifra_posla = db.Column(db.String(50), nullable=False, unique=False)
    naslov_posla = db.Column(db.String(200), nullable=False)
    naziv_tvrtke = db.Column(db.String(200), nullable=False)
    url_posla = db.Column(db.String(50), nullable=False)
    industrija = db.Column(db.String(50), nullable=False)
    lokacija = db.Column(db.String(50), nullable=False)
    strucna_sprema = db.Column(db.String(50), nullable=False)
    opis_posla = db.Column(db.String(200), nullable=False)
    datum_objave = db.Column(db.Date, nullable=False)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

class Industry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)


# definiramo rute
@app.route('/')
def pocetna():
    return render_template('index.html')


# pozivanje stranice za prikaz popisa

@app.route('/jobs', methods=["GET", "POST"])
def jobs():
    apiJobs = []
    dbJobs = []
    callDb = request.form.get('callDb', None)
    callApi = request.form.get('callApi', None)
    if callDb is not None:
        dbJobs = db.session.query(Jobs).order_by(Jobs.id).all()

    if callApi is not None:
        urlJobs = 'https://jobicy.com/api/v2/remote-jobs'

        params = {
            "count": request.form.get('count'),
            "geo": request.form.get('location'),
            "industry": request.form.get('jobIndustry'),
            "tag": request.form.get('tag'),
        }

        print("params: ", params)
        response = requests.get(urlJobs, params=params)
        if response.status_code == 200:

            responseJson = response.json()
            if 'jobs' in responseJson:
                jobsApiResultJson = responseJson['jobs']

                for i in jobsApiResultJson:
                    apiJobs.append({'naslov_posla': i['jobTitle'], 'id': int(i['id']), 'naziv_tvrtke': i['companyName'][0], 'url_posla':i['url'], 'industrija': i['jobIndustry'], 'lokacija': i['jobGeo'][0],
                                 'strucna_sprema': i['jobLevel'], 'opis_posla': i['jobExcerpt'], 'datum_objave': i['pubDate']})

    return render_template('jobs.html', apiJobs=apiJobs, dbJobs=dbJobs)



@app.route('/locations')
def locations():
    return 'locations...'


# @app.route('/industries')
# def industries():
#     return 'industries...'


@app.route('/industries', methods=['GET'])
def industries():
    industries = Industry.query.all()
    return jsonify([{'id': ind.id, 'name': ind.name} for ind in industries])


# @app.route('/industries/import', methods=['POST'])
# def import_industries():
#     url_jobs = 'https://jobicy.com/api/v2/remote-jobs?count=10&tag=python'
#     response = requests.get(url_jobs)
#
#
#     jobs = response.json().get('jobs', [])
#     for job in jobs:
#         industry_name = job.get('jobIndustry')[0] if job.get('jobIndustry') else ''
#         if industry_name:
#             existing_industry = Industry.query.filter_by(name=industry_name).first()
#             if not existing_industry:
#                 new_industry = Industry(name=industry_name)
#                 db.session.add(new_industry)
#     db.session.commit()
#     return '', 204

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5003)
