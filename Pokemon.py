class Pokemon:
    # Class variables for column headings and field descriptions
    headings = ['ID', 'Name', 'Power', 'Type', 'Email', 'PosFile']
    fields = {
        '-ID-': 'Pokemon ID:',
        '-Name-': 'Pokemon Name:',
        '-Power-': 'Power:',
        '-Type-': 'Type:',
        '-Email-': 'Email:',
        '-PosFile-': 'Position into File'
    }

    existing_ids = set()  # Set to store existing IDs

    def __init__(self, ID, name, power, type, email, posFile):
        # Check if the primary key already exists
        if ID in Pokemon.existing_ids:
            raise ValueError(f"Duplicate ID: {ID}. Pokemon IDs must be unique.")

        # Initialize instance variables with provided values
        self.ID = ID
        self.name = name
        self.power = power
        self.type = type
        self.email = email
        self.posFile = posFile
        self.erased = False  # Flag to indicate whether the Pokemon has been erased

        # Add the new primary key to the set of existing IDs
        Pokemon.existing_ids.add(ID)

    def __eq__(self, oP):
        # Define equality based on the 'posFile' attribute
        return oP.posFile == self.posFile

    def __str__(self):
        # String representation of the Pokemon object
        return f"{self.ID}, {self.name}, {self.power}, {self.type}, {self.email}, {self.posFile}"

    def pokemoninPos(self, pos):
        # Check if the Pokemon is at the specified position
        return self.posFile == pos

    def setPokemon(self, name, power, type, email):
        # Update the Pokemon's attributes with new values
        self.name = name
        self.power = power
        self.type = type
        self.email = email
