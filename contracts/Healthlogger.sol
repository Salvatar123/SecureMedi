// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract HealthLogger {

    address public admin;

    constructor() {
        admin = msg.sender;
    }

    struct Record {
        string patientId;
        string vitals;
        string status;
        uint timestamp;
    }

    Record[] public records;

    mapping(address => bool) public authorizedDevices;

    modifier onlyAdmin() {
        require(msg.sender == admin, "Not admin");
        _;
    }

    modifier onlyDevice() {
        require(authorizedDevices[msg.sender], "Not authorized device");
        _;
    }

    function addDevice(address _device) public onlyAdmin {
        authorizedDevices[_device] = true;
    }

    function addRecord(
        string memory _patientId,
        string memory _vitals,
        string memory _status
    ) public onlyDevice {

        records.push(Record(
            _patientId,
            _vitals,
            _status,
            block.timestamp
        ));
    }

    function getCount() public view returns(uint) {
        return records.length;
    }
}
