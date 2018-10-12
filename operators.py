from datetime import date


class Operator(object):
    """ Stores details on an operator. """

    def __init__(self, id, first_name, family_name, drone_license, rescue_endorsement, operations=0,drone=None, dob=None):
        self.id = id
        self.first_name = first_name
        self.family_name = family_name
        if dob == None:
            dob = str(date.today())
        self.date_of_birth = dob
        self.drone_license = drone_license
        self.rescue_endorsement = rescue_endorsement
        self.operations = operations
        self.drone = drone


class OperatorAction(object):
    """ A pending action on the OperatorStore. """

    def __init__(self, operator, commit_action):
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

        self._commit_action(self.operator)
        self._committed = True


class OperatorStore(object):
    """ Stores the operators. """

    def __init__(self, conn):
        self._operators = {}
        self._last_id = 0
        self._conn = conn

    def update(self, operator):
        """ updates an operator from the store. """
        cursor = self._conn.cursor()
        if operator.first_name != "":
            query = 'UPDATE Operator SET FirstName = %s WHERE ID = %s'
            cursor.execute(query, (operator.first_name, operator.id,))
        if operator.family_name != "":
            query = 'UPDATE Operator SET LastName = %s WHERE ID = %s'
            cursor.execute(query, (operator.family_name, operator.id,))
        if operator.drone_license == 2:
            query = 'UPDATE Operator SET DroneLicense = 2 WHERE ID = %s'
            cursor.execute(query, (operator.id,))
        else:
            query = 'UPDATE Operator SET DroneLicense = 1 WHERE ID = %s'
            cursor.execute(query, (operator.id,))
        query = 'UPDATE Operator SET Operations = %s WHERE ID = %s'
        cursor.execute(query, (operator.operations, operator.id))
        if operator.rescue_endorsement == 1 or int(operator.operations) >= 5:
            query = 'UPDATE Operator SET RescueEndorsement = 1 WHERE ID = %s'
            cursor.execute(query, (operator.id,))
        else:
            query = 'UPDATE Operator SET RescueEndorsement = 0 WHERE ID = %s'
            cursor.execute(query, (operator.id,))
        cursor.close()
        self._conn.commit()

    def add(self, operator):
        """ Starts adding a new operator to the store. """
        cursor = self._conn.cursor()
        query = 'INSERT INTO Operator(ID, FirstName, LastName, DateOfBirth, DroneLicense, RescueEndorsement, Operations) VALUES (%s, %s, %s, %s, %s, %s, %s)'
        cursor.execute(query, (operator.id, operator.first_name, operator.family_name, operator.date_of_birth, operator.drone_license, operator.rescue_endorsement, operator.operations))
        cursor.close()
        self._conn.commit()
        '''   
        action = OperatorAction(operator, self._add)
        check_age = True
        if operator.first_name is None:
            action.add_message("First name is required")
        if operator.date_of_birth is None:
            action.add_message("Date of birth is required")
            check_age = False
        if operator.drone_license is None:
            action.add_message("Drone license is required")
        else:
            if check_age and operator.drone_license == 2:
                today = date.today()
                age = today.year - operator.date_of_birth.year - \
                    ((today.month, today.day) < (
                        operator.date_of_birth.month, operator.date_of_birth.day))
                if age < 20:
                    operator.drone_license = 1
                    action.add_message(
                        "Operator should be at least twenty to hold a class 2 license")
        if operator.rescue_endorsement and operator.operations < 5:
            action.add_message(
                "Operator must be involved in five prior rescues to hold a rescue endorsement")
            operator.rescue_endorsement = False
        elif operator.rescue_endorsement == False and operator.operations >= 5:
            operator.resuce_endorsement = True
        return action'''

    def _add(self, operator):
        """ Adds a new operator to the store. """
        if operator.id in self._operators:
            raise Exception('Operator already exists in store')
        else:
            self._last_id += 1
            operator.id = self._last_id
            self._operators[operator.id] = operator

    def remove(self, operator):
        """ Removes a operator from the store. """
        if not operator.id in self._operators:
            raise Exception('Operator does not exist in store')
        else:
            del self._operators[operator.id]

    def get(self, id):
        """ Retrieves a operator from the store by its ID or name. """
        cursor = self._conn.cursor()
        query = 'SELECT ID, FirstName, LastName, DroneLicense, RescueEndorsement, Operations FROM Operator WHERE ID = %s'
        cursor.execute(query, (id,))
        for(id, first_name, family_name, drone_license, rescue_endorsement, operations) in cursor:
            operator = Operator(id, first_name, family_name, drone_license, rescue_endorsement, operations)
            return operator
        '''if isinstance(id, basestring):
            for op in self._operators:
                if (op.first_name + ' ' + op.family_name) == id:
                    return op
            return None
        else:
            if not id in self._operators:
                return None
            else:
                return self._operators[id]'''

    def get_max(self):
        cursor = self._conn.cursor()
        query = 'SELECT ID FROM Operator ORDER BY ID DESC LIMIT 1'
        cursor.execute(query)
        for(id,) in cursor:
            self._last_id = int(id)
            return int(id)

    def list_all(self):
        """ Lists all the _operators in the system. """
        #for _operator in self._operators:
          #  yield _operator
        cursor = self._conn.cursor()
        query = 'SELECT Operator.ID, FirstName, LastName, DroneLicense, RescueEndorsement, Operations, Drone.ID, Drone.Name FROM Operator LEFT OUTER JOIN Drone ON Operator.ID = Drone.OperatorID ORDER BY Name'
        cursor.execute(query)
        for (id, first_name, family_name,drone_license,rescue_endorsement,operations,drone_id,drone_name) in cursor:
            if drone_id != None:
                operator = Operator(id, first_name, family_name,drone_license,rescue_endorsement,operations, str(drone_id) + " " + str(drone_name))
            else:
                operator = Operator(id, first_name, family_name,drone_license,rescue_endorsement,operations, None)
            yield operator
        cursor.close()  

    def save(self, operator):
        """ Saves the store to the database. """
        pass    # TODO: we don't have a database yet
