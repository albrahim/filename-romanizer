import locale
import os
import pathlib
import sys

if sys.platform == 'darwin':
    import osxmetadata

import PySide6.QtWidgets, PySide6.QtGui, PySide6.QtCore
import watchdog.observers, watchdog.events

ALF = "ا"
BAA = "ب"
JIM = "ج"
DAL = "د"
HAA = "ه"
WAW = "و"
ZAY = "ز"
HHA = "ح"
TTA = "ط"
YAA = "ي"
KAF = "ك"
LAM = "ل"
MIM = "م"
NUN = "ن"
SIN = "س"
AYN = "ع"
FAA = "ف"
SAD = "ص"
QAF = "ق"
RAA = "ر"
SHN = "ش"
TAA = "ت"
THA = "ث"
KHA = "خ"
THH = "ذ"
DHA = "ض"
TTH = "ظ"
GYN = "غ"

FATHA = "َ"
DHAMMA = "ُ"
KASRA = "ِ"

TNWN_FATHA = "ً"
TNWN_DHAMMA = "ٌ"
TNWN_KASRA = "ٍ"

SUKOON = "ْ"

HAMZA = "ء"
ALF_HAMZA = "أ"
ALF_HAMZA_KASR = "إ"
WAW_HAMZA = "ؤ"
YAA_HAMZA = "ئ"
ALF_MAQSURA = "ى"
ALF_MADD = "آ"

TAA_MARBUTA = "ة"
TATWEEL = "ـ"
SHADDA = "ّ"

HAMZA_FOG = 'ٔ'
HAMZA_TAHAT = 'ٕ'
MADD = 'ٓ'

GYF = "گ"
VAA = "ڤ"

DGT0 = "٠"
DGT1 = "١"
DGT2 = "٢"
DGT3 = "٣"
DGT4 = "٤"
DGT5 = "٥"
DGT6 = "٦"
DGT7 = "٧"
DGT8 = "٨"
DGT9 = "٩"

QUESTION_MARK = "؟"
COMMA = "،"
SEMICOLON = "؛"
PERCENT = "٪"

vowels = [FATHA, DHAMMA, KASRA]
long_vowels = [ALF, WAW, YAA]
long_vowel_to_short = {
    ALF: FATHA,
    WAW: DHAMMA,
    YAA: KASRA,
}

letter_map = {
    ALF: 'a',
    BAA: 'b',
    JIM: 'j',
    DAL: 'd',
    HAA: 'h',
    WAW: 'w',
    ZAY: 'z',
    HHA: 'h',
    TTA: 't',
    YAA: 'y',
    KAF: 'k',
    LAM: 'l',
    MIM: 'm',
    NUN: 'n',
    SIN: 's',
    AYN: 'a',
    FAA: 'f',
    SAD: 's',
    QAF: 'q',
    RAA: 'r',
    SHN: 'sh',
    TAA: 't',
    THA: 'th',
    KHA: 'kh',
    THH: 'th',
    DHA: 'dh',
    TTH: 'th',
    GYN: 'gh',

    FATHA: 'a',
    DHAMMA: 'u',
    KASRA: 'i',

    TNWN_FATHA: "an",
    TNWN_DHAMMA: "un",
    TNWN_KASRA: "in",

    SUKOON: '',

    HAMZA: '',
    ALF_HAMZA: 'a',
    ALF_HAMZA_KASR: 'i',
    WAW_HAMZA: 'u',
    YAA_HAMZA: 'i',
    ALF_MAQSURA: 'a',
    ALF_MADD: 'aa',

    HAMZA_FOG: '',
    HAMZA_TAHAT: '',
    MADD: '',

    TAA_MARBUTA: 'a',
    TATWEEL: '',
    SHADDA: '',
    GYF: 'g',
    VAA: 'v',
    DGT0: '0',
    DGT1: '1',
    DGT2: '2',
    DGT3: '3',
    DGT4: '4',
    DGT5: '5',
    DGT6: '6',
    DGT7: '7',
    DGT8: '8',
    DGT9: '9',

    QUESTION_MARK: '?',
    COMMA: ',',
    SEMICOLON: ';',
    PERCENT: '%',
}


# Romanize arabic text
def romanize(text):
    romanized = []
    previous_ayn = False
    for char in text:
        # Handle vowel after ayn, by only include the vowel and ignoring the ayn, or inserting a if ayn is not voweled
        if char == AYN and not previous_ayn:
            # Add ayn to be handeled in the next iteration
            previous_ayn = True
            continue
        # Check if ayn exists from the previous iteration
        elif previous_ayn:
            # Insert the vowel if the next character is a long vowel
            if char in long_vowels:
                romanized.append(letter_map.get(long_vowel_to_short[char]))
            # Insert 'a' if the next character is a constant, don't add any extra if it is a vowel
            elif char not in vowels:
                romanized.append(letter_map.get(ALF))
            # Consume ayn
            previous_ayn = False

        romanized.append(letter_map.get(char, char))

    # Handle ayn at the end of the string
    if previous_ayn:
        romanized.append(letter_map.get(ALF))

    return ''.join(romanized)


