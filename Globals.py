from os.path import expanduser
from time import strftime, localtime

gblPgmList = [[], []]
filepath = expanduser('~\AppData\Local\Programs\TimeKeeper\\')
dtg = strftime('%D %H:%M:%S', localtime())
changes_saved = False

# Initialization messages
msgInitLog = dtg + ': Initializing the Data Log Grid'
msgInitTotals = dtg + ': Initializing the Totals Log Grid'
msgInitMainDisplay = dtg + ': Initializing the main UI'
msgInitPgmCombo = dtg + ': Initializing the Programs Combo box'

# Function call messages
msgClockIn = dtg + ': Executing the Clock In function'
msgClockOut = dtg + ': Executing the Clock Out function'
msgResetAbort = dtg + ': Reset action cancelled'
msgResetConfirm = dtg + ': Resetting all logs'
msgPopTotals = dtg + ': Populating the totals grid'
msgUpdateTotals = dtg + ': Updating the totals grid'
msgEditPrograms = dtg + ': Displaying the edit programs window'
msgOpenDeltek = dtg + ': Opening the default web browser to the DelTek website'
msgDeleteAbort = dtg + ': Delete action cancelled'
msgDeleteConfirm = dtg + ': Selected item deleted'
msgPgmAdded = dtg + ': Program added: '
msgCloseEditor = dtg + ': Closing the edit programs window'
msgClosePgm = dtg + ': Exiting the application'
msgRestore = dtg + ': Restoring previous session data'
msgSave = dtg + ': Saving current session data'
msgCreatingDir = dtg + ': ' + filepath + ' not found, creating directory'
msgDeleteJson = dtg + ': Removing old Json so new settings can be saved'

# Popup window messages
strExit = 'Are you sure you want to exit the application? Any unsaved changes will be lost.'
strReset = 'Are you sure you want to reset the form? This data cannot be recovered.'
strDelete = 'Are you sure you want to remove this program? This cannot be undone.'
strDeleteLog = 'Are you sure you want to remove this log entry? This cannot be undone.'
strResetTitle = 'Reset all data?'
strDeleteTitle = 'Confirm Program Deletion'


# comment this out for testing which will cause the json to save in the
# running directory
# filepath = '.\\'