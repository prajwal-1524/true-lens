import os
import json
import sys
from web3 import Web3
from solcx import compile_standard, install_solc
from dotenv import load_dotenv


def valid_env():
    load_dotenv()
    required_vars = ["INFURA_URL", "PRIVATE_KEY", "MY_ADDRESS"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        print(f"Configuration Error: Missing {missing_vars}")
        return False
    return True


if not valid_env():
    sys.exit(1)

INFURA_URL = os.environ["INFURA_URL"]
PRIVATE_KEY = os.environ["PRIVATE_KEY"]
MY_ADDRESS = Web3.to_checksum_address(os.environ["MY_ADDRESS"])

SOLC_VERSION = "0.8.19"
install_solc(SOLC_VERSION)

with open("./SmartContract.sol", "r") as file:
    source_code = file.read()

# Compiling
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SmartContract.sol": {"content": source_code}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "evm.bytecode", "evm.bytecode.object"]}
            }
        },
    },
    solc_version=SOLC_VERSION,
)

bytecode = compiled_sol["contracts"]["SmartContract.sol"]["Camera"]["evm"]["bytecode"][
    "object"
]
abi = compiled_sol["contracts"]["SmartContract.sol"]["Camera"]["abi"]

w3 = Web3(Web3.HTTPProvider(INFURA_URL))
chain_id = 11155111  # For Sepolia Test network

print(f"Deploying 'Camera' contract to Sepolia from {MY_ADDRESS}...")
CameraContract = w3.eth.contract(abi=abi, bytecode=bytecode)
nonce = w3.eth.get_transaction_count(MY_ADDRESS)
deploy_txn = CameraContract.constructor().build_transaction(
    {
        "chainId": chain_id,
        "from": MY_ADDRESS,
        "nonce": nonce,
        "gasPrice": w3.eth.gas_price,
    }
)

signed_deploy = w3.eth.account.sign_transaction(deploy_txn, private_key=PRIVATE_KEY)
tx_hash = w3.eth.send_raw_transaction(signed_deploy.raw_transaction)

print("Waiting for deployment receipt...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = tx_receipt.contractAddress

print(f"Contract deployed at: {contract_address}")

# Saved the address and ABI
with open("deployed_info.json", "w") as f:
    json.dump({"address": contract_address, "abi": abi}, f)
