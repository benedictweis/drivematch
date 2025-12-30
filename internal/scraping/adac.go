package scraping

import (
	"encoding/base64"
	"encoding/json"
	"fmt"
	"os/exec"
)

func ScrapeADAC(keywords []string) ([]byte, error) {
	err := extractPythonBundle()
	if err != nil {
		return nil, fmt.Errorf("error extracting python bundle: %w", err)
	}

	encodedKeywords, err := json.Marshal(keywords)
	if err != nil {
		return nil, fmt.Errorf("error marshaling keywords to JSON: %w", err)
	}
	encodedKeyIdentifiers := base64.StdEncoding.EncodeToString(encodedKeywords)

	fmt.Println("Attention: You will need to solve a google captcha once the Firefox browser opens!")
	adacCmd := exec.Command(scrapingBinaryPath(), "adac", encodedKeyIdentifiers)

	output, err := adacCmd.Output()
	if err != nil {
		return nil, fmt.Errorf("error capturing output from 'adac': %w", err)
	}

	return output, nil
}
