#!/usr/bin/env python3
"""
Interactive Report Generator
Generates markdown reports for lab exercises in any programming language.
"""

import os
import sys
from pathlib import Path
from datetime import datetime


def ask(prompt: str, default: str = "") -> str:
    """Ask user for input with optional default."""
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    response = input(full_prompt).strip()
    return response if response else default


def ask_choice(prompt: str, choices: list, default: str = None) -> str:
    """Ask user to choose from a list."""
    print(f"\n{prompt}")
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. {choice}")
    
    while True:
        try:
            choice_num = input("Enter number (or just press Enter for default): ").strip()
            if not choice_num and default:
                return default
            idx = int(choice_num) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
            print(f"Please enter a number between 1 and {len(choices)}")
        except ValueError:
            print(f"Please enter a valid number")


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    """Ask user yes/no question."""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()
    
    if response in ("y", "yes"):
        return True
    elif response in ("n", "no"):
        return False
    else:
        return default


def get_metadata() -> dict:
    """Gather all metadata through interactive prompts."""
    print("\n" + "="*60)
    print("REPORT GENERATOR - METADATA COLLECTION")
    print("="*60 + "\n")
    
    subject = ask("Subject/Course name (e.g., DSA, OOP)", "DSA")
    student_name = ask("Your name", "insert your name")
    student_major = ask("Your major", "insert your major")
    student_course = ask("Course name", "insert your course")
    instruction_link = ask("Instruction link (URL)", "link to pdf")
    
    return {
        "subject": subject,
        "student_name": student_name,
        "student_major": student_major,
        "student_course": student_course,
        "instruction_link": instruction_link,
    }


def get_file_settings() -> dict:
    """Gather file scanning settings."""
    print("\n" + "="*60)
    print("FILE SETTINGS")
    print("="*60 + "\n")
    
    # Language selection
    common_langs = ["Java", "Python", "C++", "C", "JavaScript", "TypeScript", "Other"]
    lang = ask_choice("Select programming language", common_langs, "Java")
    
    if lang == "Other":
        lang = ask("Enter language name")
    
    # File extension
    ext_map = {
        "Java": "java",
        "Python": "py",
        "C++": "cpp",
        "C": "c",
        "JavaScript": "js",
        "TypeScript": "ts",
    }
    
    file_ext = ext_map.get(lang, ask("Enter file extension (without dot)", "java"))
    if not file_ext.startswith("."):
        file_ext = f".{file_ext}"
    
    # Scan mode selection
    scan_mode_choices = ["Auto-scan for lab* folders", "Manually specify directories"]
    scan_mode = ask_choice("How would you like to select directories?", scan_mode_choices, "Auto-scan for lab* folders")
    
    target_dirs = []
    scan_dir = "."
    
    if "Manual" in scan_mode:
        # Manual directory selection
        while True:
            dir_path = ask("Enter directory path (or 'done' to finish)")
            if dir_path.lower() == "done":
                break
            if dir_path:
                target_dirs.append(dir_path)
                print(f"  Added: {dir_path}")
    else:
        # Auto-scan mode
        scan_dir = ask("Enter parent directory to scan for lab* folders", ".")
    
    # Output directory
    output_dir = ask("Output directory for reports", "reports")
    
    return {
        "language": lang,
        "file_ext": file_ext,
        "scan_dir": scan_dir,
        "target_dirs": target_dirs,
        "output_dir": output_dir,
    }


def find_lab_dirs(scan_dir: str) -> list:
    """Find all lab* directories."""
    scan_path = Path(scan_dir)
    
    if not scan_path.exists():
        print(f"Error: Directory {scan_dir} does not exist")
        return []
    
    lab_dirs = sorted([
        d for d in scan_path.iterdir()
        if d.is_dir() and d.name.startswith("lab")
    ], key=lambda x: x.name)
    
    return lab_dirs


def find_exercise_files(lab_dir: Path, file_ext: str) -> list:
    """Find all Ex*.{ext} files in a lab directory."""
    pattern = f"Ex*{file_ext}"
    files = sorted(lab_dir.glob(pattern), key=lambda x: x.name)
    return files


