from flask import Flask, render_template, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import os
import shutil
import time
from dhash import calc_dhash
from sqlalchemy import text

# istanza Flask
app = Flask(__name__)
# istanza del socket
socketio = SocketIO(app)
# collegamento al database mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root@localhost/test'
db = SQLAlchemy(app)

# collegamenti socket
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    query = text("SELECT COUNT(*) AS record_count FROM image_dhash")
    result = db.session.execute(query)
    record_count = result.fetchone()[0]
    socketio.emit('log', f'dhash presenti nel database {record_count}')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
 

#classe per inserimento degli hash nel database
class ImageDhash(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(16), unique=False, nullable=False)
    category = db.Column(db.String(50), unique=False, nullable=False)
    def __repr__(self):
        return f"<DHash(id={self.id}, hash='{self.hash}', category='{self.category}')>"



#route del web service
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ricerca')
def ricerca():
    return render_template('ricerca.html')

@app.route('/alimenta')
def alimenta():
    return render_template('alimenta.html')

@app.route('/folder', methods=['POST'])
def folder():
    folder_path = request.get_json()
    start_time = time.time()  # Registra il tempo di inizio
    for root, dirs, files in os.walk(folder_path['path']):
        for file in files:
            # Ottieni il percorso completo di ciascun file
            file_path = os.path.join(root, file)
            socketio.emit('log', f'Calcolo dhash del file {file_path}')
            dhash_img = calc_dhash(file_path)
            risultati = confronta_hash(dhash_img, 6)
            #print(f"{file} {dhash_img} {risultati}")
            if len(risultati) != 0:
                    shutil.copy(os.path.join(root, file), 'static/image_result')
                    # preparo una lista contenente il file analizzato e la categoria ottenuta
                    list_result = [f'image_result/{file}', risultati[0]]
                    # invio via socket la lista alla pagina ricerca.html
                    socketio.emit('result', list_result)        
    end_time = time.time()  # Registra il tempo di fine
    elapsed_time = end_time - start_time  # Calcola il tempo trascorso
    socketio.emit('time', f'Ricerca ottenuta in {elapsed_time} secondi')
    print("Tempo impiegato:", elapsed_time, "secondi")      
    return 'ok'
    
# funzione per il confronto degli hash
def confronta_hash(hash_confronto, soglia):
    # Query SQL per confrontare l'hash con quelli nel database utilizzando la distanza di hamming
    query = text("SELECT category FROM image_dhash WHERE BIT_COUNT(CONV(:YOUR_HASH, 16, 10) ^ CONV(hash, 16, 10)) < :threshold")
    result = db.session.execute(query, {'YOUR_HASH': hash_confronto, 'threshold': soglia})
    category_match = [row[0] for row in result]
    print(result)
    return category_match
    
# funzione per l'inserimento degli hash nel databse
@app.route('/alimentadb', methods=['POST'])
def alimentadb():
    dati_ricevuti = request.get_json()
    print(dati_ricevuti)
    path_folder = dati_ricevuti['path']
    category_image = dati_ricevuti['category']
    for root, dirs, files in os.walk(path_folder):
        for file in files:
            # Ottengo il percorso completo di ciascun file
            file_path = os.path.join(root, file)

            dhash_img = calc_dhash(file_path)
            print(bytes(dhash_img, 'utf-8'))
            dhash = ImageDhash(hash=bytes(dhash_img, 'utf-8'), category=category_image)
            db.session.add(dhash)
            db.session.commit()
            print('inserito')
               
    return 'ok'


#lancio del sistema
if __name__ == '__main__':
    socketio.run(app, debug=True)
