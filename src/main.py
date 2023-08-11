import argparse
from builder import RepertoireBuilder
from config import Config


def main():
    args = docopt(doc)
    filename = args['<config_file>']

    config = Config(filename)

    builder = RepertoireBuilder(config)
    builder.GenerateReportoire()


if __name__ == '__main__':
    main()