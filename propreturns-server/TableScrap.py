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


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://bzkatlle:zoX3tih8KZ6lZWo6H55Q-9ur_1HCVFI-@rajje.db.elephantsql.com/bzkatlle'


db = SQLAlchemy(app)

migrate = Migrate(app, db)

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


with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return "Hello, this is the main page of your Flask application."

@app.route('/scrape')
def scrape_data():
    if PropReturns.query.first():
        return jsonify({"message": "Data already exists in the database"}), 200
    else:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

        print("Opening the website...")
        driver.get("https://pay2igr.igrmaharashtra.gov.in/eDisplay/propertydetails")
        print("Website opened successfully.")

        select_year = Select(driver.find_element(By.XPATH, '//*[@id="dbselect"]'))
        select_year.select_by_index('30')

        element1 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="district_id"]/option[26]'))
        )

        element1.click()

        element2 = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,'//*[@id="taluka_id"]/option[2]'))
            )

        element2.click()
        element3  =  WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,'//*[@id="village_id"]/option[59]'))
        )
        element3.click()

        driver.find_element(By.NAME, "free_text").send_keys("2023")

        print('Please enter the captcha within 15 seconds')

        time.sleep(15)

        submit  =  driver.find_element(By.ID, "submit")
        submit.click()

        element4  = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH,'//*[@id="tableparty_length"]/label/select/option[3]'))
        )
        element4.click()

        rows = driver.find_elements(By.XPATH,'//*[@id="tbdata"]')

        Anu_no = []
        Diarrhea_no = []
        diarrhea_type = []
        Du_Prohibit_Office = []
        Year = []
        Buyer_name = []
        Seller_name = []
        Other_information = []
        List_no_2 = []

        for row in rows:
            Anu_no.append(row.find_element(By.XPATH, './td[1]').text)
            Diarrhea_no.append(row.find_element(By.XPATH, './td[2]').text)
            diarrhea_type.append(row.find_element(By.XPATH, './td[3]').text)
            Du_Prohibit_Office.append(row.find_element(By.XPATH, './td[4]').text)
            Year.append(row.find_element(By.XPATH, './td[5]').text)
            Buyer_name.append(row.find_element(By.XPATH, './td[6]').text)
            Seller_name.append(row.find_element(By.XPATH, './td[7]').text)
            Other_information.append(row.find_element(By.XPATH, './td[8]').text)
            achor_tag = row.find_element(By.XPATH, './td[9]/a')
            List_no_2.append(achor_tag.get_attribute('href') if achor_tag else "")

        translator = Translator()

        translated_diarrhea_type = []
        translated_Du_Prohibit_Office = []
        translated_Buyer_name = []
        translated_Seller_name = []
        translated_Other_information = []

        for text in diarrhea_type:
            if text.strip():
                try:
                    translation = translator.translate(text, src='hi', dest='en')
                    translated_diarrhea_type.append(translation.text)
                except:
                    translated_diarrhea_type.append("")
            else:
                translated_diarrhea_type.append("")

        for text in Du_Prohibit_Office:
            if text.strip():
                try:
                    translation = translator.translate(text, src='hi', dest='en')
                    translated_Du_Prohibit_Office.append(translation.text)
                except:
                    translated_Du_Prohibit_Office.append("")
            else:
                translated_Du_Prohibit_Office.append("")

        for text in Buyer_name:
            if text.strip():
                try:
                    translation = translator.translate(text, src='hi', dest='en')
                    translated_Buyer_name.append(translation.text)
                except:
                    translated_Buyer_name.append("")
            else:
                translated_Buyer_name.append("")

        for text in Seller_name:
            if text.strip():
                try:
                    translation = translator.translate(text, src='hi', dest='en')
                    translated_Seller_name.append(translation.text)
                except:
                    translated_Seller_name.append("")
            else:
                translated_Seller_name.append("")

        for text in Other_information:
            if text.strip():
                try:
                    translation = translator.translate(text, src='hi', dest='en')
                    translated_Other_information.append(translation.text)
                except:
                    translated_Other_information.append("")
            else:
                translated_Other_information.append("")

        df  =  pd.DataFrame({'Anu no': Anu_no, 'Diarrhea no': Diarrhea_no, 'diarrhea type': translated_diarrhea_type, 'Du. Prohibit. Office': translated_Du_Prohibit_Office, 'Year': Year, 'Buyer name' : translated_Buyer_name, 'Seller name': translated_Seller_name, 'Other information': translated_Other_information, 'List no.2': List_no_2})
        df.to_csv('data.csv', index = False)
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
        
        success_message = {"message" : "Data scraped and stored in the database successfully"}
        return jsonify(success_message), 200
        
  
    

 


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
            return jsonify({"result" : result, "message" : "Data found successfully"})
        else:
            return jsonify({'message': 'No data found for Document No: {}'.format(document_no)}), 400    
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
            return jsonify({"result" : result, "message" : "Data found successfully"})
        else:
            return jsonify({'message': 'No data found for Year of Registration: {}'.format(year)}), 400
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
            return jsonify({"result" : result, "message" : "Data found successfully"})
        else:
            return jsonify({'message': 'No data found'}), 404 
    else:
        return jsonify({'message': 'parameter is missing'}), 400
if __name__ == "__main__":
    app.run(debug=True)
