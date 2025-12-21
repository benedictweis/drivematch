package output

import (
	"fmt"
	"strings"
)

type tableOutputWriter struct{}

func newTableOutputWriter() *tableOutputWriter {
	return &tableOutputWriter{}
}

func (w *tableOutputWriter) WriteTable(columns int, rows []string) {
	maxWidths := calculateMaxColumnWidths(columns, rows)
	var sb strings.Builder

	// Top border
	sb.WriteString("┌")
	for i := range columns {
		sb.WriteString(strings.Repeat("─", maxWidths[i]+2))
		if i < columns-1 {
			sb.WriteString("┬")
		}
	}
	sb.WriteString("┐\n")

	// Data rows
	for i, row := range rows {
		colIdx := i % columns

		if colIdx == 0 {
			sb.WriteString("│ ")
		}

		sb.WriteString(formatStringForConsole(row))
		padding := maxWidths[colIdx] - calculateVisibleLength(row)
		sb.WriteString(strings.Repeat(" ", padding))

		if colIdx < columns-1 {
			sb.WriteString(" │ ")
		} else {
			sb.WriteString(" │\n")

			// Add separator only after header
			if i == columns-1 {
				sb.WriteString("├")
				for j := range columns {
					sb.WriteString(strings.Repeat("─", maxWidths[j]+2))
					if j < columns-1 {
						sb.WriteString("┼")
					}
				}
				sb.WriteString("┤\n")
			}
		}
	}

	// Bottom border
	sb.WriteString("└")
	for i := range columns {
		sb.WriteString(strings.Repeat("─", maxWidths[i]+2))
		if i < columns-1 {
			sb.WriteString("┴")
		}
	}
	sb.WriteString("┘\n")

	fmt.Print(sb.String())
}
