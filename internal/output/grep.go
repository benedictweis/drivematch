package output

import (
	"fmt"
	"strings"
)

type grepOutputWriter struct{}

func newGrepOutputWriter() *grepOutputWriter {
	return &grepOutputWriter{}
}

func (w *grepOutputWriter) WriteTable(columns int, rows []string) {
	maxWidths := calculateMaxColumnWidths(columns, rows)
	var sb strings.Builder

	for i, row := range rows {
		colIdx := i % columns
		padding := maxWidths[colIdx] - calculateVisibleLength(row)
		sb.WriteString(formatStringForConsole(row))
		if colIdx < columns-1 {
			sb.WriteString(strings.Repeat(" ", padding+2))
		} else {
			sb.WriteString("\n")
		}
	}
	fmt.Print(sb.String())
}
