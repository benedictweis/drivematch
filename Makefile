
build:
	rm -rf dist
	mkdir -p dist
	go build -o dist/drivematch ./cmd/drivematch
	cd python && source .venv/bin/activate && pyinstaller --strip --optimize 2 --noconfirm mobilede.py
	cp -r python/dist/mobilede/ dist/