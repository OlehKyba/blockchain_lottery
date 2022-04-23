// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import { AggregatorV3Interface } from "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract Lottery {
    address payable[] internal players;
    AggregatorV3Interface internal ethToUsdPriceFeed;
    uint256 internal usdEntranceFee;

    constructor(address _priceFeedAddress, uint256 _usdEntranceFee) {
        ethToUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        usdEntranceFee = _usdEntranceFee * 10 ** 26; // usd * (wei / eth) * 10**8
    }

    function enter() public payable {
        players.push(payable(msg.sender));
    }

    function getEntranceFee() public view returns (uint256) {
        (,int256 exchangeRate,,,) = ethToUsdPriceFeed.latestRoundData(); // (usd / eth) * 10**8
        uint256 entranceFee = usdEntranceFee / uint256(exchangeRate);
        return entranceFee;
    }

    function startLottery() public {

    }

    function endLottery() public {

    }
}
