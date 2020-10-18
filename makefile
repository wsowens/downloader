
# create a virtual environment to handle dependencies
env:
	python -m venv env

bin:
	cxfreeze --include-files "downloader.ui" downloader.py


clean:
	rm -rf build dist
