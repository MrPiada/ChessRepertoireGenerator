import argparse
from Builder import RepertoireBuilder
from Config import Config

def main():
    parser = argparse.ArgumentParser(description="Generate repertoire using YAML configuration file.")
    parser.add_argument('config_file', help="Path to YAML configuration file")
    args = parser.parse_args()
    print(f"\nARGS: {args}")
    filename = args.config_file

    config = Config(filename)

    builder = RepertoireBuilder(config)
    builder.GenerateReportoire()

if __name__ == '__main__':
    main()