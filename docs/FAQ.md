# Questions

### Paper Backups
- [Should I back up to paper?](#should-i-back-up-to-paper)
- [What are the advantages of paper backups?](#what-are-the-advantages-of-paper-backups)
- [How much of my backup can I lose and still restore?](#how-much-of-my-backup-can-i-lose-and-still-restore)
- [Should I encrypt (password-protect) my backups?](#should-i-encrypt-password-protect-my-backups)
- [How can I protect my paper backup?](#how-can-i-protect-my-paper-backup)

### Features
- [Do you support Windows?](#do-you-support-windows)
- [Do you support mac/OS X?](#do-you-support-macos-x)
- [How much data does this back up per page / why don't you back up more data per page?](#how-much-data-does-this-back-up-per-page)
- [How do I back up more data per page?](#how-do-i-back-up-more-data-per-page)
- [Why did you write qr-backup?](#why-did-you-write-qr-backup)
- [Why doesn't the restore process require qr-backup?](#why-doesnt-the-restore-process-require-qr-backup)
- [How exactly does the backup/restore process work?](#how-exactly-does-the-backuprestore-process-work)
- [What are the design goals of qr-backup? / Why won't you add the feature I want?](#what-are-the-design-goals-of-qr-backup)
- [What license is qr-backup released under?](#what-license-is-qr-backup-released-under)

### Competition
- [What other paper backup projects exist?](#what-other-paper-backup-projects-exist)
- [How does qr-backup compare to OllyDbg's Paperback?](#how-does-qr-backup-compare-to-ollydbgs-paperback)

### Usage
- [How do I back up multiple files?](#how-do-i-back-up-multiple-files)
- [Why does qr-backup restore to stdout? / why doesn't qr-backup extract tar files?](#why-does-qr-backup-restore-to-stdout-rather-than-the-original-filename)

### Troubleshooting
- [My self-test is failing on Ubuntu](#my-self-test-is-failing-on-ubuntu)
- [How do I find the maximum dimensions of my printer?](#how-do-i-find-the-maximum-dimensions-of-my-printer)
- [When I print a page, part of it is cut off](#when-i-print-a-page-part-of-it-is-cut-off)
- [When I print the backup, the last page is rotated](#when-i-print-the-backup-the-last-page-is-rotated)

## Paper Backups

### Should I back up to paper?
Possibly. You should still back it up to something more usual like a USB thumbstick *first*, because it's easier to restore and update.

Common files to back up are small important records, and small secret files. Examples include: a diary, an address book, a short story you wrote, financial records, medical records, an ssh or gpg cryptographic key, or a cryptocurrency (bitcoin) wallet.

Paper is not the best or most efficient storage method, so you can't back up big files. 10KB or 100KB files is a reasonable limit.

### What are the advantages of paper backups?
- It's easy to think about physical stuff. Everyone can understand whether they still have a backup (by looking), whether it's damaged (by looking), and who can access their backup.
- Paper can't be hacked. It's easy to think about who can access a paper backup compared to an online computer. Paper backups are a popular option to store GPG keys, SSH keys, crypto wallets, or encrypted messages for this reason.
- It's fun. A lot of people make paper backups for the novelty factor.
- Paper lasts a long time. CDs and flash-based storage (USB drives, SD cards, and many modern hard drives) usually stop working within 10 years. Magnetic storage works for a fairly long time unless it is damaged.
- Paper has no parts that can break. It's common for hard drives to break, and for the data inside to become unreadable, even though the data is still okay.
- Damage is visible. Sometimes a flash drive can be silently corrupted, or a drive's parts will break, but it looks OK. You can look at paper and whether it's damaged, and how much damage there is.

### How much of my backup can I lose and still restore?
Depends.

**New in v1.1**: If you restore using qr-backup, you can lose roughly 30% of the pages or QR codes, no more. Call it 20% to be safe.

If you don't have qr-backup, it's more fragile. If you lose one QR code, you're hosed. You won't be able to restore. If some dirt, a pen mark, etc gets on a QR code, you'll be fine.

There are some command-line options that reduce the damage:
- `--num-copies` prints duplicates of QR codes. If you're printing duplicates, I recommend three copies (rather arbitrarily).
- `--no-compress` disables compression. This makes the backup longer, but it means that if you have 50% of the data, you can recover 50% of the file. For some backup types (text documents) this is useful. For others (bitcoin wallets) it is not.
- `--shuffle`, which is on by default, randomly re-orders codes. This helps if you are restoring with qr-backup. Erasure codes can only cover up to 256 QRs, so large files (>20KB) are split into sets of codes. If you lose 30% of codes from one set, you lose data. To combat this, qr-backup orders codes randomly by default, so you're unlikely to lose many codes from the same set.

### Should I encrypt (password-protect) my backups?
That's up to you. I don't, because I think it's more likely I'll forget my password than have someone steal my papers.

### How can I protect my paper backup?
In order:
- Test that your restore procedure works. Seriously, do that first.
- The most common failure mode for paper backups is to *forget* about your backup or throw it out accidentally.
    - On each copy of the backup, document what it is. You can hand-write or attach a cover sheet.
        - Who you are, and several forms of contact information (phone, address, email, contact info of family, friends, or your place of work)
        - Why it shouldn't be thrown out (or when it should be).
        - What exactly this backup is (what's in the file, but also that this is a physical backup of computer data)
        - Where any other copies are, in case this one is damaged
    - If people other than you should know about the backup, tell them. If anyone would throw this away, tell them not to.
    - Wherever you normally keep your reminders, document that you have a backup, what exactly of, and where it is.
- If you encrypt your backup, write down your password, and store it *somewhere else* you won't forget.
- Make several copies in different buildings/cities. More copies is simply better than one well-protected copy.
- Protect against folding and losing pages. A box or envelope may help. Folding on a QR code can make it unreadable, and losing a page means you lose your data.
- If you're backing up something like pictures or text documents, print them and attach them to the qr-backup paper backup. That way you have the data even if the restore process somehow fails.
- Protect against water damage.
- Use acid-free paper. I don't imagine inkjet vs laser printer is that important, but I'm not an expert.

Protecting against fire damage is not worthwhile.

## Features

## Do you support windows?
Not yet. It's on the [roadmap](https://github.com/za3k/qr-backup/issues/30).

In the meantime, you could try [a different paper backup program](#what-other-paper-backup-projects-exist).

## Do you support mac/OS X?
Maybe. Please try installing it and let me know.

### How much data does this back up per page?
qr-backup on *default* settings backs up at 3-4KB/page raw data (about 15KB/page english text).

At max settings, it backs up at 130KB/page raw (or 170KB/page raw with erasure coding disabled). I recommend against these settings. Your restore will fail unless you have an incredibly good scanner, and maybe even then.

Overall, qr-backup is focused on successful, easy restores. It's not focused on maximum density.

The basic answer to "why isn't qr-backup's density higher" is that a webcam's resolution is lower than a printer's resolution. qr-backup's default settings are meant to work for everyone. If you print a denser backup, some computers won't be able to restore it via webcam.

That said, if you only want to support your own webcam/scanner, you're welcome to try and [increase your data density](#how-do-i-back-up-more-data-per-page).

You can also try [another program](#what-other-paper-backup-projects-exist). Density-focused ones claim 100-300KB/page. 

### How do I back up more data per page?
Maybe you have a better webcam/scanner than I do, in which case you can increase settings. The only cost if that people with bad webcams like me can't restore your backup. Once you hit your webcam/scanner's limit, you can still shove more data in, but there will be cost tradeoffs as you lose reliability.

Before committing to a QR size and scale, test your restore with an actual webcam or scanner! Looking OK to your eyes is not enough.

Try these, from most effective to least:

- Print double-sided
- Print smaller. Reduce the scale with `--scale <scale>` (default 8, min 1).
- Use higher-data QR codes with `--qr-version <version>` (default 10, max 40). Bigger codes doesn't always mean more data, because bigger codes don't always fit on the page. Pass `-v` to see how many KB/page you're getting. 
- Reduce error correction using `--error-correction L`. This makes your backup more sensitive to things like paper folds and dirt.
- [Maximize](#how-do-i-find-the-maximum-dimensions-of-my-printer) your page size
- Test and restore using a high-quality scanner, not a webcam.
- (Last resort) Turn off erasure coding with `--no-erasure-coding`. This means losing a single QR code will hose your data.

You can also use a [different paper backup program](#what-other-paper-backup-projects-exist). Ultimately, qr-backup is designed to make restores easy, not to pack data in as densely as posible.

### Why did you write qr-backup?
I wrote it to back up my journal (about 2MB). I hope you'll find it useful too.

### Why doesn't the restore process require qr-backup?
Because that's awesome.

I want the restore process to work when qr-backup has been lost to history. Also, I want users to understand how the backup/restore process works.

### How exactly does the backup/restore process work?
The exact commands to run are described in the README and on the printed backup. But here's a conceptual explanation of how things work.

If find this explanation helpful, run qr-backup with the `--instructions both` option to add it to the paper backup.

The backup process:
- If you're backing up multiple files, everything is combined in a single tar file.
- A sha256 sum of the original file is printed on the paper.
- If compression is on, data is compressed using gzip
- If encryption is on, data is password-protected with GPG in symmetric mode.
- The length of the data is added at the beginning.
- The data is padded to make it a round number of chunks (see below)
- The data is now preprocessed.
- The data is split into small chunks, about 2K each with the default settings.
- We use erasure coding to generate redundant "parity chunks" from the normal chunks. This adds 42% more chunks.
- The QR codes are re-order randomly, to help prevent certain kinds of data loss.
- Each chunk is base64 encoded.
- Labels are added. If there are 50 chunks, the first is labeled "N01/50" and the last is "N50/50". Parity chunks are labeled "P01/21" through "P21/21".
- Each chunk is printed as a QR code on the paper, and labeled with the same code label.

The restore process is the same, but in reverse:
- First, the user scans each QR code (in any order). 
- Since each code contains the code number (01-50), the computer sorts everything out, making sure each code 01-50 is present exactly once. The codes are put in order (and duplicates removed).
- The "N01/50" thru "N50/50" labels are removed. Any chunk with an unexpected label is thrown out (for forwards compatibility).
- Each chunk is base64-decoded
- If any normal chunks are missing, we use erasure coding to restore missing normal chunks using parity chunks.
- The normal chunks are appended together.
- The data starts with a length. We remove this, and remove the padding at the end using the length information.
- This has restored the preprocessed data.
- If the data was encrypted, it is decrypted with GPG in symmetric mode.
- If the data was compressed, it's decompressed. The file is now restored.
- Any tar file is *not* decompressed (to avoid overwriting the original files)
- The file is checksummed using sha256, which verifies the file is perfectly restored.

### What are the design goals of qr-backup?
- It should be very easy to restore the backup
- It should actually work on my actual computer, on default settings
- It should actually work with low-quality hardware (ex bad black-and-white printer and bad webcam)
- Restore should not require qr-backup, or any other unusual software. (Unfortunately there is no installed-by-default qr reader on Linux, but zbar is the only requirement)
- An average human being should be able to follow the restore directions (this is not really true currently, but an average command-line Linux user can)
- The output should include good documentation

### What license is qr-backup released under?
I release qr-backup into the public domain. I release qr-backup under [CC0](https://creativecommons.org/share-your-work/public-domain/cc0/)

## Competition

### What other paper backup projects exist?
2D code based (like qr-backup):
- [qr-backup](https://github.com/za3k/qr-backup): This project. Based on QR codes. Focuses on easy restore using webcam and standard CLI tools. Low data density.
- [qrencode](https://fukuchi.org/works/qrencode/), etc: Small amount of data can be directly printed to one QR code, and restored by any QR scanner.
- [paperbackup](https://github.com/intra2net/paperbackup): Remarkably similar to qr-backup, down to the code format. Based on QR codes. Focused on GPG/SSH key backup. See also the [paperkey](http://www.jabberwocky.com/software/paperkey/) preprocessor.
- [asc2qr.sh](https://github.com/4bitfocus/asc-key-to-qr-code): QR-based, less polished.
- [qrpdf](https://github.com/EmperorArthur/qrpdf): QR-based, similar to qr-backup. May support parity encoding.
- [qrdump](https://github.com/jerabaul29/qrdump): **Incomplete** QR-based, similar to qr-backup.

Dense pixel grid (like Paperbak). Everything in this section needs a good scanner:
- Paperback [explanation](https://ollydbg.de/Paperbak/) and [code](https://github.com/Rupan/paperbak/) by OlyDbg: Much denser, windows-only. Uses reed-solomon codes.
- [paperback-cli](https://git.teknik.io/scuti/paperback-cli): Cross-OS port for OlyDbg's Paperbak program.
- [ColorSafe](https://github.com/colorsafe/colorsafe): Black and white or color output. Split into sectors. Error correction is reed-solomon within a sector, none outside (as best I could find out).
- [optar](http://ronja.twibright.com/optar/): Black and white. Uses Golay codes.

### How does qr-backup compare to OllyDbg's Paperback?
Paperbak was a well-known attempt to write data to paper as densely as possible.

First, here's what Paperback/Paperbak is:
- [Description](https://ollydbg.de/Paperbak/)
- [Original Code](https://github.com/timwaters/paperback )
- [Attempted Linux fork](https://github.com/cyphar/paperback)

Here's how they are similar/different
- Both have the same essential goal and flow: back some stuff up to paper and restore it later.
- Both are black-and-white only
- Paperbak is Windows-only; qr-backup runs on Linux command-line.
- Paperbak was last updated in 2002. qr-backup is maintained. I'm not super clear if Paperback still works end to end (I don't have Windows).
- Paperbak was an experiment/joke. qr-backup is designed for actual long-term backups.
- Paperbak is focused around shoving the most data on paper possible. qr-backup is focused on easy, futureproof restore that works.
- Paperbak needs Paperbak to restore. qr-backup only needs standard Linux tools (and a QR reader).
- Paperbak is needs a flatbed-quality scanner. qr-backup can use a webcam or any scanner.
- Paperbak's documentation throws out the figure 300KB/page. qr-backup on default settings stores [3KB/page](#how-much-data-does-this-back-up-per-page), although this can be increased to 130KB/page. Most of this is Paperbak requiring a good scanner, and qr-backup requiring an average webcam. QR, zbar, and qr-backup inefficiencies also contribute some.
- Paperbak uses a proprietary format, and needs Paperbak to restore. qr-backup uses an esoteric mix of existing formats like QR and gzip, and can be restored with a bash oneliner of standard linux tools.
- Both support compression.
- Both support encryption.
- Both support reed-solomon coding, so you can lose part of the page(s) and still restore.
- Both print some information about the file
- qr-backup prints an explanation about what a paper backup is, and how to restore it.
- Paperbak has only library dependencies. qr-backup has library and CLI dependencies (zbar, convert)
- Paperbak is not backwards-compatible, qr-backup is backwards-compatible

## Usage

### How do I back up multiple files?
1. **New in v1.1**: Run `qr-backup FILE1 FILE2 FILE3`.
2. **New in v1.1**: Run `qr-backup DIRECTORY`.
3. You can tar/zip the files yourself, and back up the tar/zip.
4. You can run `qr-backup` multiple times, and print each PDF.

In method 1-3, if you lose enough QR codes, you lose *all* the files.
In method 4, if you lose QR codes, you only lose that file.

### Why does qr-backup restore to stdout, rather than the original filename?
This avoids overwriting up the original files. For the same reason, multiple files are not automatically extracted

## Troubleshooting

## My self-test is failing on Ubuntu
The generated PDF is probably fine, but can't be read. Ubuntu has disabled ImageMagick working on PDFs for security reasons. This breaks qr-backup's self-test process. You have two options.

1. Disable or modify the security policy. Check out StackOverflow for information of [why](https://askubuntu.com/questions/1081895/trouble-with-batch-conversion-of-png-to-pdf-using-convert) and [how to disable it](https://askubuntu.com/questions/1127260/imagemagick-convert-not-allowed) if you want.
2. Test your restore by printing your backup.

## How do I find the maximum dimensions of my printer?
If you really want to squeeze things in, you need to know how large you can print on a page. There are two options to figure out the max print size.

- Recommended: Experiment (using `--page`)
- Calculate it from CUPS PPD files.

If you want to figure it out from CUPS, here's what I did:
1. On CUPS, check out the PPD file for your printer. The Debian wiki has useful information about PPDs.
2. Use the ImageableArea for the paper size you want. Subtract the two pairs of numbers--this is the usable size of the page (in 'points', or 1/72 of an inch, the same unit `--page` uses).

You can also mess with `--dpi` but it's unlikely to be your limiting factor.

## When I print a page, part of it is cut off
You may need to adjust the dimensions of your printer (or paper size, are you using A4 instead of US letter?).

If you adjust your page dimensions to be smaller, and it works... but the QR codes are suddenly misaligned from your failing print by a small amount, you've hit a printing bug with full-size pages. You need to upgrade Ghostscript to 9.50 or later.

I believe there is a remaining [issue](https://github.com/OpenPrinting/cups-filters/issues/373) in the new version, unfortunately.

## When I print the backup, the last page is rotated
Pass CUPS the option 'nopdfAutoRotate'.
