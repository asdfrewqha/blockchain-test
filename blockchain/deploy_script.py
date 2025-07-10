import os
import json
import time
from web3 import Web3
from dotenv import load_dotenv
from solcx import compile_standard, install_solc, get_installable_solc_versions, set_solc_version
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def deploy_contracts():
    try:
        logger.info("="*50)
        logger.info("ЗАПУСК ДЕПЛОЙ-СКРИПТА")
        logger.info("="*50)
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        env_path = "./.env"
        load_dotenv(env_path)
        logger.info(f"Загружен .env файл: {env_path}")

        node_url = os.getenv("REACT_APP_GANACHE_URL")
        logger.info(f"Подключаемся к ноде: {node_url}")
        w3 = Web3(Web3.HTTPProvider(node_url))
        
        if not w3.is_connected():
            logger.error("❌ Не удалось подключиться к ноде!")
            logger.error("Проверьте URL и доступность интернета")
            return
        
        logger.info("✅ Успешное подключение к блокчейн-ноде")
        logger.info(f"ID сети: {w3.eth.chain_id}")
        logger.info(f"Последний блок: {w3.eth.block_number}")

        private_key = os.getenv("REACT_APP_OWNER_PRIVATE_KEY")
        if not private_key:
            logger.error("❌ Приватный ключ не найден в .env")
            return
        
        try:
            account = w3.eth.account.from_key(private_key)
            logger.info(f"Адрес кошелька: {account.address}")
        except ValueError as e:
            logger.error(f"❌ Неверный формат приватного ключа: {e}")
            return

        balance = w3.eth.get_balance(account.address)
        logger.info(f"Баланс: {w3.from_wei(balance, 'ether')} MATIC")
        
        if balance < w3.to_wei(0.001, 'ether'):
            print("Доступные аккаунты:")
            for i, acc in enumerate(w3.eth.accounts):
                print(f"[{i}] {acc}, баланс: {w3.from_wei(w3.eth.get_balance(acc), 'ether')} ETH")
            logger.error("❌ Недостаточно средств для деплоя!")
            return


        logger.info("Устанавливаем компилятор Solidity 0.8.20...")
        available_versions = get_installable_solc_versions()
        available_versions_str = [str(v) for v in available_versions]
        if '0.8.20' not in available_versions_str:
            logger.error("Версия 0.8.20 не найдена среди доступных для установки.")
            logger.error(f"Доступные версии: {available_versions_str}")
            return
        install_solc('0.8.0')
        set_solc_version('0.8.0')
        logger.info("✅ Компилятор установлен и выбран")

        contract_path = os.path.join(base_dir, 'node_modules', '@openzeppelin', 'contracts', 'metatx', 'MinimalForwarder.sol')
        logger.info(f"Компилируем контракт из: {contract_path}")
        
        try:
            with open(contract_path, 'r') as file:
                source_code = file.read()
                logger.debug(f"Исходный код:\n{source_code[:200]}...")
        except Exception as e:
            logger.error(f"❌ Ошибка чтения файла: {e}")
            return

        try:
            compiled_sol = compile_standard(
                {
                    "language": "Solidity",
                    "sources": {
                        "MinimalForwarder.sol": {
                            "content": source_code
                        }
                    },
                    "settings": {
                        "outputSelection": {
                            "*": {"*": ["abi", "evm.bytecode.object"]}
                        },
                        "remappings": [
                            "@openzeppelin/contracts/=node_modules/@openzeppelin/contracts/"
                        ]
                    }
                },
                base_path=base_dir,            
                allow_paths=[base_dir, 
                            os.path.join(base_dir, "node_modules")]
            )
            logger.info("✅ Контракт 2 успешно скомпилирован")
        except Exception as e:
            logger.error(f"❌ Ошибка компиляции: {e}")
            return

        bytecode = compiled_sol['contracts']['MinimalForwarder.sol']['MinimalForwarder']['evm']['bytecode']['object']
        abi = compiled_sol['contracts']['MinimalForwarder.sol']['MinimalForwarder']['abi']

        abi_path = os.path.join(base_dir, 'abi_forwarder.json')
        with open(abi_path, 'w') as f:
            json.dump(abi, f)
        logger.info(f"ABI сохранен в {abi_path}")

        VotingNotary = w3.eth.contract(abi=abi, bytecode=bytecode)
        nonce = w3.eth.get_transaction_count(account.address)
        logger.info(f"Nonce: {nonce}")

        transaction = VotingNotary.constructor().build_transaction({
            'chainId': 1337,
            'gas': 3000000,
            'gasPrice': w3.to_wei('25', 'gwei'),
            'nonce': nonce,

        })
        
        logger.info(f"Размер транзакции: {len(transaction['data'])} байт")
        estimated_gas = w3.eth.estimate_gas(transaction)
        logger.info(f"Оценка газа: {estimated_gas}")

        logger.info("Подписываем транзакцию...")
        signed_txn = account.sign_transaction(transaction)
        
        logger.info("Отправляем транзакцию в сеть...")
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        logger.info(f"Транзакция отправлена! Хеш: {tx_hash.hex()}")

        logger.info("Ожидаем подтверждения транзакции...")
        start_time = time.time()
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        logger.info(f"✅ Транзакция подтверждена за {time.time() - start_time:.2f} сек")
        logger.info(f"Блок: {tx_receipt.blockNumber}")
        logger.info(f"Использовано газа: {tx_receipt.gasUsed}")
        logger.info(f"Адрес контракта: {tx_receipt.contractAddress}")

        with open(env_path, 'a') as env_file:
            env_file.write(f'\nREACT_APP_FORWARDER_CONTRACT_ADDRESS="{tx_receipt.contractAddress}"')
        logger.info(f"Адрес контракта записан в {env_path}")




        contract_path = os.path.join(base_dir, 'contracts', 'VotingTopic.sol')
        context_path = os.path.join(base_dir, "node_modules", '@openzeppelin', 'contracts', 'context')
        logger.info(f"Компилируем контракт: {contract_path}")
        
        try:
            with open(contract_path, 'r') as file:
                source_code = file.read()
                logger.debug(f"Исходный код:\n{source_code[:200]}...")
        except Exception as e:
            logger.error(f"❌ Ошибка чтения файла: {e}")
            return

        try:
            compiled_sol = compile_standard({
                "language": "Solidity",
                "sources": {"VotingTopic.sol": {"content": source_code}},
                "settings": {
                    "outputSelection": {
                        "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
                    },
                    "remappings": [
                            "@openzeppelin/contracts/=node_modules/@openzeppelin/contracts/"
                    ]
                }
            }, base_path=base_dir, allow_paths=[context_path])
            logger.info("✅ Контракт 1 успешно скомпилирован")
        except Exception as e:
            logger.error(f"❌ Ошибка компиляции: {e}")
            return

        bytecode = compiled_sol['contracts']['VotingTopic.sol']['VotingManager']['evm']['bytecode']['object']
        abi = compiled_sol['contracts']['VotingTopic.sol']['VotingManager']['abi']
        
        abi_path = os.path.join(base_dir, 'abi.json')
        with open(abi_path, 'w') as f:
            json.dump(abi, f)
        logger.info(f"ABI сохранен в {abi_path}")

        VotingNotary = w3.eth.contract(abi=abi, bytecode=bytecode)
        nonce = w3.eth.get_transaction_count(account.address)
        logger.info(f"Nonce: {nonce}")

        transaction = VotingNotary.constructor(tx_receipt.contractAddress).build_transaction({
            'chainId': 1337,
            'gas': 3000000,
            'gasPrice': w3.to_wei('25', 'gwei'),
            'nonce': nonce,
        })
        
        logger.info(f"Размер транзакции: {len(transaction['data'])} байт")
        estimated_gas = w3.eth.estimate_gas(transaction)
        logger.info(f"Оценка газа: {estimated_gas}")


        logger.info("Подписываем транзакцию...")
        signed_txn = account.sign_transaction(transaction)
        
        logger.info("Отправляем транзакцию в сеть...")
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        logger.info(f"Транзакция отправлена! Хеш: {tx_hash.hex()}")

        logger.info("Ожидаем подтверждения транзакции...")
        start_time = time.time()
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
        
        logger.info(f"✅ Транзакция подтверждена за {time.time() - start_time:.2f} сек")
        logger.info(f"Блок: {tx_receipt.blockNumber}")
        logger.info(f"Использовано газа: {tx_receipt.gasUsed}")
        logger.info(f"Адрес контракта: {tx_receipt.contractAddress}")

        with open(env_path, 'a') as env_file:
            env_file.write(f'\nREACT_APP_CONTRACT_ADDRESS="{tx_receipt.contractAddress}"')
        logger.info(f"Адрес контракта записан в {env_path}")



        

    except Exception as e:
        logger.exception("❌ КРИТИЧЕСКАЯ ОШИБКА:")
        logger.error(f"Ошибка: {e}")