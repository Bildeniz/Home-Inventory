from flask import Flask, request, render_template, redirect, url_for, flash
from flask_mysqldb import MySQL
from flask_restful import Api, Resource
from wtforms import Form, StringField, BooleanField, TextAreaField, validators, ValidationError, SelectField
from wtforms.fields.html5 import DateField 
from func import secretKey
from api import addProperty, manageInventory, viewInventoryID, viewInvetory
import datetime
import requests

# Configration
app = Flask('Home Inventory')
app.secret_key = secretKey()

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'homeinventory'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

baseurl = 'http://127.0.0.1:5000'

db = MySQL(app)
api = Api(app)

api.add_resource(viewInventoryID, '/viewInventory/<int:id>')
api.add_resource(viewInvetory, '/viewInventory')
api.add_resource(addProperty, '/manageInventory')
api.add_resource(manageInventory, '/manageInventory/<int:id>')

class registerPropertyForm(Form):
    required = 'Lütfen bu alanı doldurun.'
    name = StringField('Eşya ismi', validators=[validators.DataRequired(message=required), validators.Length(min=3, max=50, message='Lütfen en az 3 en fazla 50 karakter olacak şekilde girin.')])
    mark = StringField('Eşya işareti', validators=[validators.DataRequired(message=required), validators.Length(min=3, max=100, message='Lütfen en az 3 en fazla 100 karakter olacak şekilde girin.')])
    description = TextAreaField('Eşya açıklaması', validators=[validators.DataRequired(message=required), validators.Length(min=3, max=500, message='Lütfen en az 3 en fazla 500 karakter olacak şekilde girin.')])
    is_added = BooleanField('Eklendi mi ?')
    buy_date = DateField('Alınma tarihi')

@app.route('/')
def index():
    cursor = db.connection.cursor()
    cursor.execute('SELECT * FROM property')
    data = cursor.fetchall()
    cursor.close()
    return render_template('index.html', datas=data)

@app.route('/addProperty', methods=['POST', 'GET'])
def addProperty():
    form = registerPropertyForm(request.form)
    if request.method == 'POST' and form.validate():
        buy_date = str(form.buy_date.data).split('-')
        response = requests.post(baseurl+'/manageInventory', {
            'name' : form.name.data,
            'mark' : form.mark.data,
            'description' : form.description.data,
            'is_added' : form.is_added.data,
            'buy_date' : buy_date
        })
        if response.status_code == 200:
            flash('Kaydınız başarıyla tamamlandı...', 'success')
            return redirect(url_for('index'))
        elif response.status_code == 400:
            flash('Hatalı giriş sağlandır...', 'danger')
            return redirect(url_for('index'))
        else:
            flash('Bir problem oluştu...', 'danger')
            return redirect(url_for('index'))

    else:
        return render_template('addProperty.html', form=form, Title="Eşya ekle")

@app.route('/updateProperty/<int:id>', methods=['POST', 'GET'])
def editProperty(id):
    form = registerPropertyForm(request.form)
    if request.method == 'POST' and form.validate():
        buy_date = str(form.buy_date.data).split('-')
        response = requests.put(baseurl+'/manageInventory/'+str(id), {
            'name' : form.name.data,
            'mark' : form.mark.data,
            'description' : form.description.data,
            'is_added' : form.is_added.data,
            'buy_date' : buy_date
        })
        if response.status_code == 200:
            flash('Başarıyla güncellendi...', 'success')
            return redirect(url_for('index'))
        elif response.status_code == 400:
            flash('Hatalı giriş sağlandır...', 'danger')
            return redirect(url_for('index'))
        else:
            flash('Bir problem oluştu...', 'danger')
            return redirect(url_for('index'))
    else:
        response = requests.get(baseurl+'/viewInventory/'+str(id))
        if response.status_code == 200:
            data = response.json()
            form.name.data = data['name']
            form.mark.data = data['mark']
            form.description.data = data['description']
            form.is_added.data = data['is_added']
            buy_date = [int(item) for item in data['buy_date'].split('-')]
            form.buy_date.data = datetime.datetime(buy_date[0], buy_date[1], buy_date[2])
            return render_template('addProperty.html', form=form, Title="Eşyayı güncelle")
        else:
            flash('Hatalı ID girişi...', 'danger')
            return redirect(url_for('index'))

@app.route('/deleteProperty/<int:id>')
def deleteProperty(id):
    response = requests.delete(baseurl+'/manageInventory/'+str(id))
    if response.status_code == 200:
        flash('Başarıyla silinmiştir', 'success')
        return redirect(url_for('index'))
    elif response.status_code == 400:
        flash('Hatalı giriş sağlandı...', 'danger')
        return redirect(url_for('index'))
    else:
        flash('Bir problem oluştu...', 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)