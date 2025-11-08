from flask import Flask, render_template, request, redirect, url_for, flash, session

class MyApp:
    def __init__(self):
        self.app = Flask(__name__, template_folder='views/templates', static_folder='views/static')
        
        # ADICIONE ESTA LINHA - SECRET KEY OBRIGATÓRIA
        self.app.secret_key = 'sua_chave_secreta_muito_segura_aqui_12345'
        
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/login', 'login', self.login, methods=['GET', 'POST'])
        self.app.add_url_rule('/register', 'register', self.register, methods=['GET', 'POST'])

    def index(self):
        return render_template('index.html')

    def login(self):
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            
            if not email or not password:
                return render_template('login.html', error='Por favor, preencha todos os campos.')
            
            # Aqui você pode adicionar a lógica de autenticação real
            # Por enquanto, vamos usar um exemplo simples
            if email == "admin@example.com" and password == "123456":
                session['user_logged_in'] = True
                session['user_email'] = email
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('index'))
            else:
                return render_template('login.html', error='Email ou senha incorretos.')
        
        return render_template('login.html')
    
    def register(self):
        if request.method == 'POST':
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if not all([name, email, password, confirm_password]):
                return render_template('register.html', error='Por favor, preencha todos os campos.')
            
            if password != confirm_password:
                return render_template('register.html', error='As senhas não coincidem.')
            
            if len(password) < 6:
                return render_template('register.html', error='A senha deve ter pelo menos 6 caracteres.')
            
            # Aqui você normalmente salvaria no banco de dados
            # Por enquanto, vamos apenas redirecionar
            flash('Cadastro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html')
    
    def run(self):
        self.app.run(debug=True)

if __name__ == "__main__":
    my_app = MyApp()
    my_app.run()