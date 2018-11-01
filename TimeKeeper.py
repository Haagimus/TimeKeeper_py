import sys
import webbrowser
from datetime import datetime
from math import floor
from os import path
from time import localtime, strftime

from DigitalClock import DigitalClock
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon, QKeySequence, QFont
from PySide2.QtWidgets import (QApplication, QComboBox, QDialog, QWidget, QGridLayout, QHBoxLayout, QHeaderView,
                               QInputDialog, QLabel, QListWidget, QMessageBox, QPushButton, QTableWidget,
                               QTableWidgetItem, QVBoxLayout, QMainWindow, QAction, QFrame, QAbstractItemView)

import Globals
from json_editor import gui_restore, gui_save


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.time_logger_widget = TimeLoggerUi(parent=self)
        self.setCentralWidget(self.time_logger_widget)
        self.statusBar()
        self.setWindowIcon(QIcon('timetable.ico'))
        self.setWindowTitle('Time Logger')

        self.resize(600, 600)

        # Create the menu bar
        menu_bar = self.menuBar()

        # Add a file menu to the bar
        file_menu = menu_bar.addMenu('File')
        help_menu = menu_bar.addMenu('Help')

        # Create the menu options
        save_action = QAction('Save', self)
        edit_action = QAction('Edit Programs', self)
        reset_action = QAction('Reset Form', self)
        quit_action = QAction('Exit', self)
        about_menu = QAction('About', self)

        # Add created options to the menus
        file_menu.addAction(save_action)
        file_menu.addAction(edit_action)
        file_menu.addAction(reset_action)
        file_menu.addSeparator()
        file_menu.addAction(quit_action)
        help_menu.addAction(about_menu)

        # Bind the created options to the target functions and setup hotkeys
        save_action.triggered.connect(self.save_event)
        save_action.setShortcut(QKeySequence.Save)
        edit_action.triggered.connect(self.time_logger_widget.edit_programs)
        reset_action.triggered.connect(self.time_logger_widget.reset_grids)
        reset_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_R))
        quit_action.triggered.connect(self.closeEvent)
        quit_action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_X))
        about_menu.triggered.connect(self.about_info)

        Globals.changes_saved = True

    def save_event(self):
        print(Globals.msgSave)
        gui_save(self.time_logger_widget)

    def closeEvent(self, event):
        # Prompt the user and confirm they want to exit
        if not Globals.changes_saved:
            result = QMessageBox.question(self, 'Exit', Globals.strExit, QMessageBox.Yes | QMessageBox.No)
            if result == QMessageBox.Yes:
                print(Globals.msgClosePgm)
                sys.exit()
            else:
                event.ignore()
        else:
            print(Globals.msgClosePgm)
            sys.exit()

    def about_info(self):
        email = 'mailto:Gary.Haag@L3T.com?Subject=Time%20Keeper%20App'
        QMessageBox.about(self, 'About TimeKeeper',
                          'Version: 1.0<br>Creator: Gary Haag<br>Email: <a href=%s>Gary.Haag@L3T.com</a>' % email)

    def keyPressEvent(self, event):
        # Redirect the native esc hot key to the close event prompt
        if event.key() == Qt.Key_Escape:
            self.close()
        # Add delete hotkey, if a row is actively selected in the dg_log, delete it
        if event.key() == Qt.Key_Delete and self.time_logger_widget.dg_log.hasFocus() is True:
            result = QMessageBox.question(self, 'Confirm Delete', Globals.strDeleteLog,
                                          QMessageBox.Yes | QMessageBox.No)
            if result == QMessageBox.Yes:
                self.time_logger_widget.dg_log.removeRow(self.time_logger_widget.dg_log.currentRow())
                self.time_logger_widget.update_totals()
            else:
                event.ignore()


