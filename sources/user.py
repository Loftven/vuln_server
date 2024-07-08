from db import db
from flask_jwt_extended import jwt_required, create_access_token
from flask_jwt_extended import get_jwt, set_access_cookies, unset_access_cookies
import hashlib
from flask import render_template, render_template_string
from flask.views import MethodView
from models.user import AuthorModel
from models.jwt import BlocklistJwt
from models.post import PostModel
from flask_smorest import Blueprint, abort
from schemas import AuthorLoginSchema
from flask import jsonify
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError


blp = Blueprint("users", __name__, description='Operations with users')


@blp.route('/register')
class UserRegister(MethodView):
    @blp.arguments(AuthorLoginSchema)
    def post(self, user_data):

        if AuthorModel.query.filter(user_data["username"] == AuthorModel.username).first():
            abort(409, message="User already exists")
        user = AuthorModel(username=user_data["username"],
                           password=hashlib.sha256(user_data["password"].encode()).hexdigest())
        db.session.add(user)
        db.session.commit()
        return {"Message": "success"}, 201

    def get(self):
        return render_template('register.html')


@blp.route('/login')
class UserLogin(MethodView):
    @blp.arguments(AuthorLoginSchema)
    def post(self, user_data):
        author = AuthorModel.query.filter(AuthorModel.username == user_data["username"]).first()
        if not author or hashlib.sha256(user_data["password"].encode()).hexdigest() != author.password:
            abort(400, message="Username or password is invalid")

        if user_data["username"] == 'admin':
            access_token = create_access_token(identity=user_data["username"],
                                               additional_claims={"is_administrator": True}, fresh=True)
        else:
            access_token = create_access_token(identity=author.username, fresh=True)

        resp = jsonify({"message": "success login"})
        set_access_cookies(resp, access_token)
        return resp, 200

    def get(self):
        return render_template('login.html')


@blp.route('/profile')
class UserProfile(MethodView):
    @jwt_required()
    def get(self):
        token = get_jwt()
        author = AuthorModel.query.filter(AuthorModel.username == token['sub']).first()
        posts = PostModel.query.filter(PostModel.author_id == author.id)
        return render_template('profile.html', user=token['sub'], posts=posts)


@blp.route('/logout')
class UserLogout(MethodView):
    @jwt_required()
    def get(self):
        resp = jsonify({"message": "logout successful"})
        try:
            unset_access_cookies(resp)
            jti = get_jwt()["jti"]
            now = datetime.now()
            db.session.add(BlocklistJwt(jti=jti, created_at=now))
            db.session.commit()
            return resp
        except SQLAlchemyError as e:
            print(f"error: {e}")
            return resp


@blp.route('/invite_user/<string:username>')
class InviteUser(MethodView):

    @jwt_required()
    def get(self, username=None):
        token = get_jwt()
        if token['sub'] != "admin" and token["is_administrator"] is True:
            return (
                jsonify(
                    {"Message": "Sorry, only admin can make inviting page", "Error": "Unauthorized"}
                ),
                401,
            )
        template = """
        <!DOCTYPE html>
        <html lang="ru">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Приветствие пользователя</title>
            <!-- Подключение Bootstrap CSS -->
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
        </head>
        <body>
            <div class="container">
            <div class="row justify-content-center">
            <div class="col-md-6">
            <!-- Приветствие пользователя -->
            <h1>Добро пожаловать, """ + username + """!</h1>
    
                <!-- Приглашение зарегистрироваться -->
                <p class="lead mt-3">Присоединяйтесь к нашему форуму.</p>
    
                <!-- Кнопка для регистрации -->
                <a href="http://localhost:5000/register" class="btn btn-primary">Зарегистрироваться</a>
            </div>

            <!-- Подключение Bootstrap JS и зависимостей -->
            <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/popper.js@1.9.3/dist/umd/popper.min.js"></script>
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
            </body>
        </html>"""
        return render_template_string(template)


@blp.route('/.config')
class ForBack(MethodView):
    def get(self):
        text = []
        with open('rules.txt', 'r') as f:
            text = f.readlines()

        return (
            jsonify({"Message": text}),
            200,
        )
