// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import { AggregatorV3Interface } from "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract Lottery {
    address payable[] internal players;
    AggregatorV3Interface internal ethToUsdPriceFeed;
    uint256 internal usdEntranceFee;

    constructor(address _priceFeedAddress, uint256 _usdEntranceFee) {
        ethToUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        usdEntranceFee = _usdEntranceFee * 10 ** 18; // $ * (wei/eth)
    }

    function enter() public payable {
        players.push(payable(msg.sender));
    }

    function getEntranceFee() public view returns (uint256) {
        (,int256 exchangeRate,,,) = ethToUsdPriceFeed.latestRoundData();
        uint256 adjustedExchangeRate = uint256(exchangeRate) * 10 ** 10; // eth/$ 18 decimals
        uint256 entranceFee = usdEntranceFee / adjustedExchangeRate;
        return entranceFee;
    }

    function startLottery() public {

    }

    function endLottery() public {

    }
}
