import csv
import sys

# Importing necessary modules and classes
from SerializeFile import *
from Pokemon import *
import PySimpleGUI as sg
import re
import operator
import os

# File name for storing Pokemon data
fPokemon = 'Pokemon.csv'

# List to store Pokemon objects
lPokemon = []

# List to store table data for GUI
table_data = []

# Regular expressions for input validation
pattern_email = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
pattern_ID = r"\d{1,4}"
pattern_power = r"\d{1,4}"

# Function to read Pokemon data from a CSV file and populate the lPokemon list
def readPokemon(filename, lPokemon):
    try:
        # Use pandas to read the CSV file and convert it to a list of lists
        df = pd.read_csv(filename)
        l = df.values.tolist()
        for poke in l:
            lPokemon.append(Pokemon(poke[0], poke[1], poke[2], poke[3], poke[4], -1))
    except FileNotFoundError:
        sg.popup_error(f'Error in readPokemon: The file {filename} does not exist.')
    except Exception as e:
        sg.popup_error('Error in readPokemon', 'Exception in readPokemon', e)

# Function to clear input fields in the GUI
def clear_fields(window):
    window['-ID-'].update(disabled=False)
    window['-ID-'].update('')
    window['-Name-'].update('')
    window['-Power-'].update('')
    window['-Type-'].update('')
    window['-Email-'].update('')
    window['-PosFile-'].update('')

# Function to add a new Pokemon to the lPokemon list and update the CSV file
def addPokemon(lPokemon, table_data, oPokemon):
    lPokemon.append(oPokemon)
    savePokemon(fPokemon, oPokemon)
    table_data.append([oPokemon.ID, oPokemon.name, oPokemon.power, oPokemon.type, oPokemon.email, oPokemon.posFile])
    return lPokemon, table_data

# Function to purge deleted records from the CSV file
def purgeDeletedRecords(filename, lPokemon, table_data):
    try:
        # Create a new CSV file with remaining records
        new_filename = filename.replace("Pokemon", "newPokemon")
        remaining_records = [row for row in table_data if not any(o.pokemoninPos(row[-1]) and o.erased for o in lPokemon)]
        df_remaining = pd.DataFrame(remaining_records, columns=Pokemon.headings)
        df_remaining.to_csv(new_filename, index=False)

        # Remove the original CSV file
        os.remove(filename)

        sg.popup("Purge operation completed successfully.")
        sg.popup_auto_close('Closing the application...')
        sys.exit()

    except Exception as e:
        sg.popup_error('Error in purgeDeletedRecords', f'Exception in purgeDeletedRecords: {e}')

# Function to delete a Pokemon from the lPokemon list and update the CSV file
def delPokemon(posinTable):
    global lPokemon
    global table_data
    posinFile = table_data[posinTable][-1]
    pdel = None
    for o in lPokemon:
        if o.pokemoninPos(posinFile):
            pdel = o
            break
    if pdel is not None:
        lPokemon.remove(pdel)
        table_data.remove(table_data[posinTable])
        pdel.erased = True
        modifyPokemon(fPokemon, pdel)
        updateCSV(fPokemon, table_data)

# Function to update the CSV file with the modified table_data
def updateCSV(filename, table_data):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(Pokemon.headings)
        for row in table_data:
            writer.writerow(row)

# Function to update a Pokemon's attributes and modify the CSV file
def updatePokemon(t_row_PokemonInterfaz, posinFile):
    global lPokemon
    global table_data
    pdel = None
    for o in lPokemon:
        if o.pokemoninPos(posinFile):
            pdel = o
            break
    if pdel is not None:
        old_id = pdel.ID
        pdel.setPokemon(t_row_PokemonInterfaz[1], t_row_PokemonInterfaz[2], t_row_PokemonInterfaz[3], t_row_PokemonInterfaz[4])

        for t in table_data:
            if t[-1] == posinFile:
                t[1], t[2], t[3], t[4] = t_row_PokemonInterfaz[1], t_row_PokemonInterfaz[2], t_row_PokemonInterfaz[3], t_row_PokemonInterfaz[4]
                break

        Pokemon.existing_ids.remove(old_id)
        Pokemon.existing_ids.add(pdel.ID)

        modifyPokemon(fPokemon, pdel)

# Function to sort the table_data based on selected columns
def sort_table(table, cols):
    for col in reversed(cols):
        try:
            table = sorted(table, key=operator.itemgetter(col))
        except Exception as e:
            sg.popup_error('Error in sort_table', 'Exception in sort_table', e)
    return table

