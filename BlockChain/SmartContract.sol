// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract Camera {
    address public manufacturer;

    mapping(string => bytes32) public modelKeys;

    constructor() {
        manufacturer = msg.sender; 
    }

    modifier onlyManufacturer() {
        require(msg.sender == manufacturer, "ACCESS DENIED");
        _;
    }
    function addModel(string memory _modelName, bytes32 _modelPublicKey) public onlyManufacturer {
        modelKeys[_modelName] = _modelPublicKey;
    }
    function getModelKey(string memory _modelName) public view returns (bytes32) {
        return modelKeys[_modelName];
    }
}

