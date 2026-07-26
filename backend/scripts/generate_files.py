import argparse
import os
import random
import string
import uuid

from file_catalog.config import Config
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

    for i in range(args.count):
        with open(config.FILES_DIR / f'{uuid.uuid4()}.txt', 'w') as file:
            content = ''.join(
                [random.choice(string.digits) for _ in range(FILE_LENGTH)]
            )
            file.write(content)

    print(f'Generated {args.count} files')


if __name__ == '__main__':
    main()
