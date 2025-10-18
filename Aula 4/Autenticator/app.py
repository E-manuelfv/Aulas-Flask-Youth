from contextlib import redirect_stderr
from flask import Flask, render_template, request, redirect, url_for

class MyApp:
    def __init__(self):
        self.app = Flask(__name__, template_folder='views/templates')
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/login', 'login', self.login, methods=['GET', 'POST'])

    # Rota Slasher
    def index(self):
        return render_template('index.html')

    def login(self):
        if request.method == 'POST':
            # Lógica de autenticação simples
            email = request.form['email']
            password = request.form['password']
            if not email or not password:
                return render_template('login.html', error = 'Por favor, preencha todos os campos.')

            return redirect(url_for('index'))

        return render_template('login.html')
    
    def run(self):
        self.app.run(debug=True)

if __name__ == "__main__":
    my_app = MyApp()
    my_app.run()
    