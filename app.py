import mysql.connector
import Tkinter as tk
import ttk

from drones import Drone, DroneStore
from operators import Operator, OperatorStore
from trackingsystem import TrackingSystem
from maps import Map, MapStore
from Tkinter import *
#from PIL import Image



class Application(object):
    """ Main application view - displays the menu. """

    def __init__(self, conn):
        # Initialise the stores
        self.conn = conn
        self.drones = DroneStore(self.conn)
        self.operators = OperatorStore(self.conn)
        self.maps = MapStore(self.conn)
        self.tracking = TrackingSystem()

        # Initialise the GUI window
        self.root = tk.Tk()
        self.root.title('Drone Allocation and Localisation')
        frame = tk.Frame(self.root)
        frame.pack(padx=10, pady=10)

        # Add in the buttons
        drone_button = tk.Button(
            frame, text="View Drones", command=self.view_drones, width=40, padx=5, pady=5)
        drone_button.pack(side=tk.TOP)
        operator_button = tk.Button(
            frame, text="View Operators", command=self.view_operators, width=40, padx=5, pady=5)
        operator_button.pack(side=tk.TOP)
        map_button = tk.Button(
            frame, text="View Maps", command=self.view_maps, width=40, padx=5, pady=5)
        map_button.pack(side=tk.TOP)
        exit_button = tk.Button(frame, text="Exit System",
                                command=quit, width=40, padx=5, pady=5)
        exit_button.pack(side=tk.TOP)

    def main_loop(self):
        """ Main execution loop - start Tkinter. """
        self.root.mainloop()

    def view_operators(self):
        """ Display the operators. """
        # Instantiate the operators window
        # Display the window and wait
        wnd = OperatorListWindow(self)
        self.root.wait_window(wnd.root)

    def view_drones(self):
        """ Display the drones. """
        wnd = DroneListWindow(self)
        self.root.wait_window(wnd.root)

    def view_maps(self):
        """ Display the drones. """
        wnd = MapWindow(self)
        self.root.wait_window(wnd.root)


class ListWindow(object):
    """ Base list window. """

    def __init__(self, parent, title):
        # Add a variable to hold the stores
        self.drones = parent.drones
        self.operators = parent.operators
        self.maps = parent.maps
        self.tracking = parent.tracking

        # Initialise the new top-level window (modal dialog)
        self._parent = parent.root
        self.root = tk.Toplevel(parent.root)
        self.root.title(title)
        self.root.transient(parent.root)
        self.root.grab_set()

        # Initialise the top level frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH,
                        expand=tk.Y, padx=10, pady=10)

    def add_list(self, columns, edit_action):
        # Add the list
        self.tree = ttk.Treeview(self.frame, columns=columns, show='headings')
        if "operator" in str(edit_action):
            self.tree["displaycolumns"]=('name', 'class', 'rescue', 'operations', 'drone')
        for col in columns:
            self.tree.heading(col, text=col.title())
        ysb = ttk.Scrollbar(self.frame, orient=tk.VERTICAL,
                            command=self.tree.yview)
        xsb = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL,
                            command=self.tree.xview)
        self.tree['yscroll'] = ysb.set
        self.tree['xscroll'] = xsb.set
        self.tree.bind("<Double-1>", edit_action)

        # Add tree and scrollbars to frame
        self.tree.grid(in_=self.frame, row=0, column=0, sticky=tk.NSEW)
        ysb.grid(in_=self.frame, row=0, column=1, sticky=tk.NS)
        xsb.grid(in_=self.frame, row=1, column=0, sticky=tk.EW)

        # Set frame resize priorities
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

    def close(self):
        """ Closes the list window. """
        self.root.destroy()


