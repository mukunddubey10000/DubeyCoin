"@author : Mukund"
"Blockchain"
"Uses Flask and Postman"
import datetime
"To get exact date the blockchain was created"
import hashlib
"To use Hash functions to hash blocks"
import json
"To encode the blocks before hashing them"
from flask import Flask, jsonify
"Flask to create web application"
"jsonify to interact with blockchain in postman"

"""Instead of using functions we use class because class has properties,
functions, methods, tools and all of them interact with each other which
is very practical"""

#building a blockchain
class Blockchain:
    "use def to define function"
    "self refers to the object of Blockchain"
    def __init__(self):
        self.chain=[] 
        "it's just a list declared by []"
        "now create a genesis block which is the 1st block of Blockchain"
        self.create_block(proof=1,previous_hash='0')
        "prev hash is 0(arbitrary value) coz genesis block is the 1st block"
        "0 is string type coz SHA 256 accepts only string arguements"
    def create_block(self, proof, previous_hash):
        block={'index':len(self.chain)+1,
               'timestamp': str(datetime.datetime.now()),
               "proof":proof,
               'previous_hash':previous_hash}
        self.chain.append(block)
        return block
    def get_previous_block(self):
        return self.chain[-1]
    "-1 gives previous index"
    def proof_of_work(self, previous_proof):
        new_proof=1
        check_proof=False
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            "can't take new+prev coz it's == prev+new (associative operation)"
            """this is a task which miners need to solve so I can make it diff.
            to mine else who would mine if it's not worth it"""
            if hash_operation[:4] =='0000' :
                """miner wins"""
                check_proof = True 
            else :
                new_proof+=1
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    def is_chain_valid(self, chain):
        "check if whole chain is valid by iterating from start to end"
        previous_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != self.hash(previous_block):
                return False
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        return True

# mining the blockchain


app = Flask(__name__) #creating a web app

blockchain = Blockchain() #creating a blockchain

@app.route('/mine_block', methods = ['GET']) #mining new block
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message' : 'Congratulations! You mined a block!',
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'proof' : block['proof'],
                'previous_hash' : block['previous_hash']
                } #response to user using postman 
    return jsonify(response), 200

#get the full blockchain on display
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,'length': len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/is_valid', methods = ['GET'])
def is_valid():
    isvalid = blockchain.is_chain_valid(blockchain.chain)
    if isvalid==True :
        response = {'message': 'VALID!!'}
    else :
        response = {'message': 'INVALID!! '}
    return jsonify(response), 200
#to run app
app.run(host = '0.0.0.0', port = 5000)
    