# Function to create the GUI
def interfaz():
    global lPokemon
    global table_data
    font1, font2 = ('Arial', 14), ('Arial', 16)
    sg.theme('DarkRed')
    sg.set_options(font=font1)
    table_data = []

    # Read Pokemon data from CSV file and populate table_data
    readPokemon(fPokemon, lPokemon)
    for o in lPokemon:
        if not o.erased:
            table_data.append([o.ID, o.name, o.power, o.type, o.email, o.posFile])

    # GUI layout
    layout = [
                 [sg.Push(), sg.Text('Pokemon CRUD'), sg.Push()]
             ] + [
                 [sg.Text(text), sg.Push(), sg.Input(key=key)] for key, text in Pokemon.fields.items()
             ] + [
                 [sg.Push()] +
                 [sg.Button(button) for button in ('Add', 'Delete', 'Modify', 'Clear')] +
                 [sg.Push()],
                 [sg.Table(values=table_data, headings=Pokemon.headings, max_col_width=50, num_rows=10,
                           display_row_numbers=False, justification='center', enable_events=True, enable_click_events=True,
                           vertical_scroll_only=False, select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                           expand_x=True, bind_return_key=True, key='-Table-')],
                 [sg.Button('Purge'), sg.Push(), sg.Combo(values=Pokemon.headings, default_value=Pokemon.headings[0], key='-SortBy-'), sg.Button('Sort File')],
                 ]
    sg.theme('DarkBlue4')

    # Create the GUI window
    window = sg.Window('Pokemon Management with Files', layout, finalize=True)
    window['-PosFile-'].update(disabled=True)
    window['-Table-'].bind("<Double-Button-1>", " Double")

    while True:
        event, values = window.read()

        # Event handling
        if event == sg.WIN_CLOSED:
            break
        if event == 'Add':
            valida = False
            if re.match(pattern_email, values['-Email-']):
                if re.match(pattern_ID, values['-ID-']):
                    if re.match(pattern_power, values['-Power-']):
                        valida = True
                    else:
                        sg.popup_error("Error: Invalid Power format.")
                else:
                    sg.popup_error("Error: Invalid ID format.")
            else:
                sg.popup_error("Error: Invalid Email format.")
            if valida:
                lPokemon, table_data = addPokemon(lPokemon, table_data, Pokemon(
                    int(values['-ID-']),
                    values['-Name-'],
                    int(values['-Power-']),
                    values['-Type-'],
                    values['-Email-'],
                    -1
                ))

                window['-Table-'].update(table_data)
                clear_fields(window)
        if event == 'Delete':
            if len(values['-Table-']) > 0:
                delPokemon(values['-Table-'][0])
                window['-Table-'].update(table_data)
                clear_fields(window)
        if (event == '-Table- Double'):
            if len(values['-Table-']) > 0:
                row = values['-Table-'][0]
                window['-ID-'].update(disabled=True)
                window['-ID-'].update(str(table_data[row][0]))
                window['-Name-'].update(str(table_data[row][1]))
                window['-Power-'].update(str(table_data[row][2]))
                window['-Type-'].update(str(table_data[row][3]))
                window['-Email-'].update(str(table_data[row][4]))
                window['-PosFile-'].update(str(table_data[row][5]))
        if event == 'Clear':
            clear_fields(window)
        if event == 'Modify':
            if len(values['-Table-']) > 0:
                row = values['-Table-'][0]
                window['-ID-'].update(disabled=True)
                window['-ID-'].update(str(table_data[row][0]))
                window['-Name-'].update(str(table_data[row][1]))
                window['-Power-'].update(str(table_data[row][2]))
                window['-Type-'].update(str(table_data[row][3]))
                window['-Email-'].update(str(table_data[row][4]))
                window['-PosFile-'].update(str(table_data[row][5]))

                # Remove the selected entry from the CSV file
                delPokemon(row)

                window['-Table-'].update(table_data)
                clear_fields(window)
        elif event == 'Purge':
            # Call the purgeDeletedRecords function
            purgeDeletedRecords(fPokemon, lPokemon, table_data)
            # Update the table after purging
            table_data = []
            for o in lPokemon:
                if not o.erased:
                    table_data.append([o.ID, o.name, o.power, o.type, o.email, o.posFile])
            window['-Table-'].update(table_data)
            clear_fields(window)
        elif event == 'Sort File':
            # Ask the user to select a sorting criterion
            sorting_criterion = values['-SortBy-']
            if not sorting_criterion:
                sg.popup_error("Please select a sorting criterion.")
            else:
                # Call the sort_table function with the selected criterion
                table_data = sort_table(table_data, cols=[Pokemon.headings.index(sorting_criterion)])
                window['-Table-'].update(table_data)

    # Close the GUI window
    window.close()

# Main execution block
if __name__ == "__main__":
    fPokemon = 'Pokemon.csv'
    lPokemon = []
    pattern_email = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    pattern_ID = r"\d{1,4}"
    pattern_power = r"\d{1,4}"
    interfaz()
