import argparse

from builder import RepertoireBuilder
from config import Config


def main():

    parser = argparse.ArgumentParser(
        description="Generate repertoire using YAML configuration file.")
    parser.add_argument('config_file', help="Path to YAML configuration file")
    parser.add_argument('--plot', action='store_true', default=False,
                        help="Print live repertoire stat plots")
    parser.add_argument(
        '--adaptive',
        action='store_true',
        default=False,
        help="Reduce gradually the FreqThreshold as a function of the depth reached")
    args = parser.parse_args()

    config = Config(args.config_file)
    options = {'plot': args.plot,
               'adaptive': args.adaptive}

    builder = RepertoireBuilder(config, options)
    builder.GenerateReportoire()


if __name__ == '__main__':
    main()
