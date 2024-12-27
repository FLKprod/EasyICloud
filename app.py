from flask import Flask, render_template, request, jsonify
import os
import zipfile

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/manual')
def manuel():
    return render_template('manual.html')

@app.route('/plan')
def plan():
    return render_template('plan.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/merge', methods=['POST'])
def merge():
    # Récupération des paramètres du formulaire
    folder_name = request.form.get('folder_name', 'EasyICloud').strip()  # Nom du dossier principal
    include_zip_files = request.form.get('include_zip_files') == 'true'  # Option pour inclure les fichiers ZIP

    # Dossier de base pour la sortie
    base_output_folder = os.path.join(os.path.expanduser("~"), "Downloads")
    output_folder = os.path.join(base_output_folder, folder_name)

    os.makedirs(output_folder, exist_ok=True)

    files = request.files.getlist('files')
    if not files:
        return jsonify({'status': 'error', 'message': 'Aucun fichier sélectionné.'})

    try:
        # Étape 1 : Extraction des fichiers ZIP
        for file in files:
            if file and file.filename.endswith('.zip'):
                temp_zip_path = os.path.join(output_folder, file.filename)
                file.save(temp_zip_path)

                with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(output_folder)

                if not include_zip_files:
                    os.remove(temp_zip_path)

        # Étape 2 : Renommage uniforme des dossiers spécifiques
        target_folder_name = "Photos iCloud"
        for root, dirs, _ in os.walk(output_folder, topdown=False):
            for directory in dirs:
                if directory.lower() in ["icloud photos", "photos icloud"]:
                    source_path = os.path.join(root, directory)
                    target_path = os.path.join(root, target_folder_name)

                    if source_path != target_path:
                        # Si un dossier cible existe déjà, fusionner
                        if os.path.exists(target_path):
                            for item in os.listdir(source_path):
                                item_path = os.path.join(source_path, item)
                                dest_path = os.path.join(target_path, item)

                                if os.path.isdir(item_path):
                                    counter = 1
                                    while os.path.exists(dest_path):
                                        dest_path = os.path.join(target_path, f"{item} ({counter})")
                                        counter += 1
                                    os.rename(item_path, dest_path)
                                else:
                                    counter = 1
                                    while os.path.exists(dest_path):
                                        dest_path = os.path.join(target_path, f"{os.path.splitext(item)[0]} ({counter}){os.path.splitext(item)[1]}")
                                        counter += 1
                                    os.rename(item_path, dest_path)

                            os.rmdir(source_path)
                        else:
                            os.rename(source_path, target_path)

        # Étape 3 : Fusion des dossiers dupliqués
        folder_mapping = {}
        for root, dirs, _ in os.walk(output_folder, topdown=True):
            for directory in dirs:
                normalized_name = directory.lower()
                source_path = os.path.join(root, directory)

                if normalized_name in folder_mapping:
                    # Fusionner avec le dossier existant
                    existing_path = folder_mapping[normalized_name]
                    for item in os.listdir(source_path):
                        item_path = os.path.join(source_path, item)
                        dest_path = os.path.join(existing_path, item)

                        if os.path.isdir(item_path):
                            counter = 1
                            while os.path.exists(dest_path):
                                dest_path = os.path.join(existing_path, f"{item} ({counter})")
                                counter += 1
                            os.rename(item_path, dest_path)
                        else:
                            counter = 1
                            while os.path.exists(dest_path):
                                dest_path = os.path.join(existing_path, f"{os.path.splitext(item)[0]} ({counter}){os.path.splitext(item)[1]}")
                                counter += 1
                            os.rename(item_path, dest_path)

                    # Supprimer le dossier source après fusion
                    os.rmdir(source_path)
                else:
                    # Ajouter au mapping
                    folder_mapping[normalized_name] = source_path

        return jsonify({'status': 'success', 'message': f'Tous les fichiers ZIP ont été extraits et fusionnés dans {output_folder}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Une erreur est survenue : {str(e)}'})


if __name__ == '__main__':
    app.run(debug=True)
