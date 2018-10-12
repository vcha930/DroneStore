from operators import Operator, OperatorAction, OperatorStore

class Drone(object):
    """ Stores details on a drone. """

    def __init__(self, id, name, class_type=1, rescue=False, operator=None, map=None, x=None, y=None):
        self.id = id
        self.name = name
        self.class_type = class_type
        self.rescue = rescue
        self.operator = operator
        self.map = map
        self.x = x
        self.y = y


class DroneAction(object):
    """ A pending action on the DroneStore. """

    def __init__(self, drone, operator, commit_action):
        self.drone = drone
        self.operator = operator
        self.messages = []
        self._commit_action = commit_action
        self._committed = False

    def add_message(self, message):
        """ Adds a message to the action. """
        self.messages.append(message)

    def is_valid(self):
        """ Returns True if the action is valid, False otherwise. """
        return len(self.messages) == 0

    def commit(self):
        """ Commits (performs) this action. """
        if self._committed:
            raise Exception("Action has already been committed")

        self._commit_action(self.drone, self.operator)
        self._committed = True


class DroneStore(object):
    """ DroneStore stores all the drones for DALSys. """

    def __init__(self, conn):
        self._drones = {}
        self._last_id = 0
        self._conn = conn

    def update(self, drone):
        """ updates a drone from the store. """
        cursor = self._conn.cursor()
        query = 'SELECT COUNT(*) FROM Drone WHERE ID = %s'
        cursor.execute(query, (drone.id,))
        for(num,) in cursor:
            if num != 1:
                print("!! Unknown drone !!")
            else:
                if drone.rescue == 1:
                    query = 'UPDATE Drone SET Rescue = 1 WHERE ID = %s'
                    cursor.execute(query, (drone.id,))
                    print("- set rescue to " + 'Yes')
                else:
                    query = 'UPDATE Drone SET Rescue = 0 WHERE ID = %s'
                    cursor.execute(query, (drone.id,))
                if drone.class_type != 0:
                    query = 'UPDATE Drone SET ClassType = %s WHERE ID = %s'
                    cursor.execute(query, (drone.class_type, drone.id,))
                    print("- set class to " + str(drone.class_type))
                if drone.name != "":
                    query = 'UPDATE Drone SET Name = %s WHERE ID = %s'
                    cursor.execute(query, (drone.name, drone.id,))
                    print("- set name to " + str(drone.name))
        cursor.close()
        self._conn.commit()
        
    def add(self, drone):
        """ Adds a new drone to the store. """
        if drone.id in self._drones:
            raise Exception('Drone already exists in store')
        else:
            self._last_id += 1
            drone.id = self._last_id
            self._drones[drone.id] = drone
            cursor = self._conn.cursor()
            query = 'INSERT INTO Drone(ID, Name, ClassType, Rescue) VALUES (%s, %s, %s, %s)'
            cursor.execute(query, (drone.id, drone.name, drone.class_type, drone.rescue))
            cursor.close()
            if drone.rescue == 1:
                print('Added rescue drone with ID ' + str(drone.id).zfill(4))
            else:
                print('Added drone with ID ' + str(drone.id).zfill(4))
            self._conn.commit()

    def remove(self, drone):
        """ Removes a drone from the store. """
        '''if not drone.id in self._drones:
            raise Exception('Drone does not exist in store')
        else:
            del self._drones[drone.id]'''
        cursor = self._conn.cursor()
        query = 'DELETE FROM Drone WHERE ID = %s;'
        cursor.execute(query, (drone.id,))
        print("Drone removed")
        self._conn.commit()

    def get(self, id):
        """ Retrieves a drone from the store by its ID. """
        '''if not id in self._drones:
            return None
        else:
            return self._drones[id]'''
        cursor = self._conn.cursor()
        
        query = 'SELECT Drone.ID, Name, ClassType, Rescue, Operator.FirstName, Operator.LastName, Map.Filename FROM Drone LEFT OUTER JOIN Operator ON Drone.OperatorID = Operator.ID LEFT OUTER JOIN Map ON Drone.MapID = Map.ID WHERE Drone.ID = %s'
        cursor.execute(query, (id,))
        for (id, name, class_type, rescue, fname, lname, mapname) in cursor:
            if fname != None and mapname != None:
                drone = Drone(id, name, class_type, rescue, str(fname) + ' ' + str(lname), str(mapname))
            elif fname != None:
                drone = Drone(id, name, class_type, rescue, str(fname) + ' ' + str(lname), None)
            elif mapname != None:
                drone = Drone(id, name, class_type, rescue, None, str(mapname))
            else:
                drone = Drone(id, name, class_type, rescue, None, None)
            return drone


    def get_max(self):
        cursor = self._conn.cursor()
        query = 'SELECT ID FROM Drone ORDER BY ID DESC LIMIT 1'
        cursor.execute(query)
        for(id,) in cursor:
            self._last_id = int(id)
            return int(id)

    def list_all(self, filter):
        """ Lists all the drones in the system. """
        cursor = self._conn.cursor()
        count = 0
        if len(filter) == 0:
            query = 'SELECT Drone.ID, Name, ClassType, Rescue, Operator.FirstName, Operator.LastName, Map.Filename FROM Drone LEFT OUTER JOIN Operator ON Drone.OperatorID = Operator.ID LEFT OUTER JOIN Map ON Drone.MapID = Map.ID ORDER BY Name'
            cursor.execute(query)
            for (id, name, class_type, rescue, fname, lname, mapname) in cursor:
                if fname != None and mapname != None:
                    drone = Drone(id, name, class_type, rescue, str(fname) + ' ' + str(lname), str(mapname))
                elif fname != None:
                    drone = Drone(id, name, class_type, rescue, str(fname) + ' ' + str(lname), None)
                elif mapname != None:
                    drone = Drone(id, name, class_type, rescue, None, str(mapname))
                else:
                    drone = Drone(id, name, class_type, rescue, None, None)                    
                yield drone
                count+=1
            if count ==0:
                print("!! There are no drones for this criteria !!")
            cursor.close()
        elif len(filter) == 1:
            if filter[0] == '-class=1': 
                query = 'SELECT Drone.ID, Name, ClassType, Rescue, Operator.FirstName, Operator.LastName FROM Drone LEFT OUTER JOIN Operator ON Drone.OperatorID = Operator.ID WHERE ClassType = 1 ORDER BY Name'
                cursor.execute(query)
                for (id, name, class_type, rescue, fname, lname) in cursor:
                    if fname or lname != None:
                        drone = Drone(id, name, class_type, rescue, str(fname) + ' ' + str(lname))
                    else:
                        drone = Drone(id, name, class_type, rescue, None)                    
                    yield drone
                    count+=1
                if count ==0:
                    print("!! There are no drones for this criteria !!")
                cursor.close()
            elif filter[0] == '-class=2': 
                query = 'SELECT Drone.ID, Name, ClassType, Rescue, Operator.FirstName, Operator.LastName FROM Drone LEFT OUTER JOIN Operator ON Drone.OperatorID = Operator.ID WHERE ClassType = 1 ORDER BY Name'
                cursor.execute(query)
                for (id, name, class_type, rescue, fname, lname) in cursor:
                    if fname or lname != None:
                        drone = Drone(id, name, class_type, rescue, str(fname) + ' ' + str(lname))
                    else:
                        drone = Drone(id, name, class_type, rescue, None)
                    yield drone
                    count+=1
                if count ==0:
                    print("!! There are no drones for this criteria !!")
                cursor.close()
            elif filter[0] == '-rescue': 
                query = 'SELECT Drone.ID, Name, ClassType, Rescue, Operator.FirstName, Operator.LastName FROM Drone LEFT OUTER JOIN Operator ON Drone.OperatorID = Operator.ID WHERE Rescue = 1 ORDER BY Name'
                cursor.execute(query)
                for (id, name, class_type, rescue, fname, lname) in cursor:
                    if fname or lname != None:
                        drone = Drone(id, name, class_type, rescue, str(fname) + ' ' + str(lname))
                    else:
                        drone = Drone(id, name, class_type, rescue, None)
                    yield drone
                    count+=1
                if count ==0:
                    print("!! There are no drones for this criteria !!")  
                cursor.close()
        elif len(filter) == 2:
            if filter[0] == '-class=1' : 
                query = 'SELECT Drone.ID, Name, ClassType, Rescue, Operator.FirstName, Operator.LastName FROM Drone LEFT OUTER JOIN Operator ON Drone.OperatorID = Operator.ID WHERE ClassType = 1 AND Rescue = 1 ORDER BY Name'
                cursor.execute(query)
                for (id, name, class_type, rescue, fname, lname) in cursor:
                    if fname or lname != None:
                        drone = Drone(id, name, class_type, rescue, str(fname) + ' ' + str(lname))
                    else:
                        drone = Drone(id, name, class_type, rescue, None)
                    yield drone
                    count+=1
                if count ==0:
                    print("!! There are no drones for this criteria !!")
                cursor.close()
            if filter[0] == '-class=2' : 
                query = 'SELECT Drone.ID, Name, ClassType, Rescue, Operator.FirstName, Operator.LastName FROM Drone LEFT OUTER JOIN Operator ON Drone.OperatorID = Operator.ID WHERE ClassType = 2 AND Rescue = 1 ORDER BY Name'
                cursor.execute(query)
                for (id, name, class_type, rescue, fname, lname) in cursor:
                    if fname or lname != None:
                        drone = Drone(id, name, class_type, rescue, str(fname) + ' ' + str(lname))
                    else:
                        drone = Drone(id, name, class_type, rescue, None)
                    yield drone
                    count+=1
                if count ==0:
                    print("!! There are no drones for this criteria !!")
                cursor.close()

            
    def allocate(self, drone, fname, lname):
        """ Starts the allocation of a drone to an operator. """
        fname = fname.strip("'")
        lname = lname.strip("'")
        cursor = self._conn.cursor()
        query = 'SELECT ID, FirstName, LastName, DroneLicense, RescueEndorsement FROM Operator WHERE FirstName = %s AND LastName = %s'
        cursor.execute(query, (fname, lname))
        for(id, fname, lname, license, rescue) in cursor:
            operator = Operator(id, fname, lname, license, rescue)
            try:
                query = 'UPDATE Drone SET OperatorID = %s WHERE ID = %s'
                cursor.execute(query, (operator.id, drone.id))
            except:
                query = 'SELECT Operator.FirstName, Operator.LastName FROM Operator LEFT OUTER JOIN Drone ON Operator.ID = Drone.OperatorID WHERE Operator.ID = Drone.OperatorID AND Drone.ID = %s'
                cursor.execute(query, (drone.id,))
                for (fname, lname) in cursor:
                    print("Validation errors :\n- drone already allocated to " + str(fname) + " " + str(lname))
                    overwrite = raw_input("Do you want to continue [ Y / n ]? ")
                    if overwrite == 'Y' or 'y':
                        query = 'UPDATE Drone SET OperatorID = NULL WHERE ID = %s'
                        cursor.execute(query, (drone.id,))
                        query = 'UPDATE Drone SET OperatorID = %s WHERE ID = %s'
                        cursor.execute(query, (operator.id, drone.id))
            #query = 'UPDATE Drone SET OperatorID = %s FROM Drone LEFT OUTER JOIN Operator ON Drone.OperatorID = Operator.ID WHERE Drone.ID = %s'
            #cursor.execute(query, (operator.id, int(drone.id)))
            #query = 'UPDATE Operator SET DroneID = %s FROM Operator INNER JOIN Drone ON Operator.ID = Drone.OperatorID WHERE Operator.ID = %s'
            #cursor.execute(query, (drone.id, operator.id))

        
        '''action = DroneAction(drone, operator, self._allocate)
        if operator.drone is not None:
            action.add_message("Operator can only control one drone")
        if operator.drone_license != drone.class_type:
            action.add_message("Operator does not have correct drone license")
        if drone.rescue and not operator.rescue_endorsement:
            action.add_message("Operator does not have rescue endorsement")
        return action

    def _allocate(self, drone, operator):
        """ Performs the actual allocation of the operator to the drone. """
        operator.drone = drone
        drone.operator = operator
        self.save(drone)'''

    def save(self, drone):
        """ Saves the drone to the database. """
        pass    # TODO: we don't have a database yet

    



    
