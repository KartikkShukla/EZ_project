import pytest
from ez.app.views import app, db
from ez.app.models import User, UploadedFile

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    client = app.test_client()

    with app.app_context():
        db.create_all()
        yield client
        db.drop_all()

def test_signup(client):
    response = client.post('/signup', data={'email': 'test@example.com', 'password': 'testpassword'})
    assert b'Check your email for verification' in response.data

def test_verify_email(client):
    user = User(email='test@example.com', password='testpassword', active=False)
    db.session.add(user)
    db.session.commit()

    response = client.get(f'/verify/{user.token}')
    assert b'Email verification successful' in response.data

def test_download_file(client):
    user = User(email='test@example.com', password='testpassword', active=True)
    db.session.add(user)
    db.session.commit()

    uploaded_file = UploadedFile(filename='test.docx', user=user)
    db.session.add(uploaded_file)
    db.session.commit()

    client.post('/login', data={'email': 'test@example.com', 'password': 'testpassword'})
    response = client.get(f'/download/{uploaded_file.id}')
    assert b'success' in response.data
