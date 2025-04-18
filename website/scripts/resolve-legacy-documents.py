#!/usr/bin/env python3

import os
from pathlib import Path

SCRIPTDIR = Path(__file__).parent.resolve()
CWD = Path.cwd().resolve()
PATH_S3FILES = Path(CWD, 'resources/s3-pdf-resources.txt')
PATH_WAGTAILDOCS = Path(SCRIPTDIR, '..', 'home/management/documents' )

def is_file_in_path(filename, target_path):
    target = Path(target_path)
    return any(file.name == filename for file in target.rglob('*') if file.is_file())


def list_common_docs():
  """iterate through rapidweaver file listing, show weather they exist in wagtail_docs"""
  with open(PATH_S3FILES, 'r') as file:
    lines = file.readlines()
    print('filename, relative_url, in_wagtail')
    for line in (line.strip() for line in lines):
      filepath = Path(line)
      filename = filepath.name
      present = is_file_in_path(filename, PATH_WAGTAILDOCS)
      print(f'{filename}, {filepath}, {present}')


def list_missing_docs():
  with open(PATH_S3FILES, 'r') as file:
    lines = file.readlines()
    print('filename, relative_url, in_wagtail')
    for line in (line.strip() for line in lines):
      filepath = Path(line)
      filename = filepath.name
      present = is_file_in_path(filename, PATH_WAGTAILDOCS)
      if not present:
        print(filepath)


    
def main():
  list_common_docs()


if __name__ == "__main__":
  main()