path = None
rootFiles = []


def fileIsMacosPackage(file):
    if sys.platform != 'darwin': return False
    return 'com.apple.package' in (osxmetadata.OSXMetaData(file.path).get('kMDItemContentTypeTree') or [])


def fileVisible(file):
    # ignore .DS_Store if using macOS
    if sys.platform == 'darwin' and file.name == '.DS_Store':
        return False
    # ignore all dot files if using a unix system
    if os.name == 'posix' and file.name.rfind('.') == 0:
        return False
    return True


# traverse file for romanization
def traverse_files():
    global path

    # breadth first search algorithm
    root_files = []
    all_files = []

    path = path or pathlib.Path(os.path.dirname(__file__))
    with os.scandir(path) as entries:
        # bring root files and dirs
        for entry in entries:
            if not fileVisible(entry):
                continue
            try:
                package = fileIsMacosPackage(entry)
            except OSError:
                continue

            root_files.append({
                "file": entry,
                "parent": '.',
                "romanized_parent": '.',
                "romanized_name": romanize(entry.name),
                "conflicts": False,
                "package": package,
            })

        # copy root files to queue
        file_queue = [e for e in root_files]

        # continue surfacing files until all is empty
        while len(file_queue) > 0:
            target_entry = file_queue[0]

            try:
                # if the target entry is a directory, bring its files to the queue
                if target_entry['file'].is_dir() and not target_entry['file'].is_symlink():
                    for entry in os.scandir(target_entry['file'].path):
                        if not fileVisible(entry):
                            continue

                        file_queue.append({
                            # keep track of file info in addition to the file entry
                            "file": entry,
                            # keep track of parent path starting from selected root directory
                            "parent": target_entry['parent'] + '/' + target_entry['file'].name,
                            "romanized_parent": target_entry['romanized_parent'] + '/' + target_entry['romanized_name'],
                            "romanized_name": romanize(entry.name),
                            "conflicts": False,
                            "package": fileIsMacosPackage(entry),
                        })

                all_files.append(target_entry)
            except PermissionError:
                pass
            except OSError:
                pass
            finally:
                # remove the file from the queue
                file_queue.pop(0)

    # print romanized file tree and find children
    SHOULD_PRINT_FILE_TREE = False

    print_stack = list(reversed([file for file in all_files if file['parent'] == '.']))
    conflicts = []
    while len(print_stack) > 0:
        target_entry = print_stack.pop(-1)

        if target_entry['package']:
            children = []
        else:
            # find children of the current file
            children = list(reversed(
                [file for file in all_files if
                 file['parent'] == target_entry['parent'] + '/' + target_entry['file'].name]))

        # store children of current file to entry dict
        target_entry['children'] = children

        # add children of the current file to the stack
        print_stack += children

        # find duplicate romanizations
        children_set = set()
        duplicate_set = set()
        for child in children:
            child_romanized_name = child['romanized_name']
            if child_romanized_name not in children_set:
                children_set.add(child_romanized_name)
            else:
                duplicate_set.add(child_romanized_name)
        if len(duplicate_set) > 0:
            conflicts += [file for file in children if file['romanized_name'] in duplicate_set]
            for file in conflicts:
                file['conflicts'] = True

        if SHOULD_PRINT_FILE_TREE:
            # count file depth
            file_depth = target_entry['parent'].count('/')

            # print current file's name
            file_is_conflicts = target_entry in conflicts
            file_text_leader = ''
            file_text_trailer = ''

            # set the colors for conflicting file
            if file_is_conflicts:
                file_text_leader = '\033[91m'
                file_text_trailer = '\033[0m'
            print(file_depth * '  ' + file_text_leader + target_entry['romanized_name'] + file_text_trailer)

    if SHOULD_PRINT_FILE_TREE:
        # print conflicts
        if len(conflicts) > 0:
            print(f'Found {len(conflicts) // 2} conflict(s)')
    return root_files


fileTreeNeedsUpdate = False
fileTreeBeingUpdated = False


