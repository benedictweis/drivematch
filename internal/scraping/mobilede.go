package scraping

import (
	"encoding/base64"
	"fmt"
	"os/exec"
)

func ScrapeMobileDe(url string) ([]byte, error) {
	err := extractPythonBundle()
	if err != nil {
		return nil, fmt.Errorf("error extracting python bundle: %w", err)
	}

	encodedURL := base64.StdEncoding.EncodeToString([]byte(url))
	mobiledeCmd := exec.Command(scrapingBinaryPath(), "mobilede", encodedURL)

	output, err := mobiledeCmd.Output()
	if err != nil {
		return nil, fmt.Errorf("error capturing output from 'mobilede': %w", err)
	}

	return output, nil
}
