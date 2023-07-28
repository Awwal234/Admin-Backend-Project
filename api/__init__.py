from flask import Flask, request
from flask_mail import Mail, Message
from flask_restx import Api, Namespace, Resource, fields
from flask_jwt_extended import JWTManager
from http import HTTPStatus
from .utils import db
import os
from dotenv import load_dotenv
from .auth.authAdmin import authAdmin_namespace
load_dotenv()

sk = os.getenv('SECRET_KEY')


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = sk
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///userstorage.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_ID')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True

    db.init_app(app)
    with app.app_context():
        db.create_all()

    mail = Mail(app)
    JWTManager(app)

    # making namespace section#
    request_namespace = Namespace(
        'request', description="User request for login")
    request_model = request_namespace.model('RequestModel', {
        'name': fields.String(required=True, description="user fullname"),
        'email': fields.String(required=True, description="user email")
    })

    @request_namespace.route('/request')
    class MakeRequest(Resource):
        @request_namespace.expect(request_model)
        def post(self):
            '''
                Making Request for Signup
            '''
            data = request.get_json()
            name = data["name"]
            email = data["email"]
            my_mail = os.getenv('MAIL_ID')

            msg = Message('Request From a new User',
                          sender=email, recipients=[my_mail])
            msg.body = 'Name: {} /n Email: {}'.format(name, email)
            mail.send(msg)

            response = {
                'message': 'Sent successfully'
            }
            return response, HTTPStatus.OK

    # end making namespace section#
    authorizations = {"bearerAuth": {"type": "apiKey",
                                     "in": "header", "name": "X-API-KEY"}}

    api = Api(app, title='Admin Backend', version='0.1',
              authorizations=authorizations, security="apiKey")

    api.add_namespace(authAdmin_namespace, path='/api/auth_admin')
    api.add_namespace(request_namespace, path='/api/user')

    return app