class TimeLoggerUi(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Define the form controls
        self.cmb_pgm = QComboBox(self)
        self.btn_in = QPushButton('Clock In')
        self.btn_out = QPushButton('Clock Out')
        self.btn_dt = QPushButton('Open Deltek')
        # self.calendar = QCalendarWidget()
        self.total_time = QLabel()
        self.time_label = QLabel()
        self.DigitalClock = DigitalClock()
        self.dg_log = QTableWidget()
        self.dg_totals = QTableWidget()

        # Add a grid layout to the window
        self.grid = QGridLayout()
        self.grid.setColumnStretch(0, 0)
        self.grid.setRowStretch(0, 1)

        # Add the programs combo box
        self.grid.addWidget(QLabel('Select a program:'), 0, 0)
        self.grid.addWidget(self.cmb_pgm, 0, 1, 1, 1)

        # Add the clock in button
        self.grid.addWidget(self.btn_in, 1, 0, 1, 1)
        self.btn_in.underMouse()
        self.btn_in.clicked.connect(self.clock_in)

        # Add the clock out button
        self.grid.addWidget(self.btn_out, 1, 1, 1, 1)
        self.btn_out.clicked.connect(self.clock_out)

        # Add the total time label
        self.grid.addWidget(self.total_time, 2, 0, 1, 2)
        self.total_time.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.total_time.setFont(QFont('Times', 20, QFont.Bold))
        self.total_time.setAlignment(Qt.AlignCenter)
        self.total_time.setText('Total: 0.0')

        # Add the open Deltek button
        self.grid.addWidget(self.btn_dt, 3, 0, 1, 2)
        self.btn_dt.clicked.connect(self.open_deltek)

        # Add the current time clock
        self.grid.addWidget(self.time_label, 4, 0, 1, 1)
        self.time_label.setText('Time: ')
        self.time_label.setFont(QFont('Times', 20, QFont.Normal))
        self.time_label.setAlignment(Qt.AlignRight)
        self.grid.addWidget(self.DigitalClock, 4, 1, 1, 1)
        self.DigitalClock.setFrameStyle(QFrame.NoFrame)

        # Add the calendar
        # self.grid.addWidget(self.calendar, 4, 0, 1, 2)
        # self.calendar.setGridVisible(True)

        self.init_data_log()
        self.dg_log.itemChanged.connect(self.manual_log_update)
        self.init_totals_log()

        self.setLayout(self.grid)

        if path.exists(Globals.filepath + 'time_keeper.json'):
            while self.dg_totals.rowCount() > 0:
                self.dg_totals.removeRow(0)
            gui_restore(self)
            self.update_totals()
        else:
            pass

    def update_status(self, message):
        MainWindow.statusBar(self.parent()).showMessage(message)

    def manual_log_update(self):
        # TODO: setup manual updates to trigger a recalculation on log entries
        Globals.changes_saved = False
        item_row = self.dg_log.currentRow()
        item_col = self.dg_log.currentColumn()
        try:
            if item_col == 2:
                print(self.dg_log.item(item_row, item_col).text())
        except AttributeError:
            pass

    def init_data_log(self):
        # Setup and add the data log grid
        print(Globals.msgInitLog)
        self.dg_log.setColumnCount(4)
        self.dg_log.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.dg_log.verticalHeader().setVisible(False)
        dg_log_header = self.dg_log.horizontalHeader()
        dg_log_header.setSectionResizeMode(0, QHeaderView.Stretch)
        dg_log_header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        dg_log_header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        dg_log_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.dg_log.setHorizontalHeaderLabels(('Program', 'Time', 'In/Out', 'Hours'))
        self.grid.addWidget(self.dg_log, 0, 2, 8, 4)

    def init_totals_log(self):
        # Setup and add the totals log grid
        print(Globals.msgInitTotals)
        self.dg_totals.setColumnCount(3)
        self.dg_log.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.dg_totals.verticalHeader().setVisible(False)
        dg_totals_header = self.dg_totals.horizontalHeader()
        dg_totals_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        dg_totals_header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        dg_totals_header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.dg_totals.setHorizontalHeaderLabels(('Program Name', 'Total Time', 'Comments'))
        self.grid.addWidget(self.dg_totals, 10, 0, 6, 6)
        self.populate_totals_grid()

    def populate_programs_combo(self, programs):
        # Populate the combo box with items
        print(Globals.msgInitPgmCombo)
        self.cmb_pgm.clear()
        for pgm in programs[0]:
            self.cmb_pgm.addItem(pgm)

    def populate_totals_grid(self):
        # Change the program selection
        print(Globals.msgPopTotals)
        self.dg_totals.setRowCount(len(Globals.gblPgmList[0]))
        for pgm in range(len(Globals.gblPgmList[0])):
            item = QTableWidgetItem(Globals.gblPgmList[0][pgm])
            hours = QTableWidgetItem(str(floor(int(Globals.gblPgmList[1][pgm] * 10)) / 10.0))
            self.dg_totals.setItem(pgm, 0, item)
            self.dg_totals.setItem(pgm, 1, hours)

    def update_totals(self):
        print(Globals.msgUpdateTotals)
        for hrs in range(len(Globals.gblPgmList[1])):
            Globals.gblPgmList[1][hrs] = 0.0
        # Update the calculated totals in the totals gid
        for pgm in Globals.gblPgmList[0]:
            for i in range(self.dg_log.rowCount()):
                if self.dg_log.item(i, 2).text() == 'Out' and self.dg_log.item(i, 0).text() == pgm:
                    p_idx = Globals.gblPgmList[0].index(pgm)
                    Globals.gblPgmList[1][p_idx] += float(self.dg_log.item(i, 3).text())
        self.total_time.setText('Total: ' + str(floor(sum((Globals.gblPgmList[1]) * 10)) / 10.0))
        self.populate_totals_grid()

    def clock_in(self):
        # Clock in to selected program
        print(Globals.msgClockIn)
        current_time = localtime()
        next_row = self.dg_log.rowCount()
        self.dg_log.insertRow(next_row)
        self.dg_log.setItem(next_row, 0, QTableWidgetItem(self.cmb_pgm.currentText()))
        self.dg_log.setItem(next_row, 1, QTableWidgetItem(strftime('%H:%M', current_time)))
        self.dg_log.setItem(next_row, 2, QTableWidgetItem('In'))
        self.dg_log.scrollToBottom()
        Globals.changes_saved = False

    def clock_out(self):
        # Clock out of selected program
        print(Globals.msgClockOut)
        end_time = strftime('%H:%M', localtime())
        next_row = self.dg_log.rowCount()
        self.dg_log.insertRow(next_row)
        self.dg_log.setItem(next_row, 0, QTableWidgetItem(self.cmb_pgm.currentText()))
        self.dg_log.setItem(next_row, 1, QTableWidgetItem(end_time)), self.dg_log.setItem(next_row, 2,
                                                                                          QTableWidgetItem('Out'))
        if next_row == 0:
            pass
        else:
            item = self.dg_log.item(next_row - 1, 2).text()
            if item != 'In':
                pass
            else:
                start_time = self.dg_log.item(next_row - 1, 1).text()
                time_diff = datetime.strptime(end_time, '%H:%M') - datetime.strptime(start_time, '%H:%M')
                self.dg_log.setItem(next_row, 3,
                                    QTableWidgetItem(str(floor((time_diff.seconds / 60 / 60) * 10) / 10.0)))
            self.update_totals()
        self.dg_log.scrollToBottom()
        Globals.changes_saved = False

    def edit_programs(self):
        # Show the edit programs dialog
        print(Globals.msgEditPrograms)
        mw.hide()
        editor = UiProgramEditor(self)
        editor.show()

    def reset_grids(self):
        # Reset the data grids
        reset_popup = QMessageBox()
        result = reset_popup.question(
            self, Globals.strResetTitle, Globals.strReset, reset_popup.Yes | reset_popup.No)
        if result == reset_popup.No:
            print(Globals.msgResetAbort)
        else:
            print(Globals.msgResetConfirm)
            while self.dg_log.rowCount() > 0:
                self.dg_log.removeRow(0)
            while self.dg_totals.rowCount() > 0:
                self.dg_totals.removeRow(0)
            for pgm in range(len(Globals.gblPgmList[1])):
                Globals.gblPgmList[1][pgm] = 0.0
            self.total_time.setText("Total: 0.0")
            self.populate_totals_grid()
            Globals.changes_saved = False

    @staticmethod
    def open_deltek():
        # Open the Deltek web page
        print(Globals.msgOpenDeltek)
        webbrowser.open('http://dcwdte01.pes.sg.l-3com.com:7009/DeltekTC/welcome.msv')


class UiProgramEditor(QDialog):
    def __init__(self, parent=None):
        super(UiProgramEditor, self).__init__(parent)

        self.setWindowTitle('Programs Config')

        # Create the window buttons and fields
        self.list_programs = QListWidget(self)
        self.btn_delete = QPushButton('Delete Program')
        self.btn_add = QPushButton('Add Program')

        self.list_programs.addItems(Globals.gblPgmList[0])
        self.btn_delete.setEnabled(False)
        self.list_programs.itemClicked.connect(self.program_selected)
        self.btn_add.clicked.connect(self.program_add)
        self.btn_delete.clicked.connect(self.program_delete)

        self.button_box = QHBoxLayout()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.list_programs)
        self.layout.addLayout(self.button_box)
        self.button_box.addWidget(self.btn_delete)
        self.button_box.addWidget(self.btn_add)
        self.setLayout(self.layout)

    def program_selected(self):
        self.btn_delete.setEnabled(True)

    def program_delete(self):
        del_popup = QMessageBox()
        result = del_popup.warning(
            self, Globals.strDeleteTitle, Globals.strDelete,
            del_popup.Yes | del_popup.No)
        if result == del_popup.No:
            print(Globals.msgDeleteAbort)
            self.btn_delete.setEnabled(False)
            self.list_programs.setItemSelected(self.list_programs.currentItem(), False)
        else:
            print(Globals.msgDeleteConfirm)
            self.btn_delete.setEnabled(False)
            Globals.gblPgmList[0].pop(self.list_programs.currentRow())
            Globals.gblPgmList[1].pop(self.list_programs.currentRow())
            # self.list_programs.takeItem(self.list_programs.currentRow())
            self.list_programs.clear()
            self.list_programs.addItems(Globals.gblPgmList[0])
            Globals.changes_saved = False

    def program_add(self):
        text, ok = QInputDialog.getText(self, 'Add Program', 'Enter the name of the program you want to add:')
        if ok:
            print(Globals.msgPgmAdded + text)
            Globals.gblPgmList[0].append(text)
            Globals.gblPgmList[1].append(0.0)
            self.list_programs.addItem(text)
            Globals.changes_saved = False

    def closeEvent(self, event):
        print(Globals.msgCloseEditor)
        mw.time_logger_widget.populate_programs_combo(Globals.gblPgmList)
        mw.time_logger_widget.populate_totals_grid()
        mw.show()
        mw.time_logger_widget.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    app.exec_()
