import os, sys, io, pathlib, subprocess
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QRunnable, QObject, QThreadPool
import youtube_dl

# if this script was called with the youtube-dl module, we need to run that
_expect_mod = False
for index, arg in enumerate(sys.argv):
    if arg == "-m":
        _expect_mod = True
    if _expect_mod:
        if arg == "youtube_dl":
            # run youtube-dl with remaining args
            youtube_dl.main(sys.argv[index+1:])
            exit()

class DownloadSignals(QObject):
    """Possible signals from a DownloadWorker"""
    finished = pyqtSignal(int)
    message = pyqtSignal(str)
    ready = pyqtSignal(str)


class DownloadWorker(QRunnable):
    '''
    Worker thread for downloading the youtube video. By running the
    subprocess in a separate thread, the PyQt5 will not hang.
    '''
    signals = DownloadSignals()
    is_interrupted = False

    def __init__(self, url, folder):
        super().__init__()
        self.url = url
        self.folder = folder

    @pyqtSlot()
    def run(self):
        output =  os.path.join(self.folder, "%(title)s-%(id)s.%(ext)s")
        args = [sys.executable, "-m", "youtube_dl", self.url, "--no-color",
                "-o", output]
        self.signals.message.emit(f"[main] {' '.join(args)}")
        dl_job = subprocess.Popen(args, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE)

        exit_code = None
        while True:
            exit_code = dl_job.poll()
            # once youtube-dl starts downloading, it uses '\b' to
            # update the ETA and percent downloaded, instead of printing
            # to a new line
            # This sucks for us, because that means stdout.readline will
            # hang until the download is complete, which makes it hard
            # for the user to tell what's going on
            for msg in iter(lambda: dl_job.stdout.read(1), b''):
                self.signals.ready.emit(msg.decode())
            if exit_code is not None:
                break
        self.signals.finished.emit(exit_code)

clicks = 0
def start_download():
    url = form.url.text()
    folder = form.folder.text()
    worker = DownloadWorker(url, folder)
    form.msg_box.clear()
    form.download.setEnabled(False)
    threadpool.start(worker)


def download_done(exit_code):
    line = "".join(buffer).strip()
    if line:
        form.msg_box.appendPlainText(line)
    buffer.clear()
    form.download.setEnabled(True)
    form.msg_box.appendPlainText("[main] youtube-dl exited with code "
                                 f"'{exit_code}'")

def log_message(msg):
    form.msg_box.appendPlainText(msg)

buffer = []
def byte_ready(byte):
    if byte == '\b':
        return
    if byte == '\r' or byte == '\n':
        line = "".join(buffer).strip()
        if line:
            form.msg_box.appendPlainText(line)
        buffer.clear()
        return
    buffer.append(byte)


DownloadWorker.signals.finished.connect(download_done)
DownloadWorker.signals.message.connect(log_message)
DownloadWorker.signals.ready.connect(byte_ready)


def browse_folder():
    new_dir = QFileDialog.getExistingDirectory(window, caption="Open Folder",
                                               directory=form.folder.text())
    if new_dir:
        form.folder.setText(new_dir)


def sys_file(base):
    if not sys.executable.endswith("python.exe"):
        return os.path.join(dirname, base)
    else:
        return "./" + base

dirname, _ = os.path.split(sys.executable)

try:
    with open(sys_file("last_dir.txt")) as f:
        start_dir = f.read().strip()
except OSError:
    # if we can't find a 'last open'
    start_dir = str(os.path.join(pathlib.Path.home(), "Downloads"))

Form, Window = uic.loadUiType(sys_file("downloader.ui"))
app = QApplication([])
window = Window()
window.setWindowIcon(QIcon(sys_file("icon.png")))
form = Form()
threadpool = QThreadPool()
form.setupUi(window)

form.download.clicked.connect(start_download)
form.folder.setText(start_dir)
form.browse.clicked.connect(browse_folder)

window.show()
app.exec_()

try:
    with open(os.path.join(dirname, "last_dir.txt"), 'w') as f:
        f.write(form.folder.text())
except OSError:
    print("couldn't save last_dir")
