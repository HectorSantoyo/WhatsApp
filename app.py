from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

app = Flask(__name__)

#Database configuration SQLITE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#Log model table
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_y_hora = db.Column(db.DateTime, default=datetime.utcnow)
    texto = db.Column(db.TEXT)

with app.app_context():
    db.create_all()

    prueba1 = Log(texto='Mensaje de prueba 1')
    prueba2 = Log(texto='Mensaje de prueba 2')

    db.session.add(prueba1)
    db.session.add(prueba2)
    db.session.commit()

#funcion para ordenar los registros por fecha y hora
def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora,reverse=True)

@app.route('/')
def index():
    #obtener registros de DB
    registros = Log.query.all()
    registros_ordenados = ordenar_por_fecha_y_hora(registros)
    return render_template('index.html', registros=registros_ordenados)

mensajes_log = []

#funcion para agregar msjs y agregar en la DB
def agregar_mensajes_log(texto):
    mensajes_log.append(texto)

    #guardar mensaje en DB
    nuevo_registro = Log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()


if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=80, debug=True)