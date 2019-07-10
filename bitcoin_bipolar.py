import pickle
import signal
import time
from datetime import datetime

from money.currency import Currency
from money.money import Money

from bitcoin import valor_btc
from twitter import twittar


class GracefulKiller:
    kill_now = False

    def __init__(self):
        signal.signal(signal.SIGINT, self.exit_gracefully)
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.kill_now = True


if __name__ == '__main__':
    killer = GracefulKiller()
    while not killer.kill_now:
        try:
            with open('ultimo_valor.db', 'rb') as db:
                ultimo_valor = pickle.load(db)
        except FileNotFoundError:
            print('Rodando pela primeira vez.')
            valor_atual = valor_btc()
            with open('ultimo_valor.db', 'wb') as db:
                pickle.dump(valor_atual, db, protocol=pickle.HIGHEST_PROTOCOL)
        else:
            valor_atual = valor_btc()
            # detecta problema na API, dorme por 10 minutos e continua o loop
            if not valor_atual:
                time.sleep(600)
                continue
            diferenca = round(abs(valor_atual - ultimo_valor), 2)

            if diferenca > 500:
                valor_reais = Money(str(valor_atual), Currency.BRL).format(
                    'pt_BR')
                hora = datetime.now().strftime('%H:%M')

                if valor_atual > ultimo_valor:
                    msg = "Bitcoin subiu :) - {} às {}".format(valor_reais,
                                                               hora)
                    twittar(msg)
                    print(msg)
                elif ultimo_valor > valor_atual:
                    msg = "Bitcoin caiu :( - {} às {}".format(valor_reais, hora)
                    twittar(msg)
                    print(msg)
                with open('ultimo_valor.db', 'wb') as db:
                    pickle.dump(valor_atual, db,
                                protocol=pickle.HIGHEST_PROTOCOL)
            else:
                print('Diferença insignificante para ser postada.')

            time.sleep(450)

    print("Parando execução.")
