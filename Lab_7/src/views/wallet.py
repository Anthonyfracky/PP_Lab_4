from marshmallow import Schema, fields, ValidationError
from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
import src.models as models
import src.db as db

wallet_bp = Blueprint('wallet', __name__, url_prefix='/wallet')
bcrypt = Bcrypt()


@wallet_bp.route('/', methods=['POST'])
def create_wallet():
    class Wallet(Schema):
        balance = fields.Int(required=True)
        currency = fields.Str(required=True)
        creation_date = fields.Date(required=True)
        info = fields.Str(required=False)
        user_id = fields.Int(required=True)

    try:
        wallet = Wallet().load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400
    if db.session.query(models.Wallet).filter(models.Wallet.user_id == wallet['user_id']).count() != 0:
        return jsonify({'message': 'Wallet already exists'}), 400

    user = db.session.query(models.User).filter(models.User.id == wallet['user_id']).first()
    if user is None:
        return jsonify({'message': 'User does not exists'}), 400

    if request.json['balance'] < 1:
        return jsonify({'error': 'Can`t set less than 1'}), 404

    new_wallet = models.Wallet(balance=wallet['balance'], currency=wallet['currency'],
                               creation_date=wallet['creation_date'], info=wallet["info"], user_id=wallet["user_id"])
    try:
        db.session.add(new_wallet)
    except:
        db.session.rollback()
        return jsonify({'message': 'Error creating wallet'}), 500
    db.session.commit()
    return get_wallet(new_wallet.id)[0], 200


@wallet_bp.route('/<int:wallet_id>', methods=['GET'])
def get_wallet(wallet_id):
    wallet = db.session.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    if wallet is None:
        return jsonify({'message': 'Wallet not found'}), 404
    res = {'id': wallet.id, 'balance': wallet.balance, 'currency': wallet.currency,
           "creation_date": wallet.creation_date, "info": wallet.info, "user_id": wallet.user_id}
    return jsonify(res), 200


@wallet_bp.route('/<int:wallet_id>', methods=['PUT'])
def update_wallet(wallet_id):
    class Wallet(Schema):
        new_currency = fields.Str(required=False)
        new_info = fields.Str(required=False)

    try:
        wallet = Wallet().load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400
    wallet_to_update = db.session.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    if wallet_to_update is None:
        return jsonify({'message': 'Wallet not found'}), 404

    try:
        if wallet.__contains__('new_currency'):
            wallet_to_update.currency = wallet['new_currency']
        if wallet.__contains__('new_info'):
            wallet_to_update.info = wallet['new_info']
    except:
        db.session.rollback()
        return jsonify({'message': 'Error updating wallet'}), 500
    db.session.commit()
    return get_wallet(wallet_id)[0], 200


@wallet_bp.route('/<int:wallet_id>', methods=['DELETE'])
def delete_wallet(wallet_id):
    wallet = db.session.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    transactions = db.session.query(models.Transaction).filter(models.Transaction.wallet_id_1 == wallet_id).all()
    if wallet is None:
        return jsonify({'message': 'Wallet not found'}), 404
    try:
        for el in transactions:
            if el is None:
                break
            db.session.delete(el)
        db.session.delete(wallet)
    except:
        db.session.rollback()
        return jsonify({'message': 'Error deleting wallet'}), 500
    db.session.commit()
    return jsonify({'message': 'Wallet deleted'}), 200
