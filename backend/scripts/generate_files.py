import argparse
import os

from file_catalog.config import Config
from file_catalog.db import generate_files
from file_catalog.di.container import container

FILE_LENGTH = 500


def main() -> None:
    print('Generating files...')
    config = container.get_sync(Config)

    parser = argparse.ArgumentParser(description='Generate random .txt files')
    parser.add_argument(
        '--count', type=int, default=3, help='Number of files to generate'
    )
    args = parser.parse_args()

    os.makedirs(config.FILES_DIR, exist_ok=True)
    generate_files(
        args.count, file_length=FILE_LENGTH, files_dir=config.FILES_DIR
    )
    print(f'Generated {args.count} files')


if __name__ == '__main__':
    main()
