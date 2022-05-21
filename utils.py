from deta import Deta
from os import environ


deta = Deta(environ['DETA_API_KEY'])

def get_db(table='users'):
    # return deta.Base(table, 'airdrop')
    return deta.Base('airdrop_'+table.strip())

