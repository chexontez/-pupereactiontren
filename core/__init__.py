"""
Инициализация Flask приложения и расширений.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Создание экземпляров расширений
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'main.login'
login_manager.login_message = 'Пожалуйста, войдите, чтобы получить доступ к этой странице.'


def create_app():
    """
    Фабричная функция для создания и настройки приложения Flask.
    """
    app = Flask(__name__, template_folder='../site/templates', static_folder='../site/static')
    app.config.from_object('config.Config')

    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)

    # Регистрация blueprint'ов
    from core.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from core.api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app