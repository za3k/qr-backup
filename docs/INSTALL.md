# Arch Linux
    yay -S qr-backup`

# Other Linux
1. Install dependencies (see below)
2. Run the following:

```
git clone https://github.com/za3k/qr-backup.git
cd qr-backup
sudo make install
```

## Dependencies
### Backup Requirements
- **A Linux computer and knowledge of how to use the command line**
- A printer
- python 3.6 or later
- python-qrcode
- python-reedsolo
- python-pillow
- imagemagick
- zbar (optional, used to digitally test restore)
- the DejaVu Sans font (fonts-dejavu on debian,  ttf-dejavu on arch. included.)
- gpg (if making an encrypted backup)
### Restore Requirements
- **A Linux computer and knowledge of how to use the command line**
- **The restore process works without qr-backup installed**
- A webcam or scanner
- imagemagick
- zbar
- python-reedsolo (if using qr-restore)
- gpg (if restoring an encrypted backup)
