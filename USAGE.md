Output of `qr-backup --help`:

```
Usage: qr-codes.py [OPTIONS] FILE
Convert a binary file to a paper .pdf backup of QR codes.

The QR codes can be read back with a scanner or webcam to re-create the original file. Directions are included in the PDF. Make sure to test that you can actually read the QR size you select.

    --dpi DPI
        Sets the print resolution of your printer. Default: 600
    --compress, --no-compress
        This gives a more compact backup, but partial recovery is impossible. Turns base-64 encoding on. Default: compressed
    --error-correction CORRECTION
        Sets the error correction level. Options are L, M, Q, and H. Default: M (25%)
    --filename FILENAME
        Set the restored filename. Max 32 chars. Default: same as <FILE>
    --page WIDTH_POINTS HEIGHT_POINTS
        Sets the usable size of the paper on your printer. This should NOT be 8.5 x 11 -- make sure to include margins. Default: 500x600
    --qr-version VERSION
        Uses QR codes, version VERSION. Versions range from 1-40. The bigger the version, the harder to scan but the more data per code. Default: 10
    --scale SCALE
        Scale QR codes so that each small square in the QR code is SCALE x SCALE pixels. Default: 8
    --base64
        Force base64 encoding. Default: turned on if needed
    --verbose, -v
        Print more detailed information during run

The QR mode is always binary with no QR compression.

The output is named <FILE>.qr.pdf. You can also pipe stdout.
```
```
