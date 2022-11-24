from marshmallow import Schema, fields, ValidationError
from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
from src.utils import *
import src.models as models
import src.db as db
from src import app
from flask_jwt_extended import (
    JWTManager, jwt_required, get_jwt_identity
)

jwt = JWTManager(app)

transaction_bp = Blueprint('transaction', __name__, url_prefix='/transaction')
bcrypt = Bcrypt()


@transaction_bp.route('/', methods=['POST'])
@jwt_required()
def create_transaction():
    class Transaction(Schema):
        wallet_id_1 = fields.Int(required=True)
        wallet_id_2 = fields.Int(required=True)
        amount_of_money = fields.Int(required=True)

    try:
        transaction = Transaction().load(request.json)
    except ValidationError as error:
        return jsonify(error.messages), 400

    wallet_1 = db.session.query(models.Wallet).filter_by(id=request.json['wallet_id_1']).first()
    if wallet_1 is None:
        return jsonify({'error': 'Wrong id of first wallet'}), 404
    wallet_2 = db.session.query(models.Wallet).filter_by(id=request.json['wallet_id_2']).first()
    if wallet_2 is None:
        return jsonify({'error': 'Wrong id of second wallet'}), 404
    if get_jwt_identity() != wallet_1.user_id:
        return jsonify({'message': 'Forbidden'}), 403
    if request.json['amount_of_money'] < 0:
        return jsonify({'error': 'Can`t set money like this'}), 404

    if wallet_1.balance < request.json['amount_of_money']:
        return jsonify({'error': 'Not enough money'}), 404

    wallet_2.balance += request.json['amount_of_money']
    wallet_1.balance -= request.json['amount_of_money']

    new_transaction = models.Transaction(wallet_id_2=transaction['wallet_id_2'],
                                         amount_of_money=transaction['amount_of_money'],
                                         wallet_id_1=transaction['wallet_id_1'])

    db.session.add(new_transaction)
    db.session.commit()
    return (get_transaction_by_wallet_id(new_transaction.wallet_id_1)[-1]), 200


@transaction_bp.route('/<wallet_id>', methods=['GET'])
@jwt_required()
def get_transaction(wallet_id):
    wallet = db.session.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    if wallet is None:
        return jsonify({'message': 'Wallet not found'}), 404
    if get_jwt_identity() != wallet.user_id:
        return jsonify({'message': 'Forbidden'}), 403
    return jsonify(get_transaction_by_wallet_id(wallet_id)), 200


@transaction_bp.route('/<int:trans_id>', methods=['DELETE'])
def delete_trans(trans_id):
    trans = db.session.query(models.Transaction).filter(models.Transaction.id == trans_id).first()
    if trans is None:
        return jsonify({'message': 'Transaction not found'}), 404
    db.session.delete(trans)
    db.session.commit()
    return jsonify({'message': 'Transaction deleted'}), 200
