
build:
	rm -rf dist internal/scraping/scraping.tar.zst
	mkdir -p dist
	cd python && source .venv/bin/activate && pyinstaller --strip --optimize 2 --noconfirm main.py
	cp -r python/dist/main/ dist/scraping
	cd dist/scraping && tar --zstd -cf ../../internal/scraping/scraping.tar.zst .
	go build -o dist/drivematch ./cmd/drivematch