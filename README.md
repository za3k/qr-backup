(Not done) Generate paper backups.

Takes a binary file, and outputs a "paper backup": a printable pdf full of QR codes. 

Following the directions in the pdf, the QR codes can be re-scanned or photographed using a webcame to restore the original file.

To make a paper backup:

0. Requirements: python, python-qrcode, imagemagick, img2pdf; a printer
1. Run `qr-backup <FILE>`. This makes `<FILE>.qr.pdf`
2. Print `<FILE>.qr.pdf` onto some paper. Now you have a backup. It's a bunch of QR codes and some instructions.

To restore from a paper backup:

0. Requirements: zbar; a video camera, image camera, or scanner
1. Using the provided directions in the backup
    - Use a webcam and `zbarcam` to scan the QR codes. 
    - OR, use `zbarimg` and a scanner to scan the QR codes.
3. Run the provided command. Now you have your original file.
4. Verify your file was restored perfectly (using the included checksum).
