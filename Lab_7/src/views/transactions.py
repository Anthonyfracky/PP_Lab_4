from marshmallow import Schema, fields, ValidationError
from flask import Blueprint, jsonify, request
from flask_bcrypt import Bcrypt
from src.utils import *
import src.models as models
import src.db as db

transaction_bp = Blueprint('transaction', __name__, url_prefix='/transaction')
bcrypt = Bcrypt()


@transaction_bp.route('/', methods=['POST'])
def create_transaction():
    class Transaction(Schema):
        wallet_id_1 = fields.Int(required=True)
        wallet_id_2 = fields.Int(required=True)
        amount_of_money = fields.Int(required=True)
        currency = fields.Str(required=True)
        date_time = fields.Date(required=False)
        transaction_description = fields.Str(required=True)

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

    if request.json['amount_of_money'] < 0:
        return jsonify({'error': 'Can`t set money like this'}), 404

    if wallet_1.balance < request.json['amount_of_money']:
        return jsonify({'error': 'Not enough money'}), 404

    wallet_2.balance += request.json['amount_of_money']
    wallet_1.balance -= request.json['amount_of_money']

    new_transaction = models.Transaction(wallet_id_2=transaction['wallet_id_2'],
                                         amount_of_money=transaction['amount_of_money'],
                                         currency=transaction["currency"],
                                         transaction_description=transaction['transaction_description'],
                                         wallet_id_1=transaction['wallet_id_1'])

    if transaction.__contains__('date_time'):
        new_transaction.date_time = transaction['date_time']
    try:
        db.session.add(new_transaction)
    except:
        db.session.rollback()
        return jsonify({'message': 'Error creating transaction'}), 500
    db.session.commit()
    return (get_transaction_by_wallet_id(new_transaction.wallet_id_1)), 200


@transaction_bp.route('/<wallet_id>', methods=['GET'])
def get_transaction(wallet_id):
    wallet = db.session.query(models.Wallet).filter(models.Wallet.id == wallet_id).first()
    if wallet is None:
        return jsonify({'message': 'Wallet not found'}), 404
    transactions = db.session.query(models.Transaction).filter(models.Transaction.wallet_id_1 == wallet_id).all()
    return jsonify([get_transaction_by_wallet_id(op.wallet_id_1) for op in transactions]), 200


@transaction_bp.route('/<int:trans_id>', methods=['DELETE'])
def delete_trans(trans_id):
    trans = db.session.query(models.Transaction).filter(models.Transaction.id == trans_id).first()
    if trans is None:
        return jsonify({'message': 'Transaction not found'}), 404
    try:
        db.session.delete(trans)
    except:
        db.session.rollback()
        return jsonify({'message': 'Error deleting transaction'}), 500
    db.session.commit()
    return jsonify({'message': 'Transaction deleted'}), 200
