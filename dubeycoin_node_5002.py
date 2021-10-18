"@author : Mukund"
"Cryptocurrency"
"Uses Flask and Postman"
import datetime
"To get exact date the blockchain was created"
import hashlib
"To use Hash functions to hash blocks"
import json
"To encode the blocks before hashing them"
from flask import Flask, jsonify, request #request->connect nodes
import requests
from uuid import uuid4
from urllib.parse import urlparse
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
        self.transactions=[]
        self.create_block(proof=1,previous_hash='0')
        "prev hash is 0(arbitrary value) coz genesis block is the 1st block"
        "0 is string type coz SHA 256 accepts only string arguements"
        self.nodes=set()
    
    def create_block(self, proof, previous_hash):
        block={'index':len(self.chain)+1,
               'timestamp': str(datetime.datetime.now()),
               "proof":proof,
               'previous_hash':previous_hash,
               'transactions':self.transactions
               }
        self.transactions=[]
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
    
    def add_transactions(self,sender,reciever,amount):
        self.transactions.append({'sender':sender,
                                  'reciever':reciever,
                                  'amount':amount
                                  })
        previous_block = self.get_previous_block()
        return previous_block['index']+1
    
    def add_node(self,address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network :
            #port 5000 is for 1 node, we need multiple http://127.0.0.1:5000/get_chain
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200 : 
              length = response.json()['length']
              chain = response.json()['chain']
              if length > max_length and self.is_chain_valid(chain):
                  max_length = length
                  longest_chain = chain
        if longest_chain : #is not None:
            self.chain = longest_chain
            return True
        return False
# mining the blockchain


app = Flask(__name__) #creating a web app

#address creation for node on port 5000
node_address = str(uuid4()).replace('-','')

blockchain = Blockchain() #creating a blockchain

@app.route('/mine_block', methods = ['GET']) #mining new block
def mine_block():
    previous_block = blockchain.get_previous_block()
    previous_proof = previous_block['proof']
    proof = blockchain.proof_of_work(previous_proof)
    previous_hash = blockchain.hash(previous_block)
    blockchain.add_transactions(sender = node_address, reciever = 'Mukund', amount = 1)
    block = blockchain.create_block(proof, previous_hash)
    response = {'message' : 'Congratulations! You mined a block!',
                'index' : block['index'],
                'timestamp' : block['timestamp'],
                'proof' : block['proof'],
                'previous_hash' : block['previous_hash'],
                'transactions' : block['transactions']
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

@app.route('/add_transaction', methods = ['POST'])
def add_transaction() :
    json = request.get_json() #json format is like python's dict key only
    transaction_keys = ['sender', 'reciever', 'amount']
    if not all (key in json for key in transaction_keys):
        return 'Sender,reciver,amount format not followed!!', 400
    index = blockchain.add_transactions(json['sender'],json['reciever'],json['amount'])
    response = {'message': f'This transaction is added to block {index}'}
    return jsonify(response), 201 #200 is for get but 201 is for post

#now decentralization begins
@app.route('/connect_node', methods = ['POST'])
def connect_node() : 
    json = request.get_json()
    nodes = json.get('nodes')   
    if nodes is None :
        return 'No nodes', 400
    for node in nodes :
        blockchain.add_node(node)
    response = {'message': 'Dubeycoin Blockchain now contains ',
                'total nodes':list(blockchain.nodes)
                }
    return jsonify(response), 201

#replace longest chain 
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    if is_chain_replaced == True :
        #if nodes had different chains then it'll be replaced by the longest one
        response = {'message': 'Replaced!!',
                    'new_chain':blockchain.chain()
                    }
    else :
        response = {'message': 'Not replaced!!',
                    'chain':blockchain.chain()
                    }
    return jsonify(response), 200
#to run app
app.run(host = '0.0.0.0', port = 5002)
    