from GUIp import updateCSV  # Importing the updateCSV function from GUIp module
from Pokemon import *  # Importing the Pokemon class
import pandas as pd  # Importing pandas library for data manipulation
import PySimpleGUI as sg  # Importing PySimpleGUI for creating graphical user interfaces

# Function to save Pokemon data to a CSV file
def savePokemon(filename, oPokemon):
    try:
        try:
            # Try reading the existing CSV file
            df = pd.read_csv(filename)
        except FileNotFoundError:
            # If the file does not exist, create an empty DataFrame with Pokemon headings
            df = pd.DataFrame(columns=Pokemon.headings)

        # Check if the Pokemon's position is already in the DataFrame
        if oPokemon.posFile in df['PosFile'].values:
            # Update the existing row with Pokemon's data
            df.loc[df['PosFile'] == oPokemon.posFile, ['ID', 'Name', 'Power', 'Type', 'Email']] = [
                oPokemon.ID, oPokemon.name, oPokemon.power, oPokemon.type, oPokemon.email
            ]
        else:
            # Create a new row with Pokemon's data and concatenate it to the DataFrame
            new_row = pd.DataFrame([[oPokemon.ID, oPokemon.name, oPokemon.power, oPokemon.type, oPokemon.email, oPokemon.posFile]],
                                   columns=Pokemon.headings)
            df = pd.concat([df, new_row], ignore_index=True)

        # Save the updated DataFrame to the CSV file
        df.to_csv(filename, index=False)

    except Exception as e:
        sg.popup_error('Error in savePokemon', f'Exception in savePokemon: {e}')

# Function to modify Pokemon data in a CSV file
def modifyPokemon(filename, oPokemon):
    try:
        # Try reading the existing CSV file
        df = pd.read_csv(filename)

        # Find the index of the row corresponding to the Pokemon's position
        index = df.index[df['PosFile'] == oPokemon.posFile].tolist()[0]

        # Update the row with Pokemon's modified data
        df.at[index, 'ID'] = int(oPokemon.ID)
        df.at[index, 'Name'] = oPokemon.name
        df.at[index, 'Power'] = pd.to_numeric(oPokemon.power, errors='coerce')
        df.at[index, 'Type'] = oPokemon.type
        df.at[index, 'Email'] = oPokemon.email

        # Save the updated DataFrame to the CSV file
        df.to_csv(filename, index=False)

        # Call the updateCSV function after modifying the record
        updateCSV(filename, df.values.tolist())

    except FileNotFoundError:
        sg.popup_error(f'Error in modifyPokemon: The file {filename} does not exist.')
    except Exception as e:
        sg.popup_error('Error in modifyPokemon', f'Exception in modifyPokemon: {e}')
