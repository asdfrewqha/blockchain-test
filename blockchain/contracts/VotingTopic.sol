// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/metatx/ERC2771Context.sol";

contract VotingManager is ERC2771Context {
    mapping(string => mapping(string => uint256)) private votes;
    event Voted(address indexed voter, string topicId, string option);
    mapping(string => mapping(address => bool)) private hasVoted;

    constructor(address trustedForwarder) ERC2771Context(trustedForwarder) {}

    function vote(string memory topicId, string memory option) external {
        address voter = _msgSender();
        require(!hasVoted[topicId][voter], "Already voted for this topic");

        votes[topicId][option]++;
        emit Voted(voter, topicId, option); 
        hasVoted[topicId][voter] = true;
    }

    function getVotes(string memory topicId, string memory option) external view returns (uint256) {
        return votes[topicId][option];
    }
}