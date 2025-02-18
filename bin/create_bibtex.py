#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2019 Marcel Bollmann <marcel@bollmann.me>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Usage: create_bibtex.py [--importdir=DIR] [--exportdir=DIR] [-c] [--debug]

Creates .bib files for all papers in the Hugo directory.

Options:
  --importdir=DIR          Directory to import XML files from. [default: {scriptdir}/../data/]
  --exportdir=DIR          Directory to write exported files to.   [default: {scriptdir}/../build/data-export/]
  --debug                  Output debug-level log messages.
  -c, --clean              Delete existing files in target directory before generation.
  -h, --help               Display this helpful text.
"""

from docopt import docopt
from lxml import etree
from tqdm import tqdm
import gzip
import logging as log
import io
import os

from anthology import Anthology
from anthology.utils import SeverityTracker
from create_hugo_pages import check_directory


def create_bibtex(anthology, trgdir, clean=False):
    """Creates .bib files for all papers."""
    if not check_directory("{}/papers".format(trgdir), clean=clean):
        return
    if not check_directory("{}/volumes".format(trgdir), clean=clean):
        return

    log.info("Creating BibTeX files for all papers...")
    with gzip.open(
        "{}/anthology.bib.gz".format(trgdir), "wt", encoding="utf-8"
    ) as file_full:
        for volume_id, volume in tqdm(anthology.volumes.items()):
            volume_dir = trgdir
            if not os.path.exists(volume_dir):
                os.makedirs(volume_dir)
            with open(
                "{}/volumes/{}.bib".format(trgdir, volume_id), "w"
            ) as file_volume:
                for paper in volume:
                    with open(
                        "{}/{}.bib".format(volume_dir, paper.full_id), "w"
                    ) as file_paper:
                        contents = paper.as_bibtex()
                        file_paper.write(contents)
                        file_paper.write("\n")
                        concise_contents = paper.as_bibtex(concise=True)
                        file_volume.write(concise_contents)
                        file_volume.write("\n")
                        file_full.write(concise_contents)
                        file_full.write("\n")


if __name__ == "__main__":
    args = docopt(__doc__)
    scriptdir = os.path.dirname(os.path.abspath(__file__))
    if "{scriptdir}" in args["--importdir"]:
        args["--importdir"] = os.path.abspath(
            args["--importdir"].format(scriptdir=scriptdir)
        )
    if "{scriptdir}" in args["--exportdir"]:
        args["--exportdir"] = os.path.abspath(
            args["--exportdir"].format(scriptdir=scriptdir)
        )

    log_level = log.DEBUG if args["--debug"] else log.INFO
    log.basicConfig(format="%(levelname)-8s %(message)s", level=log_level)
    tracker = SeverityTracker()
    log.getLogger().addHandler(tracker)

    anthology = Anthology(importdir=args["--importdir"])
    create_bibtex(anthology, args["--exportdir"], clean=args["--clean"])

    if tracker.highest >= log.ERROR:
        exit(1)
