Generate paper backups for Linux. Currently **command-line Linux only**.

**qr-backup** takes file(s), and outputs a "paper backup": a printable black-and-white pdf full of QR codes. To back up your file, print the PDF. The pile of paper in your hand is now a backup of the file.

If your file is lost, corrupted, deleted, etc, you can restore from your paper backup. qr-backup reads the [QR barcodes](https://en.wikipedia.org/wiki/QR_code) using your computer's webcam (or scanner) to get your file back.

## Example Backup
![Example Backup](docs/example.png)

## Features
- Restore without qr-backup installed (!)
- Restore using webcam
- Restore using scanner
- Clear, printed instructions on what the file is and how to restore
- Automatic compression
- 3KB/page on default settings. Single-digit MB backups of text are practical
- (Optional) Password protection
- (Optional) Print multiple copies for safety
- (Optional) Print smaller, denser codes to boost storage, up to 100KB/page
- (Restore with qr-backup only) Automatic redundancy. Lose up to 20% of pages or QR codes safely
- See [Command Line Options](docs/USAGE.md) for more

## [Install Guide](docs/INSTALL.md)
## [How to Use](docs/WALKTHROUGH.md)
## [Command Line Options](docs/USAGE.md)
## [FAQ](docs/FAQ.md)
