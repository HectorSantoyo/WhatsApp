from flask import Flask,request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
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

#Crear la tabla si no existe
with app.app_context():
    db.create_all()

#funcion para ordenar los registros por fecha y hora
def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora,reverse=True)

@app.route('/')
def index():
    #obtener registros de DB
    registros = Log.query.all()
    registros_ordenados = ordenar_por_fecha_y_hora(registros)
    return render_template('index.html',registros=registros_ordenados)

mensajes_log = []

#funcion para agregar msjs y agregar en la DB
def agregar_mensajes_log(texto):
    mensajes_log.append(texto)

    #guardar mensaje en DB
    nuevo_registro = Log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()

#Token de verificacion para la  configuracion
TOKEN_WACODE = "WACODE"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        challenge = verificar_token(request)
        return challenge
    elif request.method == 'POST':
        response = recibir_mensajes(request)
        return response

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')

    if challenge and token == TOKEN_WACODE:
        return challenge
    else:
        return jsonify({'error':'Token invalido'}),401
    
def recibir_mensajes(req):
    try:
        req = request.get_json()
        entry = req['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensaje = value['messages']

        if objeto_mensaje:
            messages = objeto_mensaje[0]

            if "type" in messages:
                tipo = messages['type']

                if tipo == "interactive":
                    return 0
                
                if "text" in messages:
                    text = messages["text"]["body"]
                    numero = messages["from"]
                    agregar_mensajes_log(json.dumps(text))
                    agregar_mensajes_log(json.dumps(numero))
                    


        

        return jsonify({'message':'EVENT_RECEIVED'})
    except Exception as e:
        return jsonify({'message':'EVENT_RECEIVED'})

    
def enviar_mensaje_whatsapp(texto, numero):
    texto = texto.lower()

    if "hola" in texto:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": "523333947431",
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "Hola, bienvenido"
            }
        }
    
    else:
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": "523333947431",
            "type": "text",
            "text": {
                "preview_url": False,
                "body": "siono?"
            }
        }

    #convertir el diccionario a formato JSON
    data = json.dumps(data)

    headers = {
        "Content-Type" : "application/json",
        "Authorization" : "Bearer EAA0zs0xA8QYBO9q2xpvjQXhnObUZBvRs0zcxSbnLF16MW8p1BarEo6QloLqZA0aCMq6UT4E7rHmru6Llg9yhzbcS1sl2nKb68H5YuKZBZCdvrQ3ptc4aPyZAgpJC2gykg4yZADVFAYTZAkkdcXeFhDaQOV5PXTYgZAQ1kmZBtx73Tv9vvKM2f44WWGSrQ3bvggJBLbTQSLVEFqYIq3vzGcZASvX2UaGetHAh7r"
    }

    connection = http.client.HTTPSConnection("graph.facebook.com")

    try:
        connection.request("POST", "/v19.0/305695472626016/messages", data, headers)
        response = connection.getresponse()
        print(response.status, response.reason)

    except Exception as e:
        agregar_mensajes_log(json.dumps(e))

    finally:
        connection.close()

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port=80, debug=True)