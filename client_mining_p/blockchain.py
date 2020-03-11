import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

DIFFICULTY = "000000"


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        self.new_block(previous_hash=1, proof=100)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
