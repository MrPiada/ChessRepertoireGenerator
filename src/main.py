import argparse
from builder import RepertoireBuilder
from config import Config


def main():
    parser = argparse.ArgumentParser(
        description="Generate repertoire using YAML configuration file.")
    parser.add_argument('config_file', help="Path to YAML configuration file")
    args = parser.parse_args()
    print(f"\nARGS: {args}")
    filename = args.config_file

    config = Config(filename)

    builder = RepertoireBuilder(config)
    stats = builder.GenerateReportoire()


if __name__ == '__main__':
    main()
