# CSV_Tidy

Clean up CSV and TSV files by removing unhelpful columns. Shared cleanup engine powers a CLI and a desktop GUI.

## Install

```bash
cd CSV_Tidy
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```


## Cleanup options

| Option | What it does |
|--------|----------------|
| Empty Columns | Remove columns with no values |
| Constant Columns | Remove columns where every value is the same |
| Duplication Columns | Remove columns that share the same title **and** the same values (keep the first) |
| Remove IDs | Drop coded columns when a display column exists and each ID/code always maps to the same label: `{Prefix} User ID`→`{Prefix}`; `{Prefix} ID` / `Code` / `Number`→`{Prefix} Meaning`, `Description`, `Desc`, `Name`, or bare `{Prefix}`. `Org`/`Organization` count as the same prefix token. |
| Duplicate Values | Remove columns with different titles but identical values (keep the leftmost) |
| Remove Emails | Remove columns whose non-empty values are all email addresses |
| Sort Columns | Sort remaining columns alphabetically by name (case-insensitive) |

## CLI

```bash
csv-tidy data.csv --all
csv-tidy data.tsv --empty-columns --constant-columns -o cleaned.tsv
csv-tidy data.csv --all --dry-run
csv-tidy data.csv --sort-columns -o sorted.csv
csv-tidy data.csv --all --delimiter tab --force -o data.csv
```

Flags: `--empty-columns`, `--constant-columns`, `--duplication-columns`, `--remove-ids`, `--duplicate-values`, `--remove-emails`, `--sort-columns`, `--all`, `--dry-run`, `--force`, `-q` / `--quiet`, `--delimiter auto|comma|tab`.

Default output is `{stem}_tidy.{csv|tsv}` next to the input. Overwriting the input path requires `--force`.

## GUI

```bash
csv-tidy-gui
```

Open a file, choose delimiter and cleanup options, then click columns to include or exclude them from the output (highlighted = excluded). Run / Save writes the current selection.

## Tests

```bash
pytest
```