class DroneListWindow(ListWindow):
    """ Window to display a list of drones. """

    def __init__(self, parent):
        super(DroneListWindow, self).__init__(parent, 'Drones')

        # Add the list and fill it with data
        columns = ('id', 'name', 'class', 'rescue', 'operator')
        self.add_list(columns, self.edit_drone)
        self.populate_data()

        # Add the command buttons
        add_button = tk.Button(self.frame, text="Add Drone",
                               command=self.add_drone, width=20, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=2, column=0, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=3, column=0, sticky=tk.E)

    def populate_data(self):
        """ Populates the data in the view. """
        'Load data'
        for i in self.tree.get_children():
            self.tree.delete(i)
        filter=[]
        last_id = self.drones.get_max()
        for drone in self.drones.list_all(filter):
            if drone.class_type == 1:
                drone.class_type = 'One'
            else:
                drone.class_type = 'Two'
            if drone.rescue == 1:
                drone.rescue = 'Yes'
            else:
                drone.rescue = 'No'
            if drone.operator == None:
                drone.operator = '<none>'
                #for child in self.tree.get_children():
                #print(self.tree.item(child)["values"])
            self.tree.insert('', 'end', values=(str(drone.id).zfill(4),str(drone.name) , drone.class_type, drone.rescue, str(drone.operator)))

            
    def add_drone(self):
        """ Starts a new drone and displays it in the list. """
        # Start a new drone instance
        'TODO: Start a new drone'
        last_id = self.drones.get_max()+1
        name = 'Drone' + str(last_id)
        drone = Drone(last_id+1, name, 1, 0)

        # Display the drone
        self.view_drone(drone, self._save_new_drone)

    def _save_new_drone(self, drone):
        """ Saves the drone in the store and updates the list. """
        self.drones.add(drone)
        self.populate_data()

    def edit_drone(self, event):
        """ Retrieves the drone and shows it in the editor. """
        # Retrieve the identifer of the drone
        item = self.tree.item(self.tree.focus())
        item_id = item['values'][0]

        # Load the drone from the store
        'TODO: Load drone with ID %04d' % (item_id)
        drone = self.drones.get(item_id)

        # Display the drone
        self.view_drone(drone, self._update_drone)

    def _update_drone(self, drone):
        """ Saves the new details of the drone. """
        self.drones.update(drone)
        self.drones.save(drone)
        self.populate_data()

    def view_drone(self, drone, save_action):
        """ Displays the drone editor. """
        wnd = DroneEditorWindow(self, drone, save_action)
        self.root.wait_window(wnd.root)

class OperatorListWindow(ListWindow):
    """ Window to display a list of operators. """

    def __init__(self, parent):
        super(OperatorListWindow, self).__init__(parent, 'Operators')

        # Add the list and fill it with data
        columns = ('id', 'name', 'class', 'rescue', 'operations', 'drone')
        self.add_list(columns, self.edit_operator)
        self.populate_data()

        # Add the command buttons
        add_button = tk.Button(self.frame, text="Add Operator",
                               command=self.add_operator, width=20, padx=5, pady=5)
        add_button.grid(in_=self.frame, row=2, column=0, sticky=tk.E)
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=3, column=0, sticky=tk.E)

    def populate_data(self):
        """ Populates the data in the view. """
        'Load data'
        for i in self.tree.get_children():
            self.tree.delete(i)
        for operator in self.operators.list_all():
            if operator.drone_license == 2:
                operator.drone_license = 'Two'
            else:
                operator.drone_license = 'One'
            if operator.rescue_endorsement == 1:
                operator.rescue_endorsement = 'Yes'
            else:
                operator.rescue_endorsement = 'No'
            if operator.drone == None:
                operator.drone = '<None>'
            self.tree.insert('', 'end', values=(str(operator.id).zfill(4) ,str(operator.first_name) + " " + str(operator.family_name) , operator.drone_license, operator.rescue_endorsement, operator.operations, operator.drone))

            
    def add_operator(self):
        """ Starts a new drone and displays it in the list. """
        # Start a new drone instance
        'TODO: Start a new drone'
        last_id = self.operators.get_max()
        fname = 'Operator'
        lname = str(last_id)
        operator = Operator(last_id+1, fname, lname, 1, 0)

        # Display the drone
        self.view_operator(operator, self._save_new_operator)

    def _save_new_operator(self, operator):
        """ Saves the drone in the store and updates the list. """
        self.operators.add(operator)
        self.populate_data()

    def edit_operator(self, event):
        """ Retrieves the drone and shows it in the editor. """
        # Retrieve the identifer of the drone
        item = self.tree.item(self.tree.focus())
        item_id = item['values'][0]

        # Load the drone from the store
        #'TODO: Load drone with ID %04d' % (item_id)
        operator = self.operators.get(item_id)

        # Display the drone
        self.view_operator(operator, self._update_operator)

    def _update_operator(self, operator):
        """ Saves the new details of the drone. """
        self.operators.update(operator)
        self.operators.save(operator)
        self.populate_data()

    def view_operator(self, operator, save_action):
        """ Displays the drone editor. """
        wnd = OperatorEditorWindow(self, operator, save_action)
        self.root.wait_window(wnd.root)

