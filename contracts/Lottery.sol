// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import { AggregatorV3Interface } from "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";
import { Ownable } from "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is Ownable {
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING
    }

    LOTTERY_STATE public state;
    address payable[] public players;

    AggregatorV3Interface internal ethToUsdPriceFeed;
    uint256 internal usdEntranceFee;

    constructor(address _priceFeedAddress, uint256 _usdEntranceFee) {
        state = LOTTERY_STATE.CLOSED;
        ethToUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        usdEntranceFee = _usdEntranceFee * 10 ** 26; // usd * (wei / eth) * 10**8
    }

    function enter() public payable {
        require(state == LOTTERY_STATE.OPEN, "Lottery state must be OPEN!");
        require(msg.value >= getEntranceFee(), "Not enough ETH!");

        players.push(payable(msg.sender));
    }

    function getEntranceFee() public view returns (uint256) {
        (,int256 exchangeRate,,,) = ethToUsdPriceFeed.latestRoundData(); // (usd / eth) * 10**8
        uint256 entranceFee = usdEntranceFee / uint256(exchangeRate);
        return entranceFee;
    }

    function startLottery() public onlyOwner {
        require(state == LOTTERY_STATE.CLOSED, "Lottery state must be CLOSED!");
        state = LOTTERY_STATE.OPEN;
    }

    function endLottery() public {

    }
}
