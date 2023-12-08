# run.py

from ez.app import app

if __name__ == '__main__':
    app.config.from_object('config.Config')  # Use the general Config class
    app.run(debug=True)