class MapWindow(object):
    """ Window to display a list of drones. """

    def __init__(self, parent):
        self.maps = parent.maps
        self.drones = parent.drones
        self.tracking = parent.tracking
        last_drone = self.drones.get_max()
        i=0
        #while i < last_drone:
         #   self.drone = self.drones.get(i)
          #  print(self.drone)
        self.maps_list = self.populate_data()
        filepaths = []
        for map in self.maps_list:
            filepaths.append(map.filepath)
        # Initialise the new top-level window (modal dialog)
        self._parent = parent.root
        self.root = tk.Toplevel(parent.root)
        self.root.title('Maps')
        self.root.transient(parent.root)
        self.root.grab_set()
        # Initialise the top level frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.Y, padx=10, pady=10)
        self.map_label = tk.Label(self.frame, text="Map :", padx=5, pady=5)
        self.map_label.grid(in_=self.frame, row=0, column=0, sticky=tk.W)
        self.map_dropdown = ttk.Combobox(self.frame, width=80)
        self.map_dropdown['values'] = (filepaths)
        self.map_dropdown.current(0)
        self.map_dropdown.grid(in_=self.frame, row=0, column=1, sticky=tk.W)
        #im = Image.open(filepaths[0])
        #width, height = im.size
        #print(width,height)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        xscrollbar = Scrollbar(self.frame, orient=HORIZONTAL)
        xscrollbar.grid(row=2, column=1, sticky=E+W)
        yscrollbar = Scrollbar(self.frame)
        yscrollbar.grid(row=1, column=2, sticky=N+S)
        self.canvas = tk.Canvas(self.frame, bd=0, xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set, width=600, height=350)
        self.canvas.grid(row=1, column=1)
        self.img = tk.PhotoImage(file=filepaths[0])
        self.canvas.create_image(600,350,image=self.img)
        xscrollbar.config(command=self.canvas.xview)
        yscrollbar.config(command=self.canvas.yview)
        self.canvas.config(scrollregion=self.canvas.bbox(ALL))
        self.map_dropdown.bind("<<ComboboxSelected>>", self.map_selection)
        
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=20, padx=5, pady=5)
        exit_button.grid(in_=self.frame, row=3, column=1, sticky=tk.E)

    def map_selection(self,event):
        selected=self.map_dropdown.get()
        self.img = tk.PhotoImage(file=selected)
        self.canvas.create_image(600,350,image=self.img)
        #im = Image.open(selected)
        #width, height = im.size
        #print(width,height)

    def close(self):
        """ Closes the editor window. """
        self.root.destroy()

    def populate_data(self):
        """ Populates the data in the view. """
        'Load data'
        self.maps_list = []
        for map in self.maps.list_all():
            self.maps_list.append(map)
        return self.maps_list


class EditorWindow(object):
    """ Base editor window. """

    def __init__(self, parent, title, save_action):
        # Initialise the new top-level window (modal dialog)
        self._parent = parent.root
        self.root = tk.Toplevel(parent.root)
        self.root.title(title)
        self.root.transient(parent.root)
        self.root.grab_set()
        self.tracking = parent.tracking

        # Initialise the top level frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(side=tk.TOP, fill=tk.BOTH,
                        expand=tk.Y, padx=10, pady=10)

        # Add the editor widgets
        name_label = tk.Label(self.frame, text="Name").grid(row=0, column=0)
        last_row = self.add_editor_widgets()

        # Add the command buttons
        add_button = tk.Button(self.frame, text="Save",
                               command=save_action, width=8)
        add_button.grid(in_=self.frame, row=last_row + 1, column=1, sticky=tk.E, padx=2, pady=2)
        exit_button = tk.Button(self.frame, text="Close",
                                command=self.close, width=8)
        exit_button.grid(in_=self.frame, row=last_row + 2, column=1, sticky=tk.E, padx=2, pady=2)

    def add_editor_widgets(self):
        """ Adds the editor widgets to the frame - this needs to be overriden in inherited classes. 
        This function should return the row number of the last row added - EditorWindow uses this
        to correctly display the buttons. """
        return -1

    def close(self):
        """ Closes the editor window. """
        self.root.destroy()

