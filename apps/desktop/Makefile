
.PHONY: package

package:
	uv run pyinstaller --windowed --noconfirm --optimize 2 --name DriveMatch drivematch_desktop/app.py

dmg: clean package 
	create-dmg dist/DriveMatch.app dist

clean:
	rm -rf dist build *.spec
