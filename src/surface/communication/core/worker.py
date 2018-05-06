from logbook import Logger
from surface.communication.ias import Quote
from rlp import encode
from surface.communication.core import IPC

log = Logger('Node')


class Worker:
    def __init__(self, account, contract, url=''.encode(), sig_key='',
                 quote: Quote = ''):
        """
        The worker is in charge of managing the tasks and talking to core.
        :param account:
        :param contract:
        :param url:
        :param sig_key:
        :param quote:
        """
        self.account = account
        self.contract = contract
        self._url = url
        self._sig_key = sig_key
        self._quote = quote
        self.ipc = IPC()

    @property
    def quote(self):
        return self._quote

    @property
    def sig_key(self):
        return self._sig_key

    @property
    def url(self):
        return self._url

    def register(self):
        """
        Registers the worker with the Enigma contract
        :return:
        """
        log.info('registering account: {}'.format(self.account))
        # TODO: why was there an encode() call here?
        # self.url.encode(), self.sig_key, self.quote
        print(self.account)
        print(len(self.quote)+len(self.sig_key)+len(self.url))
        tx = self.contract.functions.register(
            self.url, self.sig_key, self.quote
            # TODO: Research how much gas limit to put.
        ).transact({'from': self.account, 'value': 1, 'gas': 1188498})

        return tx

    def info(self):
        """
        :return: The worker struct of that account
        """
        log.info('fetching worker info: {}'.format(self.account))
        worker = self.contract.functions.workers(self.account).call(
            {'from': self.account})

        return worker

    # TODO: move into the dapp.
    def trigger_compute_task(self, secret_contract, callable, args, callback,
                             preprocessors,
                             fee):
        log.info(
            'executing computation on contract: {}'.format(secret_contract)
        )
        msg = encode(args)
        # TODO: must call approve() first, see JS test
        tx = self.contract.functions.compute(
            secret_contract, callable, msg, callback, fee, preprocessors
        ).transact({'from': self.account})

        return tx

    def get_task(self, secret_contract, task_id):
        # TODO: When this should be used? what's the task_id
        log.info('fetching task: {} {}'.format(secret_contract, task_id))
        worker = self.contract.functions.tasks(secret_contract, task_id).call(
            {'from': self.account})

        return worker

    def commit_results(self, secret_contract, task_id, results, sig):
        """
        Commiting the task
        :param secret_contract:
        :param task_id:
        :param results:
        :param sig:
        :return:
        """
        log.info(
            'solving task: {}'.format(secret_contract, task_id)
        )
        tx = self.contract.functions.commitResults(
            secret_contract, task_id, results, sig
        ).transact({'from': self.account})

        return tx
