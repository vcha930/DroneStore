INSERT INTO Operator(ID, FirstName, LastName, DateOfBirth, DroneLicense, RescueEndorsement, Operations)
	VALUES
	(1, 'John', 'Smith', '2005-05-12', 0, FALSE, 0),
	(2, 'Bob', 'Brown', '1980-05-12', 1, FALSE, 1),
	(3, 'Kate', 'Brown', '1991-05-12', 2, FALSE, 5),
	(4, 'Vince', 'Chan', '1990-05-12', 2, TRUE, 5);
	
INSERT INTO Map(ID, Filename)
	VALUES
	(1, 'map_abel_tasman_3.gif'),
	(2, 'map_ruatiti.gif');
	
INSERT INTO Drone(ID, Name, ClassType, Rescue, OperatorID, MapID)
	VALUES
	(1, 'Drone1', 1, FALSE, NULL, NULL),
	(2, 'Drone2', 2, FALSE, NULL, NULL),
	(3, 'Drone3', 2, TRUE, NULL, NULL),
	(4, 'Drone4', 1, FALSE, 1, 1),
	(5, 'Drone5', 1, FALSE, 2, 1);