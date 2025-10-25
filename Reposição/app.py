from flask import Flask, render_template, url_for, request, redirect, session, flash

class MyApp:
    def __init__(self):
        self.app = Flask(__name__, template_folder="views/templates")
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/login', 'login', self.login, methods=['GET', 'POST'])
        self.app.add_url_rule('/register', 'register', self.register, methods=['GET', 'POST'])

        self.app.secret_key = "61faed047fea42a1dd40d2721135d1f5f5898d0ac1f67d73"

    def index(self):
        return render_template('index.html', title = "Página Inicial")

    def login(self):
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            # VALIDAÇÃO DOS CAMPOS
            if not email or not password:
                return render_template('login.html', error = "Por favor, preencha todos os campos!")

            # VALIDAÇÃO DE EMAIL FICTÍCIO
            if email == "admin@example.com" and password == "12345":

                # SUCESSO
                session['user_logged_in'] = True
                session['user_email'] = email

                flash('Login efetuado com sucesso!', 'success')

                return redirect(url_for('index'))
            else:
                return render_template('login.html', error = "Email ou senha incorretos.") 

        return render_template('login.html', title = "Página Login")
    
    def register(self):
        return "Register Page"
    
    def run(self):
        self.app.run(debug=True)

print(__name__)

if __name__ == '__main__':
    my_app = MyApp()
    my_app.run()