from flask import Flask, request, render_template, redirect, url_for
import pandas as pd
import io
import base64

app = Flask(__name__)

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
        file_content = file.read()  # Read file content into memory
        encoded_content = base64.b64encode(file_content).decode('utf-8')  # Encode file content to base64
        return redirect(url_for('calculate_average', file_content=encoded_content))
    return redirect(request.url)

@app.route('/calculate')
def calculate_average():
    encoded_content = request.args.get('file_content')
    if not encoded_content:
        return redirect(url_for('index'))

    # Decode the base64 string to bytes
    file_content = base64.b64decode(encoded_content)
    file_stream = io.BytesIO(file_content)
    df = pd.read_excel(file_stream)

    kreditek = list(df["Kr."])
    jegyek = list(df["Jegyek"])

    for elem in jegyek:
        print(str(elem))

    def utsozarpojel(szo):
        index = -1
        for i in range(len(szo)):
            if szo[i] == "(":
                index = i
        return index

    szorzat = 0
    hagyomanyos, oszto  = 0, 0
    osszkredit = sum(kreditek)
    teljesitettkredit = 0
    for i in range(len(kreditek)):
        if kreditek[i] != 0 and str(jegyek[i]) != "nan" and int(jegyek[i][utsozarpojel(jegyek[i]) + 1]) != 1:
            szorzat += kreditek[i] * int(jegyek[i][utsozarpojel(jegyek[i]) + 1])
            hagyomanyos += int(jegyek[i][utsozarpojel(jegyek[i]) + 1])
            oszto += 1
            teljesitettkredit += kreditek[i]

    average = szorzat / 30 * (teljesitettkredit / osszkredit)
    sulyozottatlag = szorzat / osszkredit
    return render_template('result.html', kki=average, traditional_average=hagyomanyos/oszto, teljesitettkredit=teljesitettkredit, osszkredit=osszkredit, sulyozottatlag=sulyozottatlag)

if __name__ == '__main__':
    app.run(debug=True)
