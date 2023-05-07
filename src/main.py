from docopt import docopt
from Config import Config
from Builder import RepertoireBuilder

doc = """Usage:
    main.py <config_file>

Arguments:
    <config_file>   Path to YAML configuration file
"""


def main():
    args = docopt(doc)
    filename = args['<config_file>']

    config = Config(filename)

    builder = RepertoireBuilder(config)
    builder.GenerateReportoire()


if __name__ == '__main__':
    main()
