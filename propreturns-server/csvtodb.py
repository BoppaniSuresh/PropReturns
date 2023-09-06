from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
import time
from googletrans import Translator
import pandas as pd
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify
from sqlalchemy import or_
from flask_migrate import Migrate
from sqlalchemy import extract
from sqlalchemy import func
from sqlalchemy import cast, Date
app = Flask(__name__)


# Configure the PostgreSQL database connection URL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bzkatlle:zoX3tih8KZ6lZWo6H55Q-9ur_1HCVFI-@rajje.db.elephantsql.com/bzkatlle'

# Initialize SQLAlchemy
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Define the model for the "propreturns" table
class PropReturns(db.Model):
    Anu_no = db.Column(db.TEXT, primary_key=True)
    Diarrhea_no = db.Column(db.TEXT)
    diarrhea_type = db.Column(db.TEXT)
    Du_Prohibit_Office = db.Column(db.TEXT)
    Year = db.Column(db.TEXT)
    Buyer_name = db.Column(db.TEXT)
    Seller_name = db.Column(db.TEXT)
    Other_information = db.Column(db.TEXT)
    List_no_2 = db.Column(db.TEXT)

class PreprocessedPropReturns(db.Model):
    Anu_no = db.Column(db.TEXT, primary_key=True)
    Diarrhea_no = db.Column(db.TEXT)
    diarrhea_type = db.Column(db.TEXT)
    Du_Prohibit_Office = db.Column(db.TEXT)
    Year = db.Column(db.TEXT)
    Buyer_name = db.Column(db.TEXT)
    Seller_name = db.Column(db.TEXT)
    Other_information = db.Column(db.TEXT)
    List_no_2 = db.Column(db.TEXT)

# Create the "propreturns" table (only needed once)
with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return "Hello, this is the main page of your Flask application."

@app.route('/todb', methods =['GET'])

def todb():
    df  = pd.read_csv('data.csv')
    
    for i, row in df.iterrows():
        prop_return = PropReturns(
            Anu_no=row['Anu no'],
            Diarrhea_no=row['Diarrhea no'],
            diarrhea_type=row['diarrhea type'],
            Du_Prohibit_Office=row['Du. Prohibit. Office'],
            Year=row['Year'],
            Buyer_name=row['Buyer name'],
            Seller_name=row['Seller name'],
            Other_information=row['Other information'],
            List_no_2=row['List no.2']
        )
        db.session.add(prop_return)
    df1 = df.copy()
    df1['Year'] = pd.to_datetime(df1['Year'], format= '%d/%m/%Y')
    df1['Diarrhea no'] = df1['Diarrhea no'].astype(int)
    df1['Anu_no'] = df1['Anu no'].astype(int)
    df1.dropna(inplace=True)
    
    for j, row in df1.iterrows():
        prop_return = PreprocessedPropReturns(
            Anu_no=row['Anu no'],
            Diarrhea_no=row['Diarrhea no'],
            diarrhea_type=row['diarrhea type'],
            Du_Prohibit_Office=row['Du. Prohibit. Office'],
            Year=row['Year'],
            Buyer_name=row['Buyer name'],
            Seller_name=row['Seller name'],
            Other_information=row['Other information'],
            List_no_2=row['List no.2']
        )
        db.session.add(prop_return)
        
    db.session.commit()
    
    return "Data stored and preprocessed in the database successfully."

   
@app.route('/get_by_document_no', methods=['GET'])

def get_by_document_no():
    document_no = request.args.get('document_no')
    
    if document_no:
        prop_returns  = PreprocessedPropReturns.query.filter_by(Diarrhea_no=document_no).all()
        if prop_returns:
            result= []
            for prop_return in prop_returns:
                result.append({
                    'Anu_no': prop_return.Anu_no,
                    'Diarrhea_no': prop_return.Diarrhea_no,
                    'diarrhea_type': prop_return.diarrhea_type,
                    'Du_Prohibit_Office': prop_return.Du_Prohibit_Office,
                    'Year': prop_return.Year,
                    'Buyer_name': prop_return.Buyer_name,
                    'Seller_name': prop_return.Seller_name,
                    'Other_information': prop_return.Other_information,
                    'List_no_2': prop_return.List_no_2
                })
            return jsonify(result)
        else:
            return jsonify({'message': 'No data found for Document No: {}'.format(document_no)}), 404     
    else:
        return jsonify({'message': 'Document No parameter is missing'}), 400
    

@app.route('/get_by_year', methods=['GET'])

def get_by_year():
    year = request.args.get('year')
  
    if year:
        try:
            year = int(year) 
        except ValueError:
            return jsonify({'message': 'Invalid year parameter'}), 400

        year_int = year

        prop_returns = PreprocessedPropReturns.query.filter(extract('year', cast(PreprocessedPropReturns.Year, Date)) == year_int).all()

        
        if prop_returns:
            result = []
            for prop_return in prop_returns:
                result.append({
                    'Anu_no': prop_return.Anu_no,
                    'Diarrhea_no': prop_return.Diarrhea_no,
                    'diarrhea_type': prop_return.diarrhea_type,
                    'Du_Prohibit_Office': prop_return.Du_Prohibit_Office,
                    'Year': prop_return.Year,
                    'Buyer_name': prop_return.Buyer_name,
                    'Seller_name': prop_return.Seller_name,
                    'Other_information': prop_return.Other_information,
                    'List_no_2': prop_return.List_no_2
                })
            return jsonify(result)
        else:
            return jsonify({'message': 'No data found for Year of Registration: {}'.format(year)}), 404 
    else:
        return jsonify({'message': 'Year parameter is missing'}), 400
                

@app.route('/search', methods = ['GET'])


def search():
    word = request.args.get('word')
    
    if word:
        prop_returns = PreprocessedPropReturns.query.filter(
            or_(
                PreprocessedPropReturns.Buyer_name.ilike(f'%{word}%'),  
                PreprocessedPropReturns.Seller_name.ilike(f'%{word}%'),  
                PreprocessedPropReturns.Other_information.ilike(f'%{word}%')  
            )
        ).all()
        # print(prop_returns)
        if prop_returns:
            
            result = []
            for prop_return in prop_returns:
                result.append({
                    'Buyer_name': prop_return.Buyer_name,
                    'Seller_name': prop_return.Seller_name,
                    'Other_information': prop_return.Other_information,
                })
            return jsonify(result)
        else:
            return jsonify({'message': 'No data found'}), 404 
    else:
        return jsonify({'message': 'parameter is missing'}), 400
    
if __name__ == "__main__":
    app.run(debug=True)

