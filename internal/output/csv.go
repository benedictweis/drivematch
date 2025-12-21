package output

import (
	"fmt"
	"strings"
)

const csvDelimiter = ";"

type csvOutputWriter struct{}

func newCSVOutputWriter() *csvOutputWriter {
	return &csvOutputWriter{}
}

func (w *csvOutputWriter) WriteTable(columns int, rows []string) {
	var sb strings.Builder

	for i, row := range rows {
		if i%columns == 0 && i > 0 {
			sb.WriteString("\n")
		} else if i > 0 {
			sb.WriteString(csvDelimiter)
		}
		sb.WriteString(formatStringForConsole(row))
	}
	sb.WriteString("\n")

	fmt.Print(sb.String())
}
