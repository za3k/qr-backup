# Install Guide
## Arch Linux
    yay -S qr-backup

## Other Linux
1. Install CLI dependencies: gnupg2, imagemagick, and zbar
2. Run the following:

```
git clone https://github.com/za3k/qr-backup.git
cd qr-backup
sudo pip install -r requirements.txt
sudo make install
```

## Dependencies
- **A Linux computer and knowledge of how to use the command line**
- gnupg2
- imagemagick
- zbar
- the DejaVu Sans Mono font (fonts-dejavu on debian,  ttf-dejavu on arch. included.)
- python 3.6 or later
- python-pillow
- python-qrcode
- python-reedsolo

### Restore without qr-backup
Restore works without qr-backup installed. It requires:

- **A Linux computer and knowledge of how to use the command line**
- A webcam or scanner
- imagemagick
- zbar
- gnupg2 (if restoring an encrypted backup)
