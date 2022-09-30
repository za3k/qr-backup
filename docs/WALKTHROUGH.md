## Making a backup
1. Run qr-backup on your file. On the Linux command-line, run `qr-backup <YOUR_FILE>`
2. This generates a black-and-white PDF (`<YOUR_FILE>.qr.pdf`)
3. Print the PDF on your printer

There are many command-line options available for advanced users. For a full list, read the [USAGE](docs/USAGE.md) doc online, or run `qr-backup --help` on your computer.

## Restoring a paper backup
The restore process **does NOT require qr-backup**. It does require a command-line Linux computer.

(Option 1): Use qr-backup, if you have it.
- Webcam option
    1. Run `qr-backup --restore`
- Scanner option
    1. Scan images using your scanner
    2. Run `qr-backup --restore IMAGES`

(Option 2): Use the linux command line, if you lose qr-backup. Commands are provided in the PDF printout. You will need to install `zbar`.

