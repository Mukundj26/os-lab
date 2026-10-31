# Operating Systems Lab – 23 Practicals

This repository contains the material for all 23 practicals from the supplied `os practicals total.pdf`. Each practical has its own folder and README containing the practical question, code, and compile/run instructions as provided in the PDF.

## Repository structure

- `practicals/Practical_01/README.md` through `Practical_23/README.md` – per-practical source material
- `os practicals total.pdf` – original reference PDF
- `OS_Practicals_Full_Extract.txt` – complete text extraction for searching

## Open in VS Code / run on Ubuntu WSL

1. Extract this repository ZIP.
2. Open the extracted folder in VS Code.
3. Open the Ubuntu (WSL) terminal.
4. For a C program, copy its code into the named `.c` file and compile with `gcc file.c -o program` (use `-pthread` for pthread programs).
5. Run with `./program`. For shell scripts, save as `.sh`, then run `chmod +x file.sh` and `./file.sh`.
6. Install required tools as needed, for example `sudo apt update && sudo apt install build-essential tree -y`. Practical 23 additionally requires Docker.

## Upload to GitHub

Create a new GitHub repository, extract this ZIP, then run from this folder:

```bash
git init
git add .
git commit -m "Add all 23 Operating Systems practicals"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

Replace the remote URL with your own repository URL.

## Important note

The per-practical READMEs preserve the code and instructions from the PDF in text form. They are organized for GitHub browsing, but code snippets are not yet separated into individual `.c` and `.sh` source files.
