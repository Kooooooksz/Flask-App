from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import os
import tempfile

app = Flask(__name__)

# Set UPLOAD_FOLDER to a temporary directory
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file and file.filename.endswith('.xlsx'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        return redirect(url_for('calculate_average', filename=file.filename))
    return redirect(request.url)

@app.route('/calculate/<filename>')
def calculate_average(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_excel(file_path)

    kreditek = list(df["Kr."])
    jegyek = list(df["Jegyek"])

    def utsozarpojel(szo):
        index = 0
        for i in range(len(szo)):
            if szo[i] == "(":
                index = i
        return index

    szorzat = 0
    hagyomanyos, oszto  = 0, 0
    osszkredit = sum(kreditek)
    teljesitettkredit = 0
    for i in range(len(kreditek)):
        if kreditek[i] != 0 and int(jegyek[i][utsozarpojel(jegyek[i]) + 1]) != 1:
            szorzat += kreditek[i] * int(jegyek[i][utsozarpojel(jegyek[i]) + 1])
            hagyomanyos += int(jegyek[i][utsozarpojel(jegyek[i]) + 1])
            oszto += 1
            teljesitettkredit += kreditek[i]

    average = szorzat / 30 * (teljesitettkredit / osszkredit)
    sulyozottatlag = szorzat / osszkredit
    return render_template('result.html', kki=average, traditional_average=hagyomanyos/oszto, teljesitettkredit=teljesitettkredit, osszkredit=osszkredit, sulyozottatlag=sulyozottatlag)

if __name__ == '__main__':
    app.run(debug=True)
