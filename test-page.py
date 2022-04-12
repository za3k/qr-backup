#!/usr/bin/env python3
"""
Output a "test sheet" of scale and QR version sizes. Varying error correction (L/M/H/Q) might be worthwhile, but it's too many factors, so I kept it to the basics.

Add a symlink qr-backup -> qrbackup.py to use
"""
import PIL, PIL.Image, PIL.ImageDraw, PIL.ImageFont, PIL.ImageOps
import english_wordlist
import base64, datetime, gzip, hashlib, io, logging, math, os, random, subprocess, sys, textwrap, qrcode
assert sys.version_info >= (3,6), "Python 3.6 is required. Submit a patch removing f-strings to fix it, sucka!"


from qrbackup import *

# Defaults, not configurable
PAGE_W_POINTS, PAGE_H_POINTS = 500,600
DPI=300
ERROR_CORRECTION = M # default, 25%
QR_VERSIONS = [2,3,4,5,6,7,8,9,10,12,14,16,18,20,25,30,35,40]
SCALES = [1,2,3,4,5,6,7,8]

EXAMPLE_DATA = b"test"
PAGE_W_PIXEL, PAGE_H_PIXEL = math.floor(PAGE_W_POINTS/72.0*DPI), math.floor(PAGE_H_POINTS/72.0*DPI)

lookup = {}
samples = []
for qr_version in QR_VERSIONS:
    for scale in SCALES:
        # Figure out size of one QR code
        #digits, padding, example_qrs = qr_codes(EXAMPLE_DATA, error_correction=ERROR_CORRECTION, version=qr_version, scale=scale)
        #assert len(example_qrs) == 1, qr_version
        #qr_w_pixel, qr_h_pixel = example_qrs[0].make_image().copy().size
        qr_w_pixel = scale*qr_grid_size(qr_version)
        qr_h_pixel = qr_w_pixel
        padding=4*scale
        
        # Calculate number of QRs that can fit on a page
        qrs_per_page_w = max_units_with_padding(PAGE_W_PIXEL, qr_w_pixel, padding)
        qrs_per_page_h = max_units_with_padding(PAGE_H_PIXEL, qr_h_pixel, padding)
        qrs_per_page = qrs_per_page_w*qrs_per_page_h
        if qrs_per_page < 6:
            continue

        # Calculate characters per QR
        chars_per_qr = qr_size_chars(qr_version, QR_MODE, ERROR_CORRECTION) - 5

        # Calculate overall density
        density = chars_per_qr * qrs_per_page
        if density < 8000:
            continue
        print(density, ERROR_CORRECTION, qr_version, scale)

        # Make an image the encodes the result
        real_data = f"{density} {ERROR_CORRECTION} {qr_version} {scale}".encode("ascii")
        qr = qrcode.QRCode(
            version=qr_version,
            error_correction=ERROR_CORRECTION,
            box_size=scale,
        )
        qr.add_data(qrcode.util.QRData(real_data, mode=QR_MODE), optimize=0)
        qr.make(fit=False)

        # Store the result
        samples.append((qr_version, scale, qr_w_pixel+padding*2, density, qr))

samples.sort(key=lambda x: (x[2], x[3]))
rows = []

row = []
row_size = 0
for qr_version, scale, qr_w_pixel, density, qr in samples:
    if row_size + qr_w_pixel < PAGE_W_PIXEL:
        row.append(qr.make_image())
        row_size += qr_w_pixel
    else:
        print("row: ", len(row))
        rows.append(h_merge(row))
        row, row_size = [qr.make_image()], qr_w_pixel

pages = []

page = []
page_size = 0
for row in rows:
    if page_size + row.size[1] < PAGE_H_PIXEL:
        page.append(row)
        page_size += row.size[1]
    else:
        print("page: ", len(page))
        pages.append(v_merge(page))
        page, page_size = [row], row.size[1]

# Make everything uniform page size
for i, page in enumerate(pages):
    final_page = PIL.Image.new(mode="L", size=(PAGE_W_PIXEL, PAGE_H_PIXEL), color=255)
    final_page.paste(page, (0,0))
    pages[i] = final_page

print("num pages: ", len(pages))

pages[0].save("test.pdf", format="pdf", save_all=True, append_images=pages[1:], resolution=DPI, producer="qr-backup", title=f"qr-backup test print page")
