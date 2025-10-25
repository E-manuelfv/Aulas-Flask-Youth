from flask import Flask
from routes.user import user_bp

app = Flask(__name__, template_folder='views/templates', static_folder='views/static')

@app.route('/')
def root():
    return "Hello, World!"

# REGISTER BLUEPRINT
app.register_blueprint(user_bp, url_prefix='/user')

if __name__ == '__main__':
    app.run(debug=True, port=5500)