
from flask import Flask, render_template, request, jsonify, json
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
    __tablename__ = 'locations'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

class Industry(db.Model):
    __tablename__ = 'industries'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


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



locations_data = [
    {"id": 1, "name": "United States"},
    {"id": 2, "name": "Canada"},
    {"id": 3, "name": "United Kingdom"},
    {"id": 4, "name": "Germany"},
    {"id": 5, "name": "France"},
    {"id": 6, "name": "Australia"},
    {"id": 7, "name": "Brazil"},
    {"id": 8, "name": "Japan"},
    {"id": 9, "name": "India"},
    {"id": 10, "name": "China"}
]


@app.route('/locations')
def locations():
    return render_template('locations.html', locations_data=locations_data)

# Route for importing locations from API
@app.route('/import-locations', methods=['POST'])
def import_locations():
    # Logic for importing locations from API
    return jsonify({'message': 'Locations imported successfully'})

# Route for adding a new location
@app.route('/add-location', methods=['POST'])
def add_location():
    new_location = request.form.get('new_location')
    locations_data.append({"id": len(locations_data) + 1, "name": new_location})
    return jsonify({'message': 'Location added successfully'})

# Route for updating a location
@app.route('/update-location/<int:id>', methods=['PUT'])
def update_location(id):
    updated_location = request.form.get('updated_location')
    for location in locations_data:
        if location['id'] == id:
            location['name'] = updated_location
            return jsonify({'message': 'Location updated successfully'})
    return jsonify({'error': 'Location not found'}), 404

# Route for deleting a location
@app.route('/delete-location/<int:id>', methods=['DELETE'])
def delete_location(id):
    for location in locations_data:
        if location['id'] == id:
            locations_data.remove(location)
            return jsonify({'message': 'Location deleted successfully'})
    return jsonify({'error': 'Location not found'}), 404

industries_data = [
    {"id": 1, "name": "Information Technology"},
    {"id": 2, "name": "Finance"},
    {"id": 3, "name": "Healthcare"},
    {"id": 4, "name": "Education"},
    {"id": 5, "name": "Marketing"},
    {"id": 6, "name": "Retail"},
    {"id": 7, "name": "Manufacturing"},
    {"id": 8, "name": "Hospitality"},
    {"id": 9, "name": "Real Estate"},
    {"id": 10, "name": "Transportation"}
]

@app.route('/industries')
def industries():
    return render_template('industries.html', industries_data=industries_data)

# Route for importing industries from API
@app.route('/import-industries', methods=['POST'])
def import_industries():
    # Logic for importing industries from API
    return jsonify({'message': 'Industries imported successfully'})

# Route for adding a new industry
@app.route('/add-industry', methods=['POST'])
def add_industry():
    new_industry = request.form.get('new_industry')
    industries_data.append({"id": len(industries_data) + 1, "name": new_industry})
    return jsonify({'message': 'Industry added successfully'})

# Route for updating an industry
@app.route('/update-industry/<int:id>', methods=['PUT'])
def update_industry(id):
    updated_industry = request.form.get('updated_industry')
    for industry in industries_data:
        if industry['id'] == id:
            industry['name'] = updated_industry
            return jsonify({'message': 'Industry updated successfully'})
    return jsonify({'error': 'Industry not found'}), 404

# Route for deleting an industry
@app.route('/delete-industry/<int:id>', methods=['DELETE'])
def delete_industry(id):
    for industry in industries_data:
        if industry['id'] == id:
            industries_data.remove(industry)
            return jsonify({'message': 'Industry deleted successfully'})
    return jsonify({'error': 'Industry not found'}), 404



jobs_data = [
    {"title": "Machine Learning Engineer", "company": "Tech Innovations Ltd.", "type": "Full-time", "location": "Remote"},
    {"title": "UX/UI Designer", "company": "Creative Solutions Inc.", "type": "Contract", "location": "Remote"},
    {"title": "Backend Developer", "company": "Software Experts LLC", "type": "Part-time", "location": "Remote"},
    {"title": "Product Manager", "company": "Digital Ventures Co.", "type": "Full-time", "location": "Remote"},
    {"title": "Content Writer", "company": "Marketing Maven", "type": "Contract", "location": "Remote"},
    {"title": "Frontend Developer", "company": "Web Wizards Ltd.", "type": "Part-time", "location": "Remote"},
    {"title": "Business Analyst", "company": "Strategy Masters Inc.", "type": "Full-time", "location": "Remote"},
    {"title": "Graphic Designer", "company": "Visual Creations Co.", "type": "Contract", "location": "Remote"},
    {"title": "Network Engineer", "company": "Connectivity Solutions LLC", "type": "Part-time", "location": "Remote"}
]


@app.route('/get_api_data')
def get_api_data():
    return jsonify(jobs_data)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5003)