class DroneEditorWindow(EditorWindow):
    """ Editor window for drones. """

    def __init__(self, parent, drone, save_action):
        # TODO: Add either the drone name or <new> in the window title, depending on whether this is a new
        # drone or not
        self._drone = drone
        #link operator to drone
        #print(self._drone.map)
        self.location = parent.tracking.retrieve(self._drone.map, self._drone.id)
        if self.location.is_valid():
            x,y,z = self.location.position()
            self._drone.x = x
            self._drone.y = y
        self._save_action = save_action
        super(DroneEditorWindow, self).__init__(parent, 'Drone: ', self.save_drone)
        
        # TODO: Load drone details

    def add_editor_widgets(self):
        """ Adds the widgets for editing a drone. """
        'TODO: Create widgets and populate them with data'
        self.name_label = tk.Label(self.frame, text="Name :    ", padx=5, pady=5)
        self.name_label.grid(in_=self.frame, row=0, column=0, sticky=tk.W)
        self.name_entrybox = tk.Entry(self.frame, width=30)
        self.name_entrybox.grid(in_=self.frame, row=0, column=1, sticky=tk.W)
        self.class_label = tk.Label(self.frame, text="Drone Class :", padx=5, pady=5)
        self.class_label.grid(in_=self.frame, row=1, column=0, sticky=tk.W)
        self.class_dropdown = ttk.Combobox(self.frame, width=8)
        self.class_dropdown['values'] = ('One', 'Two')
        self.class_dropdown.grid(in_=self.frame, row=1, column=1, sticky=tk.W)
        self.rescue_label = tk.Label(self.frame, text="Rescue Drone :", padx=5, pady=5)
        self.rescue_label.grid(in_=self.frame, row=2, column=0, sticky=tk.W)
        self.rescue_dropdown = ttk.Combobox(self.frame, width=8)
        self.rescue_dropdown['values'] = ('Yes', 'No')
        self.rescue_dropdown.grid(in_=self.frame, row=2, column=1, sticky=tk.W)
        self.location_label = tk.Label(self.frame, text="Location : ", padx=5, pady=5)
        self.location_label.grid(in_=self.frame, row=3, column=0, sticky=tk.W)
        self.location_entrybox = tk.Entry(self.frame, width=20)
        self.location_entrybox.grid(in_=self.frame, row=3, column=1, sticky=tk.W)
        if self.location.is_valid():
            self.location_entrybox.insert('end', '(' + str(self._drone.x) + ', ' + str(self._drone.y) + ')')
        else:
            self.location_entrybox.insert('end', 'n/a')
        self.location_entrybox.config(state='readonly')
        if "update" in str(self._save_action):
            self.name_entrybox.insert('end', str(self._drone.name))
            if self._drone.class_type == 2:
                self.class_dropdown.current(1)
            else:
                self.class_dropdown.current(0)
            if self._drone.rescue == 1:
                self.rescue_dropdown.current(0)
            else:
                self.rescue_dropdown.current(1)
        elif "save" in str(self._save_action):
            self.name_entrybox.insert('end', 'Enter name here')
            self.class_dropdown.current(0)
            self.rescue_dropdown.current(1)
        return 3

    def save_drone(self):
        """ Updates the drone details and calls the save action. """
        'TODO: Update the drone from the widgets'
        if self.name_entrybox.get() != '':
            self._drone.name = self.name_entrybox.get()
        if self.class_dropdown.get() =='One':
            self._drone.class_type = 1
        else:
            self._drone.class_type = 2
        if self.rescue_dropdown.get() == 'No':
            self._drone.rescue = 0
        else:
            self._drone.rescue = 1
        self._save_action(self._drone)

