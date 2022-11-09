from marshmallow import Schema, fields, ValidationError
from enum import Enum
from flask import Blueprint, jsonify, request
import src.models as models
import src.db as db
from flask_bcrypt import Bcrypt

user_blueprint = Blueprint('user', __name__, url_prefix='/user')
bcrypt = Bcrypt()


@user_blueprint.route('/', methods=['POST'])
def create_user():
    class User(Schema):
        surname = fields.Str(required=True)
        name = fields.Str(required=True)
        username = fields.Str(required=True)
        password = fields.Str(required=True)

    try:
        if not request.json:
            raise ValidationError('No input data provided')
        User().load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    new_user_model = models.Users(surname=request.json['surname'], name=request.json['name'],
                                  username=request.json['username'],
                                  password=bcrypt.generate_password_hash(request.json['password']).decode('utf-8'))
    user_already_exists = db.session.query(models.Users).filter(
        models.Users.username == new_user_model.username).count() != 0

    if user_already_exists:
        return jsonify({'error': 'User already exists'}), 401

    try:
        db.session.add(new_user_model)
    except:
        db.session.rollback()
        return jsonify({"User data is not valid"}), 400

    new_user = db.session.query(models.Users).filter_by(username=request.json['username']).first()
    new_PersonalBudget_model = models.PersonalBudgets(id=new_user_model.id, money_amount=0)
    try:
        db.session.add(new_PersonalBudget_model)
    except:
        db.session.rollback()
        return jsonify({"Failed to create personal budget, database error"}), 405

    db.session.commit()

    res_json = {}

    res_json['id'] = new_user_model.id
    res_json['surname'] = new_user_model.surname
    res_json['name'] = new_user_model.name
    res_json['username'] = new_user_model.username
    res_json['personal_budget'] = new_user_model.id
    res_json['family_budgets'] = [int(row.family_budget_id) for row in
                                  db.session.query(models.FamilyBudgetsUsers).filter_by(
                                      user_id=new_user_model.id).all()]

    return jsonify(res_json), 200


@user_blueprint.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = db.session.query(models.Users).filter_by(id=user_id).first()
    if user is None:
        return jsonify({'error': 'User not found'}), 404

    res_json = {}

    res_json['id'] = user.id
    res_json['surname'] = user.surname
    res_json['name'] = user.name
    res_json['username'] = user.username
    res_json['personal_budget'] = user.id
    res_json['family_budgets'] = [int(row.family_budget_id) for row in
                                  db.session.query(models.FamilyBudgetsUsers).filter_by(user_id=user_id).all()]

    return jsonify(res_json), 200


@user_blueprint.route('/<int:user_id>', methods=['PATCH'])
def update_user(user_id):
    try:
        class User(Schema):
            surname = fields.Str(required=True)
            name = fields.Str(required=True)
            username = fields.Str(required=True)
            password = fields.Str(required=True)

        if not request.json:
            raise ValidationError('No input data provided')
        User().load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user = db.session.query(models.Users).filter(models.Users.id == user_id).first()
    if user is None:
        return jsonify({'error': 'User does not exist'}), 404

    try:
        if 'name' in request.json:
            user.name = request.json['name']
        if 'username' in request.json:
            user.username = request.json['username']
        if 'password' in request.json:
            user.password = bcrypt.generate_password_hash(request.json['password']).decode('utf-8')
        if 'surname' in request.json:
            user.suename = request.json['surname']
    except:
        db.session.rollback()
        return jsonify({'error': "User data is not valid"}), 400

    db.session.commit()

    return "", 200


@user_blueprint.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = db.session.query(models.Users).filter(models.Users.id == user_id).first()
    if user is None:
        return jsonify({'error': 'User does not exist'}), 404

    try:
        db.session.delete(user)
    except:
        db.session.rollback()
        return jsonify({'error': "User data is not valid"}), 400

    db.session.commit()

    return jsonify({'message': "User deleted successfully"}), 200