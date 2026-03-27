#!/usr/bin/env bash
set -euo pipefail

# Generate one ITC-style markdown report per target folder by reading Ex*.java files.
# Usage:
#   bash scripts/generate-itc-report.sh
#   bash scripts/generate-itc-report.sh --scan-dir ./lab-archive
#   bash scripts/generate-itc-report.sh lab01 ../other-course/lab03
#
# Optional environment variables:
#   OUTPUT_DIR=reports
#   FILE_NAME="OOP_Name_03"
#   STUDENT_NAME="Your Name"
#   STUDENT_MAJOR="Your Major"
#   STUDENT_COURSE="OOP 4"
#   INSTRUCTION_LINK="https://example.com/instructions.pdf"
#   SCAN_DIR=.    (used only when no target folders are provided)

OUTPUT_DIR="${OUTPUT_DIR:-reports}"
FILE_NAME="${FILE_NAME:-}"
STUDENT_NAME="${STUDENT_NAME:-insert your name}"
STUDENT_MAJOR="${STUDENT_MAJOR:-insert your major}"
STUDENT_COURSE="${STUDENT_COURSE:-insert your course}"
INSTRUCTION_LINK="${INSTRUCTION_LINK:-link to pdf}"
SCAN_DIR="${SCAN_DIR:-.}"

usage() {
  cat <<'EOF'
Usage:
  bash scripts/generate-itc-report.sh [--scan-dir DIR] [--file-name NAME] [TARGET_DIR ...]

Behavior:
  - If TARGET_DIR is provided, each directory is scanned for Ex*.java.
  - If no TARGET_DIR is provided, subdirectories matching lab* under --scan-dir are scanned.

Examples:
  bash scripts/generate-itc-report.sh
  bash scripts/generate-itc-report.sh --scan-dir ./archives
  bash scripts/generate-itc-report.sh --file-name OOP_Name_03 lab03
  bash scripts/generate-itc-report.sh lab01 ../another-project/lab02

Optional env vars:
  OUTPUT_DIR, FILE_NAME, STUDENT_NAME, STUDENT_MAJOR, STUDENT_COURSE, INSTRUCTION_LINK, SCAN_DIR
EOF
}

TARGET_DIRS=()
while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --scan-dir|-s)
      if [[ "$#" -lt 2 ]]; then
        echo "Missing value for $1"
        exit 1
      fi
      SCAN_DIR="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    --file-name|-f)
      if [[ "$#" -lt 2 ]]; then
        echo "Missing value for $1"
        exit 1
      fi
      FILE_NAME="$2"
      shift 2
      ;;
    *)
      TARGET_DIRS+=("$1")
      shift
      ;;
  esac
done

mkdir -p "$OUTPUT_DIR"

if [[ "${#TARGET_DIRS[@]}" -gt 0 ]]; then
  mapfile -t LAB_DIRS < <(printf '%s\n' "${TARGET_DIRS[@]}")
else
  mapfile -t LAB_DIRS < <(find "$SCAN_DIR" -maxdepth 1 -mindepth 1 -type d -name 'lab*' | sort -V)
fi

if [[ "${#LAB_DIRS[@]}" -eq 0 ]]; then
  echo "No target directories found to scan."
  exit 1
fi

generated_count=0

for lab in "${LAB_DIRS[@]}"; do
  if [[ ! -d "$lab" ]]; then
    echo "Skipping $lab (not a directory)."
    continue
  fi

  mapfile -t files < <(find "$lab" -maxdepth 1 -type f -name 'Ex*.java' | sort -V)
  if [[ "${#files[@]}" -eq 0 ]]; then
    echo "Skipping $lab (no Ex*.java files found)."
    continue
  fi

  lab_base="$(basename "$lab")"
  report_slug="$(printf '%s' "$lab" | sed 's#^[./]*##; s#[/\\]#-#g')"
  if [[ -n "$FILE_NAME" ]]; then
    file_base="$FILE_NAME"
    if [[ "${#LAB_DIRS[@]}" -gt 1 ]]; then
      file_base="${FILE_NAME}-${report_slug}"
    fi
    [[ "$file_base" == *.md ]] || file_base="${file_base}.md"
    report_file="$OUTPUT_DIR/$file_base"
  else
    report_file="$OUTPUT_DIR/${report_slug}-report.md"
  fi
  report_title="${lab_base^^} Report"
  created_date="$(date +%Y-%m-%d)"

  {
    cat <<EOF
---
created: $created_date
title: $report_title
course: "[[OOP-4-Java]]"
tags:
  - studies
  - ITC
---
<div style="font-family: Arial, sans-serif; color: #333; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; min-height: 95vh; width: 100%; padding: 28px 24px; box-sizing: border-box; margin: 0 auto; break-after: page; page-break-after: always;">
<div style="margin-bottom: 30px;">
<img src="https://upload.wikimedia.org/wikipedia/en/f/f7/Institute_of_Technology_of_Cambodia_logo.png" alt="ITC Logo" style="max-width: 150px; height: auto;">
</div>
<h1 style="margin: 20px 0; color: #1a1a1a; font-size: 32px; font-weight: 700; line-height: 1.2;">$report_title</h1>
<h2 style="margin: 15px 0; color: #444; font-size: 24px; font-weight: 400; line-height: 1.25;">Object-Oriented Programming Exercises</h2>
<div style="margin-top: 42px; font-size: 18px; line-height: 1.8; text-align: center;">
<p style="margin: 0;">Student: $STUDENT_NAME</p>
<p style="margin: 0;">Major: $STUDENT_MAJOR</p>
<p style="margin: 0;">Course: $STUDENT_COURSE</p>
<p style="margin: 0;">Lab: $lab_base</p>
<p style="margin: 0;">Date: $created_date</p>
</div>
</div>

## Overview

Student: \`$STUDENT_NAME\`
Major: \`$STUDENT_MAJOR\`
Course: \`$STUDENT_COURSE\`
Instruction: \`$INSTRUCTION_LINK\`

---

EOF

    for file in "${files[@]}"; do
      base_name="$(basename "$file" .java)"
      ex_tag="${base_name%%_*}"
      ex_id="${ex_tag#Ex}"
      rel_file="${file#./}"

      cat <<EOF
## Exercise $ex_id

> [!example]
> Source file: \`$rel_file\`

\`\`\`java
EOF

      cat "$file"

      cat <<EOF
\`\`\`

![[Output Image.png]]

EOF
    done
  } > "$report_file"

  generated_count=$((generated_count + 1))
  echo "Generated $report_file"
done

if [[ "$generated_count" -eq 0 ]]; then
  echo "No reports generated."
  exit 1
fi

echo "Done. Generated $generated_count report(s) in $OUTPUT_DIR/."
