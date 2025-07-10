import { ethers } from "ethers";
import dotenv from 'dotenv';
dotenv.config();



async function Vote(topicId, option) {
    async function sendMetaTx(data) {
        async function getNonceFromForwarder(forwarderAddress, from) {
            const forwarderAbi = [
                "function getNonce(address from) view returns (uint256)"
            ];
            const forwarder = new ethers.Contract(forwarderAddress, forwarderAbi, provider);
            const nonce = await forwarder.getNonce(from);
            return nonce.toString();
        }

        async function safeStringify(obj) {
            return JSON.stringify(obj, (key, value) =>
                typeof value === 'bigint' ? value.toString() : value
            );
        }

        async function loadWalletFromLocalStorage() {
            const privateKey = localStorage.getItem('privateKey');
            if (!privateKey) {
                throw new Error("Wallet not found in localStorage");
            }
            const wallet = new ethers.Wallet(privateKey);
            return wallet;
        }
        const clientWallet = await loadWalletFromLocalStorage();
        const clientAddress = clientWallet.address;

        const BackendUrl = process.env.REACT_APP_BACKEND_URL;
        const BACKEND_PORT = process.env.REACT_APP_BACKEND_PORT;
        const BLOCKCHAIN_NODE_URL = process.env.REACT_APP_BLOCKCHAIN_NODE_URL;

        const adresses_url = `${BackendUrl}:${BACKEND_PORT}/adresses`
        console.log("Fetching addresses from:", adresses_url);
        const response = await fetch(adresses_url, {
                method: "GET",
            });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const response_data = await response.json();
        const contractAddress = response_data.VOTING_ADRESS;
        const forwarderAddress = response_data.FORWARDER_ADRESS;

        const provider = new ethers.JsonRpcProvider(BLOCKCHAIN_NODE_URL);
        const nonce = await getNonceFromForwarder(forwarderAddress, clientAddress);

        const request_to_sign = {
            from: clientAddress,
            to: contractAddress,
            value: 0,
            gas: 1_000_000,
            gasPrice: ethers.parseUnits('10', 'gwei').toString(),
            nonce: Number(nonce),
            data,
        };

        const domain = {
            name: "MinimalForwarder",
            version: "0.0.1",
            chainId: 1337,
            verifyingContract: forwarderAddress,
        };

        const types = {
            ForwardRequest: [
                { name: "from", type: "address" },
                { name: "to", type: "address" },
                { name: "value", type: "uint256" },
                { name: "gas", type: "uint256" },
                { name: "nonce", type: "uint256" },
                { name: "data", type: "bytes" },
            ],
        };

        const signature = await clientWallet.signTypedData(domain, types, request_to_sign);

        const request = {
            from_ad: clientAddress,
            to: contractAddress,
            value: 0,
            gas: 1_000_000,
            gasPrice: ethers.parseUnits('10', 'gwei').toString(),
            nonce: Number(nonce),
            data,
        };

        const request_to_send = await safeStringify({ request, signature });

        try {
            const relayRes = await fetch(`${BackendUrl}:${BACKEND_PORT}/relay`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: request_to_send,
            });

            if (!relayRes.ok) {
                throw new Error(`HTTP error! status: ${relayRes.status}`);
            }

            const relayResult = await relayRes.json();
            console.log("Relay tx result:", relayResult);

            return {
                txHash: relayResult.tx_hash,
                status: "success"
            };
        } catch (error) {
            console.error("Error in sendMetaTx:", error);
            throw error;
        }
    }
    const ABI = [
        "function vote(string topicId, string option)"
    ];
    const iface = new ethers.Interface(ABI);
    const data = iface.encodeFunctionData("vote", [topicId, option]);

    try {
        const result = await sendMetaTx(data);
        console.log("Vote transaction completed:", result);
        return result;
    } catch (error) {
        console.error("Error in Vote:", error);
        throw error;
    }
}

Vote("6", "Option6")
