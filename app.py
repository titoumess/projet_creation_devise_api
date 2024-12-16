import csv
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from database import create_connection

app = Flask(__name__)

@app.route('/')
def index():
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT id_devise, nom_devise FROM devise')
    currencies = cursor.fetchall()
    conn.close()
    return render_template('index.html', currencies=currencies)

@app.route('/currency/<int:id_devise>')
def currency(id_devise):
    conn = create_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Récupération des taux de change
    cursor.execute('SELECT * FROM taux_change WHERE id_devise = %s', (id_devise,))
    rates = cursor.fetchall()
    print("Données brutes des taux : ", rates)
    
    # Récupération du nom de la devise
    cursor.execute('SELECT nom_devise FROM devise WHERE id_devise = %s', (id_devise,))
    nom_devise = cursor.fetchone()
    if nom_devise is None:
        print(f"Nom de la devise introuvable pour id_devise={id_devise}")
        return "Devise introuvable", 404
    
    nom_devise = nom_devise['nom_devise']

    # Nettoyer les données pour éviter les valeurs None ou incorrectes
    cleaned_rates = []
    for rate in rates:
        if rate['date'] is None or rate['taux_change'] is None:
            print(f"Donnée ignorée pour {rate}")  # Ajouter un log pour les données ignorées
            continue  # Ignore les entrées incorrectes
        cleaned_rates.append(rate)

    print("Données nettoyées pour le graphique : ", cleaned_rates)  # Voir les données après nettoyage

    conn.close()

    return render_template('currency.html', id_devise=id_devise, nom_devise=nom_devise, rates=cleaned_rates)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files['file']
        
        if file:
            file_path = 'uploads/' + file.filename
            file.save(file_path)
            
            # Étape 1 : Lire le fichier et extraire le nom de la devise
            with open(file_path, 'r') as f:
                reader = csv.reader(f)
                header = next(reader)  # Lire la première ligne (en-têtes)
                if len(header) < 2 or not header[1].endswith('_to_EUR'):
                    return "Fichier CSV invalide. Le nom de la devise est introuvable.", 400
                devise_name = header[1].split('_')[0]  # Extraire 'JPY' de 'JPY_to_EUR'

            # Étape 2 : Vérifier si la devise existe déjà ou l'ajouter
            conn = create_connection()
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("SELECT id_devise FROM devise WHERE nom_devise = %s", (devise_name,))
            result = cursor.fetchone()
            
            if result:
                id_devise = result['id_devise']
            else:
                cursor.execute("INSERT INTO devise (nom_devise) VALUES (%s)", (devise_name,))
                id_devise = cursor.lastrowid  # Récupérer l'ID de la devise nouvellement insérée
            
            conn.commit()

            # Étape 3 : Lire et insérer les taux de change
            with open(file_path, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        cursor.execute(
                            "INSERT INTO taux_change (id_devise, date, taux_change) VALUES (%s, %s, %s)",
                            (id_devise, row['DateTime'], row[header[1]])
                        )
                    except Exception as e:
                        print(f"Erreur d'insertion pour la ligne {row}: {e}")  # Debugging
            
            conn.commit()
            conn.close()
            
            return redirect(url_for('index'))
    
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)