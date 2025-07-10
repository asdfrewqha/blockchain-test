import { ethers } from "ethers";
import dotenv from 'dotenv';
dotenv.config();

// Настройки подключения
const provider = new ethers.JsonRpcProvider(process.env.BLOCKCHAIN_NODE_URL || "http://localhost:8545");
const contractAddress = process.env.CONTRACT_ADDRESS;
const backendUrl = process.env.BACKEND_URL || "http://localhost";
const backendPort = process.env.BACKEND_PORT || 8000;

// ABI контракта (только нужные функции)
const votingManagerABI = [
    "function getVotes(string memory topicId, string memory option) external view returns (uint256)"
];

async function getVotes(topicId, option) {
    try {
        // Создаем экземпляр контракта
        const votingContract = new ethers.Contract(
            contractAddress,
            votingManagerABI,
            provider
        );

        // Получаем голоса
        const votes = await votingContract.getVotes(topicId, option);
        
        console.log(`Голосов за опцию "${option}" в топике "${topicId}":`, votes.toString());
        return votes;
        
    } catch (error) {
        console.error("Ошибка при получении голосов:", error);
        throw error;
    }
}

// Альтернативный вариант через ваш бэкенд (если предпочитаете)
async function getVotesViaBackend(topicId, option) {
    try {
        const response = await fetch(`${backendUrl}:${backendPort}/votes?topic_id=${topicId}&option=${option}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log(`Голосов через бэкенд:`, data.votes);
        return data.votes;
        
    } catch (error) {
        console.error("Ошибка при запросе к бэкенду:", error);
        throw error;
    }
}

// Пример использования
const topicId = "3";
const option = "Option3";

// Вариант 1: Прямой запрос к контракту
getVotes(topicId, option)
    .then(votes => console.log("Результат:", votes))
    .catch(console.error);

// Вариант 2: Через ваш бэкенд (нужно раскомментировать)
// getVotesViaBackend(topicId, option)
//     .then(votes => console.log("Результат через бэкенд:", votes))
//     .catch(console.error);