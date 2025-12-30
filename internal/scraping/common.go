package scraping

import (
	"archive/tar"
	"bytes"
	_ "embed"
	"io"
	"os"
	"path/filepath"

	"github.com/DataDog/zstd"
)

const (
	appName                = "drivematch"
	pythonBundleDirName    = "scraping"
	pythonBundleBinaryName = "main"
)

//go:embed scraping.tar.zst
var pythonBundle []byte

func extractPythonBundle() error {
	cacheDir, err := os.UserCacheDir()
	if err != nil {
		return err
	}

	directory := filepath.Join(cacheDir, appName)
	if err := os.MkdirAll(directory, 0755); err != nil {
		return err
	}

	filePath := filepath.Join(directory, pythonBundleDirName)
	if _, err := os.Stat(filePath); err == nil {
		return nil
	}

	decompressed, err := zstd.Decompress(nil, pythonBundle)
	if err != nil {
		return err
	}

	tarReader := tar.NewReader(bytes.NewReader(decompressed))

	for {
		header, err := tarReader.Next()
		if err == io.EOF {
			break
		}
		if err != nil {
			return err
		}

		targetPath := filepath.Join(filePath, header.Name)

		switch header.Typeflag {
		case tar.TypeDir:
			if err := os.MkdirAll(targetPath, os.FileMode(header.Mode)); err != nil {
				return err
			}
		case tar.TypeReg:
			if err := os.MkdirAll(filepath.Dir(targetPath), 0755); err != nil {
				return err
			}
			file, err := os.OpenFile(targetPath, os.O_CREATE|os.O_WRONLY, os.FileMode(header.Mode))
			if err != nil {
				return err
			}
			_, err = io.Copy(file, tarReader)
			file.Close()
			if err != nil {
				return err
			}
		}
	}

	return nil
}

func scrapingBinaryPath() string {
	cacheDir, err := os.UserCacheDir()
	if err != nil {
		panic(err)
	}
	return filepath.Join(cacheDir, appName, pythonBundleDirName, pythonBundleBinaryName)
}
