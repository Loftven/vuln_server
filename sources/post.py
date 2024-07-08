from flask_smorest import Blueprint
from db import db
from models.post import PostModel
from schemas import PostSchema
from flask.views import MethodView
from flask import render_template, jsonify
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt
from sources.user import AuthorModel


blp = Blueprint('posts', __name__, description='Operations with items')


@blp.route('/')
class Home(MethodView):
    def get(self):
        posts = PostModel.query.all()
        return render_template("home.html", posts=posts)


@blp.route('/create')
class CreatePost(MethodView):

    @jwt_required()
    @blp.arguments(PostSchema)
    @blp.response(200, PostSchema)
    def post(self, post_data):
        try:
            token = get_jwt()
            user = AuthorModel.query.filter(AuthorModel.username == token['sub']).first()
            post_model = PostModel(author_id=user.id, **post_data) # you need create another object!!
            db.session.add(post_model)
            db.session.commit()
            return {"success": "message"}, 201
        except SQLAlchemyError as e:
            print(e)

    def get(self):
        return render_template('create.html')


# @blp.route('/post/<int:post_id>')
# class GetPost(MethodView):
#     @jwt_required()
#     def get(self, post_id):
#         post_model = PostModel.query.get_or_404(post_id)
#         return render_template("post.txt", posts=post_model)


@blp.route('/post/change/<int:post_id>')
class ChangePost(MethodView):
    @jwt_required()
    def delete(self, post_id):
        try:
            post_model = PostModel.query.get_or_404(post_id)
            jwt_token = get_jwt()
            if jwt_token["sub"] != post_model.author.username:
                return (
                    jsonify(
                        {"Message": "It isn't your post", "Error": "Access is denied"}
                    ),
                    401,
                )
            db.session.delete(post_model)
            db.session.commit()
            return {"Message:": "success"}, 201
        except SQLAlchemyError as e:
            return {"error: {}".format(e): "message"}, 400

    @jwt_required()
    @blp.arguments(PostSchema)
    def post(self, user_data, post_id):
        try:
            post_model = PostModel.query.get_or_404(post_id)
            jwt_token = get_jwt()
            if jwt_token["sub"] != post_model.author.username:
                return (
                    jsonify(
                        {"Message": "It isn't your post", "Error": "Access is denied"}
                    ),
                    401,
                )

            post_model.title = user_data["title"]
            post_model.content = user_data["content"]
            db.session.add(post_model)
            db.session.commit()
            return {"Message:": "success"}, 201

        except SQLAlchemyError as e:
            return {"error: {}".format(e): "message"}, 400

    @jwt_required()
    def get(self, post_id):
        post = PostModel.query.get_or_404(post_id)
        return render_template('change.html', post=post)
