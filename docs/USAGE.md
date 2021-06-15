Output of `qr-backup --help`:

```
Usage: qr-codes.py [OPTIONS] FILE
               qr-codes.py --restore [OPTIONS]
               qr-codes.py --restore [OPTIONS] IMAGE [IMAGE ...]
Convert a binary file to a paper .pdf backup of QR codes. With '--restore', read the QR codes in the paper backup using a webcam or scanner, to re-create the original file.

Restore directions are included in the PDF, and do not require qr-backup. Make sure to test that you can actually read the QR size you select.

Backup options:
    --dpi DPI
        Sets the print resolution of your printer. Default: 600
    --compress, --no-compress
        This gives a more compact backup, but partial recovery is impossible. Default: compressed
    --error-correction CORRECTION
        Sets the error correction level. Options are L, M, Q, and H. Default: M (25%)
    --filename FILENAME
        Set the restored filename. Max 32 chars. Default: same as <FILE>
    --output FILENAME, -o FILENAME
        Set the output pdf path (redirecting stdout also works). Default: <FILE>.qr.pdf
    --page WIDTH_POINTS HEIGHT_POINTS
        Sets the usable size of the paper on your printer. This should NOT be 8.5 x 11 -- make sure to include margins. Default: 500x600
    --qr-version VERSION
        Uses QR codes, version VERSION. Versions range from 1-40. The bigger the version, the harder to scan but the more data per code. Default: 10
    --scale SCALE
        Scale QR codes so that each small square in the QR code is SCALE x SCALE pixels. Default: 8

Restore options:
    --code-count COUNT, -c COUNT
        Specify the number of total QR codes. Default: automatic
    --compress, --no-compress
        Force decompression (on/off). Default: automatic
    --image-restore
        Force image-based (scanner) restore. Default: automatic
    --display, --no-display
        For webcam scanning, (display/don't display) a webcam preview. Default: display
    --output FILENAME, -o
        Set the restore file path. Default: stdout
    --sha256 SHA256
        Include a sha256sum to check the file. Default: no check, prints checksum
    --webcam-restore
        Force webcam-based restore. Default: automatic

Options for both:
    --verbose, -v
        Print more detailed information during run

The QR mode is always binary with no QR compression.
```
