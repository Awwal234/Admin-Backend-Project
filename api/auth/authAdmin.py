from flask_restx import Namespace, Resource, fields
from flask import request
from ..models.userschema import UserModel
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash, generate_password_hash
from http import HTTPStatus
import os
from dotenv import load_dotenv
load_dotenv()

authAdmin_namespace = Namespace('authAdmin', description="auth for admin")
adminLoginModel = authAdmin_namespace.model('AdminLogin', {
    'email': fields.String(required=True, description="admin email"),
    'password': fields.String(required=True, description="admin password")
})

userCreationModel = authAdmin_namespace.model('UserCreationScheme', {
    'id': fields.Integer(description="user id"),
    'name': fields.String(required=True, description='user name'),
    'email': fields.String(required=True, description='user email'),
    'password': fields.String(required=True, description='user password')
})

userLogin = authAdmin_namespace.model('UserLoginScheme', {
    'email': fields.String(required=True, description='user email'),
    'password': fields.String(required=True, description='user password')
})

# Login for admin dashboard


@authAdmin_namespace.route('/login_admin')
class LoginAdmin(Resource):
    @authAdmin_namespace.expect(adminLoginModel)
    def post(self):
        '''
            Login for Admin
        '''

        data = request.get_json()
        email = data['email']
        password = data['password']

        secure_email = os.getenv('ADMIN_EMAIL')
        secure_password = os.getenv('ADMIN_PASSWORD')

        if (email == secure_email) and (password == secure_password):
            response = {
                'message': 'Successfully logged in'
            }

            return response, HTTPStatus.OK
        else:
            response = {
                'error_message': 'You are unauthorized'
            }
            return response, HTTPStatus.UNAUTHORIZED

# create password for new requested users(Admin)


@authAdmin_namespace.route('/create_user')
class createUser(Resource):
    @authAdmin_namespace.expect(userCreationModel)
    @authAdmin_namespace.marshal_with(userCreationModel)
    def post(self):
        '''
            Creation of Users
        '''

        data = request.get_json()
        name = data['name']
        email = data['email']
        password = data['password']

        user_exists_name = UserModel.query.filter_by(name=name).first()
        user_exists_email = UserModel.query.filter_by(email=email).first()
        user_exists_password = UserModel.query.filter_by(
            password=password).first()

        if user_exists_name and user_exists_email and user_exists_password:
            response = {
                'error-message': 'User already exists'
            }

            return response, HTTPStatus.UNAUTHORIZED
        else:
            password_hash = generate_password_hash(password)
            user_to_save = UserModel(
                name=name, email=email, password=password_hash)
            user_to_save.save()

            return user_to_save, HTTPStatus.CREATED

# login system for the users


@authAdmin_namespace.route('/login_user')
class LoginUser(Resource):
    @authAdmin_namespace.expect(userLogin)
    def post(self):
        '''
            Login User
        '''
        data = request.get_json()
        email = data['email']
        password = data['password']

        user_exists = UserModel.query.filter_by(email=email).first()

        if (user_exists) and check_password_hash(user_exists.password, password):
            access_token = create_access_token(identity=email)
            refresh_token = create_refresh_token(identity=email)

            response = {
                'access_token': access_token,
                'refresh_token': refresh_token
            }

            return response, HTTPStatus.CREATED
        else:
            response = {
                'message': 'You are unauthorized'
            }
            
            return response, HTTPStatus.UNAUTHORIZED
            
# refresh user token
@authAdmin_namespace.route('/refresh_token')
class RefreshToken(Resource):
    @jwt_required(refresh=True)
    def post(self):
        '''
                refresh user token
        '''
        
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        refresh_token = create_refresh_token(identity=current_user)
        
        response = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

        return response, HTTPStatus.CREATED
        
        
        
        
        
        
