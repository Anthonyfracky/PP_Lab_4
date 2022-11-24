from marshmallow import Schema, fields, ValidationError
from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
import src.models as models
import src.db as db
from src import app
from flask_jwt_extended import (
    JWTManager, jwt_required, get_jwt_identity
)

jwt = JWTManager(app)

wallet_bp = Blueprint('wallet', __name__, url_prefix='/wallet')
bcrypt = Bcrypt()


@wallet_bp.route('/', methods=['POST'])
@jwt_required()
def create_wallet():
    class Wallet(Schema):
        balance = fields.Int(required=True)

    try:
        wallet = Wallet().load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400

    user = db.session.query(models.User).filter(models.User.id == get_jwt_identity()).first()
    if user is None:
        return jsonify({'message': 'User not found'}), 500

    new_wallet = models.Wallet(balance=wallet['balance'], user_id=get_jwt_identity())

    db.session.add(new_wallet)
    db.session.commit()
    return 'Success', 200


@wallet_bp.route('/<int:wallet_id>', methods=['GET'])
@jwt_required()
def get_wallet(wallet_id):
    wallet = db.session.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    if wallet is None:
        return jsonify({'message': 'Wallet not found'}), 404
    else:
        if get_jwt_identity() is None:
            return jsonify({'message': 'Unauthorized'}), 401
    res = {'id': wallet.id, 'balance': wallet.balance, "user_id": get_jwt_identity()}
    return jsonify(res), 200


@wallet_bp.route('/<int:wallet_id>', methods=['PUT'])
@jwt_required()
def update_wallet(wallet_id):
    class Wallet(Schema):
        new_balance = fields.Int(required=True)

    try:
        wallet = Wallet().load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400
    wallet_to_update = db.session.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    if wallet_to_update is None:
        return jsonify({'message': 'Wallet not found'}), 404

    if get_jwt_identity() is None:
        return jsonify({'message': 'Unauthorized'}), 401

    if wallet.__contains__('new_balance'):
        wallet_to_update.balance = wallet['new_balance']

    db.session.commit()
    return get_wallet(wallet_id)[0], 200


@wallet_bp.route('/<int:wallet_id>', methods=['DELETE'])
@jwt_required()
def delete_wallet(wallet_id):
    wallet = db.session.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    transactions = db.session.query(models.Transaction).filter(models.Transaction.wallet_id_1 == wallet_id).all()
    if wallet is None:
        return jsonify({'message': 'Wallet not found'}), 404
    if get_jwt_identity() != wallet.user_id:
        return jsonify({'message': 'Forbidden'}), 403
    else:
        if transactions is not None:
            for el in transactions:
                if el is None:
                    break
                db.session.delete(el)
        db.session.delete(wallet)
    db.session.commit()
    return jsonify({'message': 'Wallet deleted'}), 200