class OperatorEditorWindow(EditorWindow):
    """ Editor window for drones. """

    def __init__(self, parent, operator, save_action):
        self._operator = operator
        #print(self._operator.operations)
        self._save_action = save_action
        super(OperatorEditorWindow, self).__init__(parent, 'Operator: ', self.save_operator)


    def add_editor_widgets(self):
        """ Adds the widgets for editing a drone. """
        'TODO: Create widgets and populate them with data'
        self.fname_label = tk.Label(self.frame, text="First Name :    ", padx=5, pady=5)
        self.fname_label.grid(in_=self.frame, row=0, column=0, sticky=tk.W)
        self.fname_entrybox = tk.Entry(self.frame, width=30)
        self.fname_entrybox.grid(in_=self.frame, row=0, column=1, sticky=tk.W)
        self.lname_label = tk.Label(self.frame, text="Family Name :    ", padx=5, pady=5)
        self.lname_label.grid(in_=self.frame, row=1, column=0, sticky=tk.W)
        self.lname_entrybox = tk.Entry(self.frame, width=30)
        self.lname_entrybox.grid(in_=self.frame, row=1, column=1, sticky=tk.W)
        self.class_label = tk.Label(self.frame, text="Drone License :", padx=5, pady=5)
        self.class_label.grid(in_=self.frame, row=2, column=0, sticky=tk.W)
        self.class_dropdown = ttk.Combobox(self.frame, width=8)
        self.class_dropdown['values'] = ('One', 'Two')
        self.class_dropdown.grid(in_=self.frame, row=2, column=1, sticky=tk.W)
        self.rescue_label = tk.Label(self.frame, text="Rescue Endrosement :", padx=5, pady=5)
        self.rescue_label.grid(in_=self.frame, row=3, column=0, sticky=tk.W)
        self.rescue_dropdown = ttk.Combobox(self.frame, width=8)
        self.rescue_dropdown['values'] = ('Yes', 'No')
        self.rescue_dropdown.grid(in_=self.frame, row=3, column=1, sticky=tk.W)
        self.operations = tk.Label(self.frame, text="Number of Operations :", padx=5, pady=5)
        self.operations.grid(in_=self.frame, row=4, column=0, sticky=tk.W)
        self.operations_spinbox = tk.Spinbox(self.frame, from_=0, to=100, width=9)
        self.operations_spinbox.grid(in_=self.frame, row=4, column=1, sticky=tk.W)
        if "update" in str(self._save_action):
            self.fname_entrybox.insert('end', str(self._operator.first_name))
            self.lname_entrybox.insert('end', str(self._operator.family_name))
            if self._operator.drone_license == 2:
                self.class_dropdown.current(1)
            else:
                self.class_dropdown.current(0)
            if self._operator.rescue_endorsement == 1:
                self.rescue_dropdown.current(0)
            else:
                self.rescue_dropdown.current(1)
            self.operations_spinbox.delete(0,"end")
            self.operations_spinbox.insert(0,self._operator.operations)
        elif "save" in str(self._save_action):
            self.fname_entrybox.insert('end', 'Enter first name here')
            self.lname_entrybox.insert('end', 'Enter last name here')
            self.class_dropdown.current(0)
            self.rescue_dropdown.current(1)
        return 4

    def save_operator(self):
        """ Updates the drone details and calls the save action. """
        'TODO: Update the drone from the widgets'
        if self.fname_entrybox.get() != '':
            self._operator.first_name = self.fname_entrybox.get()
        if self.lname_entrybox.get() != '':
            self._operator.family_name = self.lname_entrybox.get()
        if self.class_dropdown.get() =='Two':
            self._operator.drone_license = 2
        else:
            self._operator.drone_license = 1
        if self.rescue_dropdown.get() == 'Yes':
            self._operator.rescue_endorsement = 1
        else:
            self._operator.rescue_endorsement = 0
        self._operator.operations = self.operations_spinbox.get()
        self._save_action(self._operator)


if __name__ == '__main__':
    conn = mysql.connector.connect(user='root',
                                   password='password',
                                   host='localhost',
                                   database='database280')
    app = Application(conn)
    app.main_loop()
    conn.close()
