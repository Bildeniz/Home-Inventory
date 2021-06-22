from flask_restful import Resource, abort
from flask import request
import MySQLdb
from MySQLdb.cursors import DictCursor
import datetime

def database():
    return MySQLdb.connect(host='127.0.0.1', user='root', passwd="", db='homeinventory', cursorclass=DictCursor, charset='utf8', use_unicode=True)

class registerProperty():
    def __init__(self, data):
        try:
            self.name = str(data.form['name'])
            self.mark = str(data.form['mark'])
            self.description = str(data.form['description'])
            self.is_added = bool(data.form['is_added'])
            self.buy_date = [int(item) for item in list(data.form.getlist('buy_date'))]
            if self.buy_date[1] <= 12 and self.buy_date[2] <= 31:
                self.buy_date = datetime.datetime(self.buy_date[0], self.buy_date[1], self.buy_date[2])
            else:
                abort(400, message='Lütfen girdiğiniz tarih değerlerini kontrol edin...')
        except TypeError:
            abort(400, message='Lütfen girdiğiniz değerleri kontrol edip tekrar deneyin...')
    def dict(self):
        return {'name': self.name, 'mark': self.mark, 'description': self.description, 'is_added': self.is_added, 'buy_date': str(self.buy_date)}            

class viewInventoryID(Resource):
    def get(self, id):
        db = database()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM property WHERE _id=%s', (id,))
        data = cursor.fetchone()
        cursor.close()
        db.close()
        if data is None:
            abort(404, message="Hatalı ID girişi...")
        data['buy_date'] = str(data['buy_date'])
        return data
        

class viewInvetory(Resource):
    def get(self):
        db = database()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM property')
        data = list(cursor.fetchall())
        cursor.close()
        db.close()
        return data

class addProperty(Resource):
    def post(self):
        data = registerProperty(request)
        db = database()
        cursor = db.cursor()
        cursor.execute("INSERT INTO property (name, mark, description, is_added, buy_date) values (%s,%s,%s,%s,%s)", (
            data.name,
            data.mark,
            data.description,
            data.is_added,
            data.buy_date
        ))
        db.commit()
        cursor.execute('SELECT _id FROM property WHERE name=%s and mark=%s and description=%s and buy_date=%s', (
            data.name,
            data.mark,
            data.description,
            data.buy_date
        ))        
        registeredData = cursor.fetchone()
        cursor.close()
        db.close()
        print(registeredData)
        return {'_id': registeredData['_id'],'name': data.name, 'mark': data.mark, 'description': data.description, 'is_added': data.is_added, 'buy_date': str(data.buy_date)}
        

class manageInventory(Resource):
    def delete(self, id):
        db = database()
        cursor = db.cursor()
        cursor.execute('SELECT _id FROM property WHERE _id=%s', (id,))
        if cursor.fetchone() is None:
            cursor.close()
            db.close()
            abort(400, message='Hatalı id girişi sağlandı...')
        else:
            cursor.execute('DELETE FROM property WHERE _id=%s', (id,))
            db.commit()
            cursor.execute('SELECT * FROM property WHERE _id=%s', (id,))
            if cursor.fetchone() is None:
                cursor.close()
                db.close()
                return 'Başarıyla silindi...'
            else:
                cursor.close()
                db.close()
                return 'Girdiğiniz değerleri kontrol edip tekrar deneyin...'

    def put(self, id):
        data = registerProperty(request)
        db = database()
        cursor = db.cursor()
        cursor.execute('SELECT _id FROM property WHERE _id=%s', (id,))
        if cursor.fetchone() is None:
            abort(400, message='Hatalı id girişi sağlandı...')
        cursor.execute('UPDATE property SET name=%s, mark=%s, description=%s, is_added=%s, buy_date=%s WHERE _id=%s',(
            data.name,
            data.mark,
            data.description,
            data.is_added,
            data.buy_date,
            id
        ))
        cursor.execute('SELECT * FROM property WHERE _id=%s', (id,))
        updatedData = cursor.fetchone()
        db.commit()
        db.close()
        updatedData['buy_date'] = str(updatedData['buy_date'])
        return updatedData
