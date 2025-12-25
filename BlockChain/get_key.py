import os
import sys
import json
import argparse
from web3 import Web3
from dotenv import load_dotenv


def get_model_public_key(model_name):
    load_dotenv()

    base_path = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_path, "deployed_info.json")
    infura_url = os.getenv("INFURA_URL")

    if not os.path.exists(json_path):
        return f"Error: {json_path} not found"

    w3 = Web3(Web3.HTTPProvider(infura_url))

    with open(json_path, "r") as f:
        data = json.load(f)
        contract_address = data["address"]
        abi = data["abi"]

    contract = w3.eth.contract(address=contract_address, abi=abi)

    try:
        public_key = contract.functions.getModelKey(model_name).call()
        if public_key.hex() == "0x" + "0" * 64:
            return None
        return public_key.hex()
    except Exception as _:
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    args = parser.parse_args()

    result = get_model_public_key(args.name)

    if result is None:
        print(f"No data found for model: {args.name}")
        exit(1)
    elif not result:
        print("Error")
    else:
        print(f"Model: {args.name}")
        print(f"Public Key: {result}")
