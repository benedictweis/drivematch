
build:
	rm -rf dist internal/scraping/mobilede_scraper.tar.zst
	mkdir -p dist
	cd python && source .venv/bin/activate && pyinstaller --strip --optimize 2 --noconfirm mobilede.py
	cp -r python/dist/mobilede/ dist/mobilede_scraper
	cd dist/mobilede_scraper && tar --zstd -cf ../../internal/scraping/mobilede_scraper.tar.zst .
	go build -o dist/drivematch ./cmd/drivematch