def main():
    app = PySide6.QtWidgets.QApplication()
    app.setApplicationName('Filename Romanizer')
    app.setApplicationDisplayName('Filename Romanizer')

    mw = PySide6.QtWidgets.QMainWindow()
    widget = PySide6.QtWidgets.QWidget()
    vview = PySide6.QtWidgets.QVBoxLayout()

    openPathHView = PySide6.QtWidgets.QHBoxLayout()

    tree = PySide6.QtWidgets.QTreeWidget()
    tree.setColumnCount(2)
    tree.setHeaderLabels(['Filename', 'Romanized'])
    treeRtl = tree.isRightToLeft()
    tree.setAlternatingRowColors(True)

    fileIcon = mw.style().standardIcon(PySide6.QtWidgets.QStyle.StandardPixmap.SP_FileIcon)
    dirIcon = mw.style().standardIcon(PySide6.QtWidgets.QStyle.StandardPixmap.SP_DirClosedIcon)

    def fileToTreeItem(file):
        str1 = file['file'].name
        str2 = file['romanized_name']
        typedir = file['file'].is_dir() and not file['package']
        children = file['children']
        item = PySide6.QtWidgets.QTreeWidgetItem()
        item.setText(0, str1)
        item.setText(1, str2)
        item.setToolTip(0, str1)
        item.setToolTip(1, str2)
        if treeRtl:
            item.setTextAlignment(1, PySide6.QtCore.Qt.AlignmentFlag.AlignTrailing)
        item.setIcon(0, dirIcon if typedir else fileIcon)
        for child in children:
            item.addChild(fileToTreeItem(child))
        return item

    def syncFiles():
        global fileTreeBeingUpdated
        global rootFiles

        fileTreeBeingUpdated = True
        tree.clear()

        rootFiles = traverse_files()
        rootTreeItems = []
        for file in rootFiles:
            rootTreeItems.append(fileToTreeItem(file))

        for treeItem in rootTreeItems:
            tree.addTopLevelItem(treeItem)
        fileTreeBeingUpdated = False

    syncFiles()

    # add browse button
    openButton = PySide6.QtWidgets.QPushButton("Open")

    dialog = PySide6.QtWidgets.QFileDialog()
    dialog.setFileMode(PySide6.QtWidgets.QFileDialog.FileMode.Directory)
    dialog.setDirectoryUrl(pathlib.Path.home().as_uri())

    fileWatcher = watchdog.observers.Observer()

    # Event handler called when the directory is changed
    class FileEventHandler(watchdog.events.FileSystemEventHandler):
        def on_any_event(self, event):
            global fileTreeNeedsUpdate
            fileTreeNeedsUpdate = True

    fileEventHandler = FileEventHandler()

    fileWatcher.unschedule_all()
    if path:
        fileWatcher.schedule(fileEventHandler, path=str(path), recursive=True)
    fileWatcher.start()

    def checkForFileUpdates():
        global fileTreeNeedsUpdate
        global fileTreeBeingUpdated

        if fileTreeNeedsUpdate and not fileTreeBeingUpdated:
            syncFiles()
            fileTreeNeedsUpdate = False

    timer = PySide6.QtCore.QTimer(tree)
    tree.connect(timer, PySide6.QtCore.SIGNAL("timeout()"), checkForFileUpdates)
    timer.start(1000)

    def browse(checked):
        global path
        didSelect = dialog.exec()
        if didSelect:
            # update tree according to selected path
            path = pathlib.Path(dialog.directory().path())

            # continue watching for any changes in the selected directory
            fileWatcher.unschedule_all()
            fileWatcher.schedule(fileEventHandler, path=str(path), recursive=True)

            syncFiles()
            updateLabel()
            if mw:
                mw.setWindowFilePath(str(path))

    openButton.clicked.connect(browse)

    # add path label
    pathLabel = PySide6.QtWidgets.QLabel()

    def updateLabel():
        pathLabel.setText(path.as_posix())
        pathLabel.setToolTip(path.as_posix())

    updateLabel()

    # add rename all button
    renameButton = PySide6.QtWidgets.QPushButton("Rename All")

    def startRename(checked):
        ret = PySide6.QtWidgets.QMessageBox.critical(
            mw,
            'Rename Files',
            f'Do you want to rename files in "{path.name if path else "nil"}"?',
            PySide6.QtWidgets.QMessageBox.StandardButton.Yes | PySide6.QtWidgets.QMessageBox.StandardButton.Cancel,
            PySide6.QtWidgets.QMessageBox.StandardButton.Cancel,
        )
        if ret == PySide6.QtWidgets.QMessageBox.StandardButton.Yes:
            doRename(rootFiles)

    def doRename(root):
        for e in root:
            if len(e['children']) > 0:
                doRename(e['children'])
            old_path = pathlib.Path(e['file'].path)
            new_path = old_path.with_name(e['romanized_name'])
            if not e['conflicts']:
                os.renames(old_path, new_path)

    renameButton.clicked.connect(startRename)

    openButton.setMinimumWidth(120)
    openButton.setMaximumWidth(120)

    renameButtonLayout = PySide6.QtWidgets.QHBoxLayout()
    renameButtonLayout.addWidget(renameButton)
    renameButtonLayout.setAlignment(renameButton, PySide6.QtCore.Qt.AlignmentFlag.AlignTrailing)

    openPathHView.addStretch()
    openPathHView.addWidget(openButton)
    openPathHView.addWidget(pathLabel)
    openPathHView.addStretch()

    vview.addLayout(openPathHView)
    vview.addWidget(tree)
    vview.addLayout(renameButtonLayout)
    widget.setLayout(vview)

    tree.setColumnWidth(0, tree.width() // 2)
    tree.setColumnWidth(1, 0)

    mw.setMinimumWidth(420 + 200)
    mw.setMinimumHeight(594 + 200 * int(594 / 420))

    mw.setCentralWidget(widget)
    if path:
        mw.setWindowFilePath(str(path))
    mw.show()

    err = app.exec()
    fileWatcher.stop()
    app.exit(err)


if __name__ == '__main__':
    main()
