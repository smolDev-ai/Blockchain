import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request
from flask_cors import CORS

DIFFICULTY = "000000"


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        self.new_block(previous_hash=1, proof=100)

    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({'sender': sender, "recipient": recipient, "amount": amount})

        return self.last_block['index'] + 1

    def new_block(self, proof, previous_hash=None):
        block = {
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[:-1])

        }

        self.current_transactions = []

        self.chain.append(block)

        return block

    def hash(self, block):
        new_string = json.dumps(block, sort_keys=True)
        block_string = new_string.encode()

        hash_string = hashlib.sha256(block_string).hexdigest()

        return hash_string

    @property
    def last_block(self):
        return self.chain[-1]


    @staticmethod
    def valid_proof(block_string, proof):
        guess = f"{block_string}{proof}".encode()
        guessing_hash = hashlib.sha256(guess).hexdigest()
        return guessing_hash[:6] == DIFFICULTY

app = Flask(__name__)
CORS(app)

node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()


@app.route('/')
def api_up():
    return "Api is up!"


@app.route('/chain')
def full_chain():
    response = {
        "chain": blockchain.chain,
        "length": len(blockchain.chain),
    }

    return jsonify(response), 200


@app.route('/last_block', methods=['GET'])
def get_last_block():
    response = {
        "chain": blockchain.last_block,
        "length": len(blockchain.chain)
    }

    return jsonify(response), 200


@app.route('/mine', methods=['POST'])
def mine():
    data = request.get_json()

    if data["proof"] is None or data["id"] is None:
        response = {
            "message": "INVALID, proof and/or id must be supplied!"
        }
        return jsonify(response), 400
    
    proof = data["proof"]
    block_string = json.dumps(blockchain.last_block, sort_keys=True)
    new_hash = blockchain.valid_proof(block_string, proof)

    if new_hash is True:
        if blockchain.last_block["proof"] != proof:
            blockchain.new_transaction(0, data['id'], 1)
            new_block = blockchain.new_block(proof)
      
            response = {
                "message": "New Block Forged",
                "new_block": new_block,
            }
            
            return jsonify(response), 201
        else:
            response = {
                "message": "unable to create new block, block already claimed."
            }
            return jsonify(response), 200

@app.route('/transaction/new', methods=['POST'])
def receive_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']

    if not all(k in values for k in required):
        response = {
            "message": "You're missing required fields, please check your request and try again."
        }
        return jsonify(response), 401

    index = blockchain.new_transaction(*values)

    response = {
        "message": f"Transaction will be added to block: {index}"
    }

    return jsonify(response), 201


@app.route('/wallet/<user>')
def wallet(user):
    balance = 0
    remove_funds = []
    add_funds = []
    # loop through the chain find the current transactions of the link
    # if user is the sender subtract the amount they sent
    # if user is the recipient add the amount the received        

    for block in blockchain.chain:
        for transaction in block.transactions:
            if transaction['sender'] == user:
                balance -= transaction['amount']
                remove_funds.append(transaction)
            if transaction['recipient'] == user:
                balance += transaction['amount']
                add_funds.append(transaction)
    response = {
        "user": user,
        "balance": balance,
        "negative_transactions": remove_funds,
        "positive_transactions": add_funds
    }
    
    return jsonify(response), 200




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
