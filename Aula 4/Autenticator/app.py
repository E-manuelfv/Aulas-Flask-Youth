from flask import Flask, render_template, request, redirect, url_for

class MyApp:
    def __init__(self):
        self.app = Flask(__name__, template_folder='views/templates', static_folder='views/static')
        self.app.add_url_rule('/login', 'login', self.login, methods=['GET', 'POST']) # Nesta aula paramos apenas com o LOGIN
        self.app.add_url_rule('/', 'index', self.index)

    def login(self):
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']

            if not email or not password:
                return render_template('login.html', title='Login Page', error='Email ou senha não podem estar vazios.')     
            return redirect(url_for('index'))
        return render_template('login.html', title='Login Page')

    def index(self):
        return render_template('index.html', title='Home Page')
    
    def run(self):
        self.app.run(debug=True)

if __name__ == '__main__':
    my_app = MyApp()
    my_app.run()