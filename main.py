from core import create_app

from dotenv import load_dotenv
load_dotenv()

app = create_app()

with app.app_context():
    from core import db
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)