UPDATE Operator
SET Operations = 6, DroneLicense = 2, RescueEndorsement = TRUE
WHERE FirstName = 'Bob';

UPDATE Operator
SET RescueEndorsement = TRUE
WHERE Operations >= 5;

UPDATE Drone
SET OperatorID = 3, MapID = 2
WHERE Name = 'Drone2';



