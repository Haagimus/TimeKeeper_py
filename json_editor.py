from inspect import getmembers
from json import dump, loads
from os import path, remove, mkdir
from time import strftime
from urllib import request

from PySide2.QtWidgets import (QCheckBox, QComboBox, QLineEdit, QListWidget,
                               QRadioButton, QSlider, QSpinBox, QTableWidget,
                               QTableWidgetItem)

import Globals

# ===================================================================
# save "ui" controls and values to config.json
# ui = QMainWindow object
# settings = QSettings object
# ===================================================================

def gui_save(form):
    print(Globals.msgSave)
    if not path.exists(Globals.programsPath):
        print(Globals.msgCreatingPrograms)
        mkdir(Globals.programsPath)

    if not path.exists(Globals.filepath):
        print(Globals.msgCreatingDir)
        mkdir(Globals.filepath)

    if path.exists(Globals.filepath + 'time_keeper.json'):
        print(Globals.msgDeleteJson)
        remove(Globals.filepath + 'time_keeper.json')

    data = {'programs': Globals.gblPgmList}

    for name, obj in getmembers(form):
        if isinstance(obj, QComboBox):
            data[name] = {'index': obj.currentIndex(), 'itemText': obj.itemText(obj.currentIndex())}

        if isinstance(obj, QLineEdit):
            data[name] = {'text': obj.text()}

        if isinstance(obj, QCheckBox):
            data[name] = {'checkState': obj.checkState()}

        if isinstance(obj, QRadioButton):
            data[name] = {'isChecked': obj.isChecked()}

        if isinstance(obj, (QSpinBox, QSlider)):
            data[name] = {'value': obj.value()}

        if isinstance(obj, QListWidget):
            list_items = []
            for i in range(obj.count()):
                value = '' if obj.item(
                    i).text() is None else obj.item(i).text()
                list_items.append({i: {'text': value}})
            data[name] = list_items

        if isinstance(obj, QTableWidget):
            list_items = []
            if name == 'dg_log':
                for row in range(obj.rowCount()):
                    pgm = '' if obj.item(row, 0).text() is None else obj.item(row, 0).text()
                    time = '' if obj.item(row, 1).text() is None else obj.item(row, 1).text()
                    state = '' if obj.item(row, 2).text() is None else obj.item(row, 2).text()
                    hour = '' if obj.item(row, 3) is None else obj.item(row, 3).text()
                    list_items.append({row: {'Program': pgm, 'Time': time, 'State': state, 'Hours': hour}})

            if name == 'dg_totals':
                for row in range(obj.rowCount()):
                    pgm = '' if obj.item(row, 0).text() is None else obj.item(row, 0).text()
                    time = '' if obj.item(row, 1).text() is None else obj.item(row, 1).text()
                    comment = '' if obj.item(row, 2) is None else obj.item(row, 2).text()
                    list_items.append({row: {'Program': pgm, 'Time': time, 'Comment': comment}})

            data[name] = list_items

    with open(Globals.filepath + 'time_keeper.json', mode='a', encoding='utf-8') as \
            write_file:
        dump(data, write_file, indent=4)

    form.update_status('Last save at - ' + strftime('%c'))
    Globals.changes_saved = True

# ===================================================================
# restore "ui" controls with values stored in config.json
# ui = QMainWindow object
# settings = QSettings object
# ===================================================================


def gui_restore(form):
    print(Globals.msgRestore)
    json_data = open(Globals.filepath + 'time_keeper.json').read()
    data = loads(json_data)

    Globals.gblPgmList = data['programs']

    form.populate_programs_combo(Globals.gblPgmList)

    for name, obj in getmembers(form):
        try:
            if isinstance(obj, QComboBox):
                value = data[name]

                # get the index for specified string in combobox
                index = obj.findText(value['itemText'])

                if index == -1:  # add to list if not found
                    obj.insertItems(0, [value])
                    index = obj.findText(value)
                    obj.setCurrentIndex(index)
                else:
                    # preselect a combobox value by index
                    obj.setCurrentIndex(index)

            if isinstance(obj, QLineEdit):
                value = data[name]
                obj.setText(value['text'])  # restore lineEditFile

            if isinstance(obj, QCheckBox):
                value = data[name]  # get stored value from json file
                if value is not None:
                    obj.setCheckState(value['checkState'])  # restore checkbox

            if isinstance(obj, QRadioButton):
                value = data[name]
                if value is not None:
                    obj.setChecked(value(value['isChecked']))

            if isinstance(obj, (QSpinBox, QSlider)):
                value = data[name]
                if value is not None:
                    obj.setValue(data['value'])

            if isinstance(obj, QListWidget):
                size = len(data[name])
                for i in range(size):
                    value = data[name][i]  # get stored value from registry
                    if value is not None:
                        obj.addItem(value['text'])

            if isinstance(obj, QTableWidget):
                if name == 'dg_log':
                    for index in range(len(data[name])):
                        obj.insertRow(index)
                        obj.setItem(index, 0, QTableWidgetItem(
                            data[name][index][str(index)]['Program'])),
                        obj.setItem(index, 1, QTableWidgetItem(
                            data[name][index][str(index)]['Time'])),
                        obj.setItem(index, 2, QTableWidgetItem(
                            data[name][index][str(index)]['State'])),
                        obj.setItem(index, 3, QTableWidgetItem(
                            data[name][index][str(index)]['Hours']))

                elif name == 'dg_totals':
                    for index in range(len(data[name])):
                        obj.insertRow(index)
                        obj.setItem(index, 0, QTableWidgetItem(
                            data[name][index][str(index)]['Program'])),
                        obj.setItem(index, 1, QTableWidgetItem(
                            data[name][index][str(index)]['Time'])),
                        obj.setItem(index, 2, QTableWidgetItem(
                            data[name][index][str(index)]['Comment']))
        except TypeError:
            pass
