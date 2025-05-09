from flask import Flask, render_template, request, redirect, url_for, send_file
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new', methods=['GET', 'POST'])
def new_file():
    if request.method == 'POST':
        filename = request.form['filename']
        if not filename.endswith('.csv'):
            filename += '.csv'
        df = pd.DataFrame(columns=['列1', '列2', '列3'])
        df.to_csv(os.path.join('uploads', filename), index=False)
        return redirect(url_for('edit', filename=filename))
    return render_template('new.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)
    if file:
        filename = file.filename
        file.save(os.path.join('uploads', filename))
        encodings = ['utf-8', 'gbk', 'gb2312', 'big5', 'utf-16']
        df = None
        for encoding in encodings:
            try:
                df = pd.read_csv(os.path.join('uploads', filename), encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        if df is None:
            return "无法识别文件编码，请尝试其他编码格式"
        # 统一转换为UTF-8保存
        df.to_csv(os.path.join('uploads', filename), encoding='utf-8', index=False)
        return redirect(url_for('edit', filename=filename))

@app.route('/edit/<filename>')
def edit(filename):
    df = pd.read_csv(os.path.join('uploads', filename))
    encodings = ['utf-8', 'gbk', 'gb2312', 'big5', 'utf-16']
    return render_template('edit.html', filename=filename, columns=df.columns, data=df.values.tolist(), encodings=encodings)

@app.route('/save', methods=['POST'])
def save_file():
    filename = request.form['filename']
    encoding = request.form['encoding']
    df = pd.DataFrame(request.form.getlist('data[]'))
    df.to_csv(os.path.join('downloads', filename), encoding=encoding, index=False)
    return send_file(os.path.join('downloads', filename), as_attachment=True)

if __name__ == '__main__':
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('downloads', exist_ok=True)
    app.run(debug=True)