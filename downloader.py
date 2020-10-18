import os, sys, io, pathlib, subprocess
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QFileDialog
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

def start_download():
    url = form.url.text()
    form.msg_box.clear()

    output =  os.path.join(form.folder.text(), "%(title)s-%(id)s.%(ext)s")
    args = [sys.executable, "-m", "youtube_dl", url, "--no-color",
            "-o", output]
    form.msg_box.appendPlainText(" ".join(args))
    dl_job = subprocess.Popen(args,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    exit_code = None
    while True:
        exit_code = dl_job.poll()
        for msg in dl_job.stdout:
            form.msg_box.appendPlainText(msg.decode().strip())
        if exit_code is not None:
            break
    form.msg_box.appendPlainText(f"youtube-dl exited with code '{exit_code}'")
    form.download.setFlat(False)


def browse_folder():
    new_dir = QFileDialog.getExistingDirectory(window,
                                               caption="Select a folder to download to",
                                               directory=form.folder.text()
                                               )
    if new_dir:
        form.folder.setText(new_dir)

dirname, _ = os.path.split(__file__)
uipath = os.path.join(dirname, "downloader.ui")
print(dirname)

Form, Window = uic.loadUiType(uipath)
app = QApplication([])
window = Window()
form = Form()
form.setupUi(window)

form.download.clicked.connect(start_download)
form.folder.setText(str(pathlib.Path.home()))
form.browse.clicked.connect(browse_folder)

window.show()
app.exec_()