import json
import os
import time

import uvicorn
from deploy_script import deploy_contracts
from dotenv import load_dotenv
from eth_account.messages import encode_typed_data
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from pydantic import BaseModel
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

app = FastAPI()
base_dir = os.path.dirname(os.path.abspath(__file__))
env_path = "./.env"
load_dotenv(env_path)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://localhost:3000", "https://vote.vickz.ru"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ForwardRequest(BaseModel):
    from_ad: str
    to: str
    value: int
    gas: int
    nonce: int
    data: str


class RelayPayload(BaseModel):
    request: ForwardRequest
    signature: str


@app.get("/")
async def redirect():
    return RedirectResponse("/docs")


@app.post("/relay")
def relay_transaction(payload: RelayPayload):
    RELAY_PRIVATE_KEY = os.getenv("REACT_APP_OWNER_PRIVATE_KEY")
    GANACHE_URL = os.getenv("REACT_APP_GANACHE_URL")
    FORWARDER_ADDRESS = os.getenv("REACT_APP_FORWARDER_CONTRACT_ADDRESS")
    web3 = Web3(Web3.HTTPProvider(GANACHE_URL))
    web3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)
    RELAY_ADDRESS = web3.eth.account.from_key(RELAY_PRIVATE_KEY).address
    with open("abi_forwarder.json") as f:
        forwarder_abi = json.load(f)
    forwarder = web3.eth.contract(address=FORWARDER_ADDRESS, abi=forwarder_abi)
    print(payload.request.from_ad)
    request = {
        "from": payload.request.from_ad,
        "to": payload.request.to,
        "value": payload.request.value,
        "gas": payload.request.gas,
        "nonce": payload.request.nonce,
        "data": payload.request.data,
    }

    domain = {
        "name": "MinimalForwarder",
        "version": "0.0.1",
        "chainId": web3.eth.chain_id,
        "verifyingContract": FORWARDER_ADDRESS,
    }

    types = {
        "ForwardRequest": [
            {"name": "from", "type": "address"},
            {"name": "to", "type": "address"},
            {"name": "value", "type": "uint256"},
            {"name": "gas", "type": "uint256"},
            {"name": "nonce", "type": "uint256"},
            {"name": "data", "type": "bytes"},
        ]
    }

    typed_data = {
        "types": types,
        "domain": domain,
        "primaryType": "ForwardRequest",
        "message": request,
    }

    encoded = encode_typed_data(full_message=typed_data)
    signer = web3.eth.account.recover_message(encoded, signature=payload.signature)

    if signer.lower() != request["from"].lower():
        raise HTTPException(status_code=400, detail="Invalid signature")

    tx = forwarder.functions.execute(request, payload.signature).build_transaction(
        {
            "from": RELAY_ADDRESS,
            "nonce": web3.eth.get_transaction_count(RELAY_ADDRESS),
            "gas": request["gas"] + 100_000,
            "gasPrice": web3.eth.gas_price,
        }
    )

    signed_tx = web3.eth.account.sign_transaction(tx, private_key=RELAY_PRIVATE_KEY)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print(f"Transaction sent: {tx_hash.hex()}")
    return {"tx_hash": tx_hash.hex()}


@app.get("/votes")
def get_votes(options: list[str] = Query(), topic_id: str = Query()):
    res = {}
    VOTING_CONTRACT = os.getenv("REACT_APP_CONTRACT_ADDRESS")
    GANACHE_URL = os.getenv("REACT_APP_GANACHE_URL")
    print(VOTING_CONTRACT)
    web3 = Web3(Web3.HTTPProvider(GANACHE_URL))
    with open(os.path.join(os.path.dirname(__file__), "abi.json")) as f:
        abi = json.load(f)
    for option in options:
        voting_contract = web3.eth.contract(address=VOTING_CONTRACT, abi=abi)
        votes = voting_contract.functions.getVotes(topic_id, option).call()
        res[option] = votes
    return JSONResponse(content=res)


@app.get("/adresses")
def send_adresses():
    VOTING_ADRESS = os.getenv("REACT_APP_CONTRACT_ADDRESS")
    FORWARDER_ADRESS = os.getenv("REACT_APP_FORWARDER_CONTRACT_ADDRESS")
    return JSONResponse(
        content={"VOTING_ADRESS": VOTING_ADRESS, "FORWARDER_ADRESS": FORWARDER_ADRESS}
    )


if __name__ == "__main__":
    time.sleep(10)
    if os.getenv("REACT_APP_CONTRACT_ADDRESS") is None:
        deploy_contracts()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = "./.env"
        load_dotenv(env_path)
        uvicorn.run(
            app, host="0.0.0.0", port=int(os.getenv("REACT_APP_BACKEND_PORT")), reload=False
        )
    else:
        uvicorn.run(
            app, host="0.0.0.0", port=int(os.getenv("REACT_APP_BACKEND_PORT")), reload=False
        )
