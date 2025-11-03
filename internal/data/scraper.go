package data

import (
	"fmt"
	"log/slog"
	"os"
	"time"

	"github.com/benedictweis/drivematch/internal/common"
	playwright "github.com/playwright-community/playwright-go"
)

func GetCarsFromURL(url string) ([]*common.Car, error) {
	htmlPages, err := fetchAllHTMLPages(url)
	if err != nil {
		return nil, err
	}

	var cars []*common.Car
	for _, html := range htmlPages {
		pageCars, err := parseCarsFromHTML(html)
		if err != nil {
			return nil, err
		}
		cars = append(cars, pageCars...)
	}

	return cars, nil
}

func fetchAllHTMLPages(baseURL string) ([]string, error) {
	pw, err := playwright.Run()
	if err != nil {
		return nil, fmt.Errorf("could not start playwright: %v", err)
	}
	defer func() {
		if err = pw.Stop(); err != nil {
			slog.Error("could not stop Playwright", "error", err)
		}
	}()

	browser, err := pw.Firefox.Launch()
	defer func() {
		if err = browser.Close(); err != nil {
			slog.Error("could not close browser", "error", err)
		}
	}()

	if err != nil {
		return nil, fmt.Errorf("could not launch browser: %v", err)
	}
	page, err := browser.NewPage()
	if err != nil {
		return nil, fmt.Errorf("could not create page: %v", err)
	}
	if _, err = page.Goto(baseURL); err != nil {
		return nil, fmt.Errorf("could not goto: %v", err)
	}

	time.Sleep(5 * time.Second)

	html, err := page.Content()
	if err != nil {
		return nil, fmt.Errorf("could not get page content: %v", err)
	}

	filePath := "./page.html"
	if err := os.WriteFile(filePath, []byte(html), 0644); err != nil {
		return nil, fmt.Errorf("could not write HTML to file: %v", err)
	}
	slog.Info("HTML written to file", "path", filePath)

	return []string{}, nil
}

func parseCarsFromHTML(html string) ([]*common.Car, error) {

	return nil, nil
}
