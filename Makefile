# DriftWatch: every step is one command. Each step reads files and writes files under out/.
# No make on your machine (for example plain Windows)? Every recipe below is one line of Python:
# copy it and run it by hand, or install make (winget install ezwinports.make).
PY ?= python
PORT ?= 8000

.PHONY: help setup data train live drift alerts ui test issues all clean

# The echo lines have no quotes and no brackets on purpose: cmd.exe (Windows) prints quotes, sh (Linux, macOS) chokes on brackets.
help:
	@echo make setup  - install the Python packages
	@echo make data   - build the synthetic machine data and the live plan
	@echo make train  - pull history from Feast and train the model
	@echo make live   - push live batches, some drifted, into Feast
	@echo make drift  - compare batches with the reference using Evidently, then raise alerts
	@echo make ui     - serve the dashboard at http://localhost:$(PORT)/web/
	@echo make test   - run the tests
	@echo make issues - run the Issue Lab and print Reproduced or Fixed or Error
	@echo make all    - data, train, live and drift in one go
	@echo make clean  - delete out/

setup:
	$(PY) -m pip install -r requirements.txt

data:
	$(PY) src/make_data.py

train:
	$(PY) src/train.py

live:
	$(PY) src/live.py

drift:
	$(PY) src/check_drift.py
	$(PY) src/alerts.py

alerts:
	$(PY) src/alerts.py

ui:
	@echo Dashboard: http://localhost:$(PORT)/web/ - press Ctrl+C to stop
	$(PY) -m http.server $(PORT) --bind 127.0.0.1

test:
	$(PY) -m pytest -q

issues:
	$(PY) issues/check_all.py

all: data train live drift

clean:
	$(PY) -c "import shutil; shutil.rmtree('out', ignore_errors=True)"
