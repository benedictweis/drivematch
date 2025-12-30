package output

import (
	"fmt"
	"unicode/utf8"
)

// OutputWriter is an interface for writing tables.
type OutputWriter interface {

	// SetContent sets the content of the table.
	// The first parameter is the number of columns.
	// The second parameter indicates whether the first line is a header.
	// The third parameter is a slice of strings representing the rows.
	WriteTable(int, []string)
}

type OutputFormats string

const (
	FormatTable OutputFormats = "table"
	FormatCSV   OutputFormats = "csv"
	FormatGrep  OutputFormats = "grep"
)

func GetOutputWriter(format string) (OutputWriter, error) {
	switch format {
	case string(FormatTable):
		return newTableOutputWriter(), nil
	case string(FormatCSV):
		return newCSVOutputWriter(), nil
	case string(FormatGrep):
		return newGrepOutputWriter(), nil
	default:
		return nil, fmt.Errorf("unknown output format: %s", format)
	}
}

func Price(price float64) string {
	if price <= 1000 {
		return fmt.Sprintf("%.0f EUR", price)
	}

	priceStr := fmt.Sprintf("%.0f", price)
	var result string
	for i, digit := range priceStr {
		if i > 0 && (len(priceStr)-i)%3 == 0 {
			result += "."
		}
		result += string(digit)
	}
	return result + " EUR"
}

func Link(url, text string) string {
	return fmt.Sprintf("\x1f%s\x1f%s", url, text)
}

func DataLength(len int) string {
	bytes := float64(len)

	if bytes < 1024 {
		return fmt.Sprintf("%d B", len)
	} else if bytes < 1024*1024 {
		return fmt.Sprintf("%.1f KB", bytes/1024)
	} else if bytes < 1024*1024*1024 {
		return fmt.Sprintf("%.1f MB", bytes/(1024*1024))
	} else {
		return fmt.Sprintf("%.1f GB", bytes/(1024*1024*1024))
	}
}

func decodeLink(s string) (string, string, bool) {
	if len(s) < 3 || s[0] != '\x1f' {
		return "", "", false
	}
	parts := []rune(s)
	secondSepIdx := -1
	for i := 1; i < len(parts); i++ {
		if parts[i] == '\x1f' {
			secondSepIdx = i
			break
		}
	}
	if secondSepIdx == -1 {
		return "", "", false
	}
	url := string(parts[1:secondSepIdx])
	text := string(parts[secondSepIdx+1:])
	return url, text, true
}

func encodeLinkForConsole(url, text string) string {
	return fmt.Sprintf("\033]8;;%s\033\\%s\033]8;;\033\\", url, text)
}

func calculateMaxColumnWidths(columns int, rows []string) []int {
	maxWidths := make([]int, columns)
	for i, row := range rows {
		colIdx := i % columns
		visibleLength := calculateVisibleLength(row)
		if visibleLength > maxWidths[colIdx] {
			maxWidths[colIdx] = visibleLength
		}
	}
	return maxWidths
}

func calculateVisibleLength(s string) int {
	_, text, isLink := decodeLink(s)
	if isLink {
		return utf8.RuneCountInString(text)
	}
	return utf8.RuneCountInString(s)
}

func formatStringForConsole(s string) string {
	url, text, isLink := decodeLink(s)
	if isLink {
		return encodeLinkForConsole(url, text)
	}
	return s
}
