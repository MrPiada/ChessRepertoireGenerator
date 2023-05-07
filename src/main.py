from docopt import docopt
from config import Config
from myclass import MyClass

doc = """Usage:
    main.py <config_file>

Arguments:
    <config_file>   Path to YAML configuration file
"""


def main():
    # Legge i parametri di input utilizzando docopt
    args = docopt(doc)

    # Ottiene il percorso del file di configurazione dal parametro di input
    filename = args['<config_file>']

    # Istanzia un oggetto di configurazione dal file YAML
    config = Config(filename)

    # Costruisce un'istanza di MyClass con l'oggetto di configurazione
    my_object = MyClass(config)

    # Esegue la funzione compute dell'oggetto MyClass
    my_object.compute()


if __name__ == '__main__':
    main()
