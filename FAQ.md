# Questions

- [How much data does this back up per page / why don't you back up more data per page?](#how-much-data-does-this-back-up-per-page)
- [How do I back up more data per page?](#how-do-i-back-up-more-data-per-page)
- [How much of my backup can I lose and still restore?](#how-much-of-my-backup-can-i-lose-and-still-restore)
- [Do you support Windows / why don't you support Windows?](#why-dont-you-support-windows)
- [Do you support mac/OS X?](#why-dont-you-support-macos-x)
- [Why doesn't the restore process use qr-backup?](#why-doesnt-the-restore-process-use-qr-backup)
- [How exactly does the backup/restore process work?](#how-exactly-does-the-backuprestore-process-work)
- [Should I encrypt (password-protect) my backups?](#should-i-encrypt-password-protect-my-backups)
- [How can I protect my paper backup?](#how-can-i-protect-my-paper-backup)
- [What are the design goals of qr-backup?](#what-are-the-design-goals-of-qr-backup)
- [How do I find the maximum dimensions of my printer?](#how-do-i-find-the-maximum-dimensions-of-my-printer)
- [When I print a page, part of it is cut off](#when-i-print-a-page-part-of-it-is-cut-off)
- [How do I back up multiple files?](#how-do-i-back-up-multiple-files)

# Answers

## How much data does this back up per page?
qr-backup on default settings backs up about 3KB/page. This is about the same as written text in a small font--maybe a little worse.

I picked these settings by experimenting with the restore process on my computer. If I use higher-data codes, or make the QRs physically smaller, zbarcam couldn't consistently recognize them with my webcam.  That said, you're welcome to see if your computer can [handle more](#how-do-i-back-up-more-data-per-page).

## How do I back up more data per page?
Sure, maybe you have a better webcam/scanner than I do. Past that, you can just shove more data in, but there will be costs to doing so (you'll lose other benefits).

- Test your restore! I tried making the default settings more aggressive, but I actually can't scan smaller QR codes on my laptop.
- Print double-sided
- Print smaller. Reduce the scale with `--scale <scale>` (default 8, min 1).
- Use higher-data QR codes with `--qr-version <version>`` (default 10, max 40). Bigger codes doesn't always mean more data, because bigger codes don't always fit on the page. Pass `-v` to see how many KB/page you're getting. 
- Reduce error correction using `--error-correction L`. This makes your backup more sensitive to things like paper folds and dirt.
- [Maximize](#how-do-i-find-the-maximum-dimensions-of-my-printer) your page size
- Test and restore using a high-quality scanner, not a webcam.
- Use a different program. Ultimately, this is designed to make restores easy, not to pack data in as densely as posible. [PaperBack](http://ollydbg.de/Paperbak/) by OllyDbg claims to achieve 1-2MB per page, but requires Windows and a high-quality scanner. I have not been able to test the program myself.

## How much of my backup can I lose and still restore?
If you lose one page, or even one QR code (like if it's torn off or you spill grape juice), you're hosed. You won't be able to restore. If some dirt gets on a QR code, you'll be fine (QR codes have some error correction).

There are some command-line options that reduce the damage:

- `--num-copies` prints duplicates of QR codes. If you're printing duplicates, I recommend three copies (rather arbitrarily).
- `--no-compress` disables compression. This makes the backup longer, but it means that if you have 50% of the data, you can recover 50% of the file. For some backup types (text documents) this is useful. For others (bitcoin wallets) it is not. Make sure your document doesn't contain weird characters (including "\r", the mac/windows newline), or base64 encoding will turn on, which makes recovery harder.
- There is an open [feature request](https://github.com/za3k/qr-backup/issues/2) to improve this and let you lose some QR codes.

## Why don't you support windows?
I might someday, I just haven't done it yet.

- I don't use Windows myself
- I want the restore process to work WITHOUT qr-backup software. I'm not sure how to do this on Windws yet.

In the meantime, you could try [PaperBack](http://ollydbg.de/Paperbak/) by OllyDbg which works only on Windows. I have not used the program myself.

## Why don't you support mac/OS X?
Both backup and restore probably work, actually, it's just not tested. `brew install zbar` and let me know in the issue tracker.

## Why doesn't the restore process use qr-backup?
Because I want the restore process to work when qr-backup has been lost to history. Also, I want users to understand how the backup/restore process works.

## How exactly does the backup/restore process work?
The exact commands to run are described in the README and on the printed backup. But here's a conceptual explanation of how things work.

The backup process:
- If compression is on, data is compressed using gzip
- If base64-encoding is needed (compression is on, or the file contains unusual characters, or the command line option is set) then the data is base64 encoded to turn it into normal-looking ascii.
- The data is now preprocessed.
- The data is split into small chunks, about 2K each with the default settings. If there are 50 cunks, the number 01 thru 50 is put at the start of each chunk, to label them.
- Each chunk is printed as a QR code on the paper, and labeled with the code number.

The restore process is
- First, the user scans each QR code (in any order). Since each code contains the code number (01-50), the computer sorts everything out, making sure each code 01-50 is present exactly once.
- The codes are put in order (and duplicates removed). The 01-50 labels are removed, and the chunks are appended together.
- The chunks are appended together. This has restored the preprocessed data.
- If the data was base64-encoded, it's now base64-decoded
- If the data was compressed, it's now decompressed
- The file is now restored.
- The file is checksummed using sha256, which verifies the file is perfectly restored.

## Should I encrypt (password-protect) my backups?
That's up to you. 

I don't, because I think it's likely that I'll forget my password in 5-10 years. But, I'm not backing up my bitcoin wallet either.

There is an open [feature request](https://github.com/za3k/qr-backup/issues/4) to add this to qr-backup directly. Until then, if you want to password-protect your backup, you'll need to do it yourself. I'd use `gpg --symmetric` to encrypt and `gpg --decrypt` to decrypt (because gpg is widely available). 

If you do need to encrypt your backup, remember that you can write your password down (somewhere different!) on physical paper. Preferably several places--you need to remember where it's written. 

The especially geeky can also look into Shamir's secret-sharing scheme, which can let you need any 3 out of 4 pieces of information to restore. Remember to test your restore as usual.

## How can I protect my paper backup?
Before anything else, test that your restore procedure works. I advise (in order): 

- Document that you have a backup, what exactly of, and where it is. If you forget about your backup, it won't matter. If people other than you should know about the backup, tell them.
- Make several copies in different buildings/cities. More copies is simply better than one well-protected copy. Making multiple copies in the same place is a bit better than nothing.
- Protect against folding. At least on my scanner, folds really mess up the restore.
- If you're backing up something like pictures or text documents, print them. That way you have the data even if the restore process somehow fails (solar flare takes out most computers, etc). It's okay to print them very small, especially for text.
- Protect against water damage.
- Use acid-free paper. I don't imagine inkjet vs laser printer is that important, but I'm not an expert.
- Protect against fire damage. Again, the best way to protect against fire damage is to have a copy in another building.

## What are the design goals of qr-backup?
Okay, you caught me, no one has asked this, it's not really an FAQ.

- Restore should not require qr-backup, or any other unusual software. (Unfortunately there is no installed-by-default qr reader on Linux, but that's the only requirement)
- It should be very easy to restore the backup
- It should actually work, on my actual computer, on default settings
- It should be black-and-white
- An average human being should be able to follow the restore directions (this is not really true currently, but an average command-line Linux user can)

## How do I find the maximum dimensions of my printer?
If you really want to squeeze things in, you need to know how large you can print on a page.
There are two options.

- Experiment (using --page and --dpi)
- Try to figure it out from CUPS.

If you want to figure it out from CUPS, here's what I did:
1. On CUPS, check out the PPD file for your printer. The Debian wiki has useful information about PPDs.
2. Use the ImageableArea for the paper size you want. Subtract the two pairs of numbers--this is the usable size of the page (in 'points', or 1/72 of an inch).

## When I print a page, part of it is cut off
You may need to adjust the dimensions of your printer (or paper size, are you using A4 instead of US letter?).

If you adjust your page dimensions to be smaller, and it works... but the QR codes are suddenly misaligned from your failing print by a small amount, you've hit a printing bug with full-size pages. You need to upgrade Ghostscript to 9.50 or later.

## How do I back up multiple files?
1. You can run `qr-backup` multiple times, and print each PDF. If you lose any of the QR codes, you won't be able to restore that file.
2. OR, you can tar/zip the files, and back up the tar/zip. If you lose any of the QR codes, you won't be able to restore **any** of the files.
