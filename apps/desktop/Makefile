
.PHONY: package

package:
	uv run pyinstaller --windowed --noconfirm --optimize 2 --name DriveMatch drivematch-desktop/app.py

clean:
	rm -rf dist build *.spec