def generate_report(lab_dir: Path, output_dir: str, metadata: dict, file_settings: dict) -> str:
    """Generate a single report for a lab directory."""
    files = find_exercise_files(lab_dir, file_settings["file_ext"])
    
    if not files:
        return None
    
    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Generate report filename following pattern: subject_Name_labnumber
    lab_name = lab_dir.name
    
    # Extract lab number from directory name (e.g., "lab3-pointers" -> "3")
    lab_number = "".join(c for c in lab_name if c.isdigit())
    if not lab_number:
        lab_number = lab_name.replace("lab", "")
    
    # Format: subject_FirstName_labnumber.md
    student_first_name = metadata["student_name"].split()[0] if metadata["student_name"] else "Name"
    report_file = Path(output_dir) / f"{metadata['subject']}_{student_first_name}_lab{lab_number}.md"
    
    # Create report content
    created_date = datetime.now().strftime("%Y-%m-%d")
    report_title = f"{lab_name.upper()} Report"
    lang = file_settings["language"]
    
    content = f"""---
created: {created_date}
title: {report_title}
course: "{metadata['student_course']}"
tags:
  - studies
  - lab
---

<div style="font-family: Arial, sans-serif; color: #333; display: flex; flex-direction: column; justify-content: center; align-items: center; text-align: center; min-height: 95vh; width: 100%; padding: 28px 24px; box-sizing: border-box; margin: 0 auto; break-after: page; page-break-after: always;">
<div style="margin-bottom: 30px;">
<img src="https://upload.wikimedia.org/wikipedia/en/f/f7/Institute_of_Technology_of_Cambodia_logo.png" alt="ITC Logo" style="max-width: 150px; height: auto;">
</div>
<h1 style="margin: 20px 0; color: #1a1a1a; font-size: 32px; font-weight: 700; line-height: 1.2;">{report_title}</h1>
<h2 style="margin: 15px 0; color: #444; font-size: 24px; font-weight: 400; line-height: 1.25;">{lang} Programming Exercises</h2>
<div style="margin-top: 42px; font-size: 18px; line-height: 1.8; text-align: center;">
<p style="margin: 0;">Student: {metadata['student_name']}</p>
<p style="margin: 0;">Major: {metadata['student_major']}</p>
<p style="margin: 0;">Course: {metadata['student_course']}</p>
<p style="margin: 0;">Lab: {lab_name}</p>
<p style="margin: 0;">Date: {created_date}</p>
</div>
</div>

## Overview

Student: `{metadata['student_name']}`
Major: `{metadata['student_major']}`
Course: `{metadata['student_course']}`
Instruction: `{metadata['instruction_link']}`

Language: `{lang}`

---

"""
    
    # Add exercises
    lang_code = file_settings["file_ext"].lstrip(".")
    for file in files:
        base_name = file.stem  # filename without extension
        ex_tag = base_name.split("_")[0]
        ex_id = ex_tag.replace("Ex", "")
        
        # Get relative path for display
        try:
            rel_path = file.relative_to(Path.cwd())
        except ValueError:
            # If file is not relative to cwd, just use the absolute path
            rel_path = file.resolve()
        
        content += f"""## Exercise {ex_id}

> [!example]
> Source file: `{rel_path}`

```{lang_code}
"""
        
        try:
            with open(file, 'r') as f:
                file_content = f.read()
                # Ensure code block ends with newline for proper formatting
                if not file_content.endswith('\n'):
                    file_content += '\n'
                content += file_content
        except Exception as e:
            content += f"ERROR: Could not read file: {e}"
        
        content += """```

![[Output Image.png]]

"""
    
    # Write report
    try:
        with open(report_file, 'w') as f:
            f.write(content)
        return str(report_file)
    except Exception as e:
        print(f"Error writing report: {e}")
        return None


def main():
    """Main program flow."""
    try:
        # Gather settings
        metadata = get_metadata()
        file_settings = get_file_settings()
        
        print("\n" + "="*60)
        print("GENERATING REPORTS")
        print("="*60 + "\n")
        
        # Find lab directories
        if file_settings["target_dirs"]:
            # Use manually specified directories
            lab_dirs = [Path(d).resolve() for d in file_settings["target_dirs"]]
            
            # Show which paths were tried
            print(f"Checking {len(lab_dirs)} directory path(s):")
            for path in lab_dirs:
                exists = path.exists() and path.is_dir()
                status = "✓" if exists else "✗"
                print(f"  {status} {path}")
            
            # Filter to existing directories
            lab_dirs = [d for d in lab_dirs if d.exists() and d.is_dir()]
        else:
            # Auto-scan for lab* directories
            lab_dirs = find_lab_dirs(file_settings["scan_dir"])
        
        if not lab_dirs:
            print(f"No directories found.")
            return 1
        
        print(f"Found {len(lab_dirs)} directory/ies:")
        for lab in lab_dirs:
            print(f"  - {lab}")
        
        # Generate reports
        generated_count = 0
        for lab_dir in lab_dirs:
            report_file = generate_report(
                lab_dir,
                file_settings["output_dir"],
                metadata,
                file_settings
            )
            
            if report_file:
                print(f"✓ Generated {report_file}")
                generated_count += 1
            else:
                print(f"✗ Skipped {lab_dir.name} (no Ex* files found)")
        
        print(f"\n{'='*60}")
        if generated_count > 0:
            print(f"✓ Done! Generated {generated_count} report(s) in {file_settings['output_dir']}/")
            return 0
        else:
            print("✗ No reports were generated")
            return 1
    
    except KeyboardInterrupt:
        print("\n\nCancelled by user")
        return 1
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
