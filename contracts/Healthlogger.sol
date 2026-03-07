// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

/*
    secureMedi Smart Contract

    Features:
    - Admin controlled patient registration
    - Doctor registration
    - Doctor access key generation
    - Emergency access (24 hrs)
    - Blockchain-based authentication
    - Access logging
    - Patient audit trail
*/

contract SecureMedi {

    /* ========================================================
                        STRUCTURES
    ======================================================== */

    struct AccessLog {
        address doctor;
        uint256 timestamp;
        bool emergency;
    }


    /* ========================================================
                        STATE VARIABLES
    ======================================================== */

    // Contract owner
    address public admin;

    // Registered doctors
    mapping(address => bool) public isDoctor;

    // Doctor -> Access Key
    mapping(address => bytes32) private accessKeys;

    // Doctor -> Emergency Expiry
    mapping(address => uint256) public emergencyAccess;

    // Patient ID -> Wallet
    mapping(string => address) private patientOwner;

    // Patient ID -> Access History
    mapping(string => AccessLog[]) private patientLogs;


    /* ========================================================
                        MODIFIERS
    ======================================================== */

    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin allowed");
        _;
    }

    modifier onlyDoctor() {
        require(isDoctor[msg.sender], "Not registered doctor");
        _;
    }


    /* ========================================================
                        CONSTRUCTOR
    ======================================================== */

    constructor() {
        admin = msg.sender;
    }


    /* ========================================================
                    DOCTOR MANAGEMENT
    ======================================================== */

    // Register doctor (Admin only)
    function registerDoctor(address doctor)
        public
        onlyAdmin
    {
        require(doctor != address(0), "Invalid address");

        isDoctor[doctor] = true;
    }


    /* ========================================================
                    PATIENT MANAGEMENT
    ======================================================== */

    // Register a patient (Admin only)
    function registerPatient(
        string memory patientId,
        address wallet
    )
        public
        onlyAdmin
    {
        require(wallet != address(0), "Invalid wallet");

        patientOwner[patientId] = wallet;
    }


    /* ========================================================
                    DOCTOR AUTHENTICATION
    ======================================================== */

    // Generate access key (Doctor only)
    function generateKey()
        public
        onlyDoctor
    {
        bytes32 key = keccak256(
            abi.encodePacked(
                msg.sender,
                block.timestamp
            )
        );

        accessKeys[msg.sender] = key;
    }


    // Get own key
    function getMyKey()
        public
        view
        returns (bytes32)
    {
        return accessKeys[msg.sender];
    }


    // Verify key
    function verifyKey(
        address user,
        bytes32 key
    )
        public
        view
        returns (bool)
    {
        return accessKeys[user] == key;
    }


    /* ========================================================
                    EMERGENCY ACCESS
    ======================================================== */

    // Generate emergency access (24 hours) (Doctor only)
    function generateEmergencyAccess()
        public
        onlyDoctor
    {
        emergencyAccess[msg.sender] =
            block.timestamp + 24 hours;
    }


    // Check emergency validity
    function hasEmergencyAccess(address user)
        public
        view
        returns (bool)
    {
        return emergencyAccess[user] > block.timestamp;
    }


    /* ========================================================
                    ACCESS LOGGING
    ======================================================== */

    // Log doctor access
    function logAccess(
        string memory patientId
    )
        public
        onlyDoctor
    {
        require(
            patientOwner[patientId] != address(0),
            "Patient not registered"
        );

        bool normal =
            accessKeys[msg.sender] != bytes32(0);

        bool emergency =
            emergencyAccess[msg.sender] > block.timestamp;

        require(
            normal || emergency,
            "No valid access"
        );

        patientLogs[patientId].push(
            AccessLog(
                msg.sender,
                block.timestamp,
                emergency
            )
        );
    }


    // Get access logs
    function getAccessLogs(
        string memory patientId
    )
        public
        view
        returns (
            address[] memory,
            uint256[] memory,
            bool[] memory
        )
    {
        require(
            patientOwner[patientId] != address(0),
            "Invalid patient"
        );

        uint256 len = patientLogs[patientId].length;

        address[] memory doctors =
            new address[](len);

        uint256[] memory times =
            new uint256[](len);

        bool[] memory emergencies =
            new bool[](len);

        for (uint256 i = 0; i < len; i++) {

            doctors[i] =
                patientLogs[patientId][i].doctor;

            times[i] =
                patientLogs[patientId][i].timestamp;

            emergencies[i] =
                patientLogs[patientId][i].emergency;
        }

        return (doctors, times, emergencies);
    }


    /* ========================================================
                    HELPERS
    ======================================================== */

    // Check if patient exists
    function isPatientRegistered(
        string memory patientId
    )
        public
        view
        returns (bool)
    {
        return patientOwner[patientId] != address(0);
    }


    // Get admin address
    function getAdmin()
        public
        view
        returns (address)
    {
        return admin;
    }
}
