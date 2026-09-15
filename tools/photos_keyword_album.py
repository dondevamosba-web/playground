#!/usr/bin/env python3
"""Add photos whose OCR/search text matches keywords to a Photos album.

Usage: photos_keyword_album.py "Album Name" keyword1 keyword2 ...
Matches groups.normalized_string prefix-wise (keyword*) in psi.sqlite,
converts asset ids to Photos UUIDs (little-endian), skips trashed assets,
then calls tools/photos_add_to_album.sh.
Note: psi.sqlite OCR index is built by Photos' background analysis —
rerun after analysis completes to pick up newly indexed photos.
"""
import sqlite3, struct, uuid, os, sys, subprocess, tempfile

album = sys.argv[1]
keywords = [k.lower() for k in sys.argv[2:]]
home = os.path.expanduser('~')
lib = f"{home}/Pictures/Photos Library.photoslibrary/database"

psi = sqlite3.connect(f"file:{lib}/search/psi.sqlite?mode=ro", uri=True)
clauses = " OR ".join(["g.normalized_string LIKE ?"] * len(keywords))
rows = psi.execute(
    f"SELECT DISTINCT a.uuid_0, a.uuid_1 FROM ga "
    f"JOIN groups g ON g.rowid=ga.groupid JOIN assets a ON a.rowid=ga.assetid "
    f"WHERE {clauses}", [k + '%' for k in keywords]).fetchall()
uuids = [str(uuid.UUID(bytes=struct.pack('<qq', u0, u1))).upper() for u0, u1 in rows]

ph = sqlite3.connect(f"file:{lib}/Photos.sqlite?mode=ro", uri=True)
valid = [u for u in uuids if ph.execute(
    "SELECT 1 FROM ZASSET WHERE ZUUID=? AND ZTRASHEDSTATE=0", (u,)).fetchone()]
print(f"{len(valid)} assets match {keywords}")
if not valid:
    sys.exit(0)

f = tempfile.NamedTemporaryFile('w', suffix='.txt', delete=False)
f.write("\n".join(valid) + "\n"); f.close()
script_dir = os.path.dirname(os.path.abspath(__file__))
subprocess.run([f"{script_dir}/photos_add_to_album.sh", f.name, album])
