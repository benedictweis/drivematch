package database

import (
	"database/sql"
	"fmt"

	"github.com/DataDog/zstd"
	"github.com/benedictweis/drivematch/internal/common"
	"github.com/google/uuid"
	_ "modernc.org/sqlite"
)

type SQLiteDatabase struct {
	path string
	conn *sql.DB
}

func NewSQLiteDatabase(path string) *SQLiteDatabase {
	return &SQLiteDatabase{path: path}
}

func (db *SQLiteDatabase) Connect() error {
	conn, err := sql.Open("sqlite", db.path)
	if err != nil {
		return fmt.Errorf("failed to open database: %w", err)
	}

	if err := conn.Ping(); err != nil {
		return fmt.Errorf("failed to ping database: %w", err)
	}

	db.conn = conn

	db.performMigrations()

	return nil
}

func (db *SQLiteDatabase) Close() error {
	if db.conn != nil {
		return db.conn.Close()
	}
	return nil
}

func (db *SQLiteDatabase) InsertSearch(name, searchType string, data []byte) (string, error) {
	id := uuid.New().String()

	tx, err := db.conn.Begin()
	if err != nil {
		return "", fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer tx.Rollback()

	stmt, err := tx.Prepare(`INSERT INTO searches (id, name, created_at, searchType, data) VALUES (?, ?, datetime('now'), ?, ?)`)
	if err != nil {
		return "", fmt.Errorf("failed to prepare statement: %w", err)
	}
	defer stmt.Close()

	compressedData, err := zstd.Compress(nil, data)
	if err != nil {
		return "", fmt.Errorf("failed to compress data: %w", err)
	}

	_, err = stmt.Exec(id, name, searchType, compressedData)
	if err != nil {
		return "", fmt.Errorf("failed to execute statement: %w", err)
	}

	if err = tx.Commit(); err != nil {
		return "", fmt.Errorf("failed to commit transaction: %w", err)
	}

	return id, nil
}

func (db *SQLiteDatabase) GetSearches() ([]common.Search, error) {
	tx, err := db.conn.Begin()
	if err != nil {
		return nil, fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer tx.Rollback()

	rows, err := tx.Query(`SELECT id, name, created_at, searchType, LENGTH(data) FROM searches`)
	if err != nil {
		return nil, fmt.Errorf("failed to query searches: %w", err)
	}
	defer rows.Close()

	var searches []common.Search
	for rows.Next() {
		var s common.Search
		if err := rows.Scan(&s.ID, &s.Name, &s.CreatedAt, &s.SearchType, &s.DataLen); err != nil {
			return nil, fmt.Errorf("failed to scan row: %w", err)
		}
		searches = append(searches, s)
	}

	if err = tx.Commit(); err != nil {
		return nil, fmt.Errorf("failed to commit transaction: %w", err)
	}

	return searches, nil
}

func (db *SQLiteDatabase) GetSearchData(id string) ([]byte, error) {
	tx, err := db.conn.Begin()
	if err != nil {
		return nil, fmt.Errorf("failed to begin transaction: %w", err)
	}
	defer tx.Rollback()

	var compressedData []byte
	err = tx.QueryRow(`SELECT data FROM searches WHERE id LIKE ? || '%'`, id).Scan(&compressedData)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("no search found with id %s", id)
		}
		return nil, fmt.Errorf("failed to query search data: %w", err)
	}

	if err = tx.Commit(); err != nil {
		return nil, fmt.Errorf("failed to commit transaction: %w", err)
	}

	data, err := zstd.Decompress(nil, compressedData)
	if err != nil {
		return nil, fmt.Errorf("failed to decompress data: %w", err)
	}

	return data, nil
}

func (db *SQLiteDatabase) performMigrations() error {
	createTablesSQL := `
	CREATE TABLE IF NOT EXISTS searches (
		id TEXT PRIMARY KEY,
		name TEXT NOT NULL,
		created_at DATETIME NOT NULL,
		searchType TEXT NOT NULL,
		data BLOB NOT NULL
	);
	`

	_, err := db.conn.Exec(createTablesSQL)
	if err != nil {
		return fmt.Errorf("failed to create tables: %w", err)
	}

	return nil
}
