import logging
import traceback
import sys
from sawtooth_sdk.processor.core import TransactionProcessor
from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InternalError, InvalidTransaction
from utility import generate_hash, generate_address
import constants

LOGGER = logging.getLogger(__name__)
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)

class AccountTransactionHandler(TransactionHandler):
    def __init__(self, namespace):
        self._namespaces = namespace
        self._family_version = ["1.0"]

    @property
    def namespaces(self):
        return self._namespaces

    @classmethod
    def ns(cls):
        return

    @property
    def family_name(self):
        return constants.FAMILY_NAME

    @property
    def family_versions(self):
        return self._family_version

    def apply(self, transaction, context):
        """
            Transaction will have the header and payload
            for this example I have used the csv so we are splitting
            the payload to get the keys
        """
        print("Hey this is test")
        header = transaction.header
        payload_list = transaction.payload.decode().split(",")
        action = payload_list[0]
        amount = payload_list[1]
        from_key = header.signer_public_key

        if action == "deposit":
            self.deposit(context, amount, from_key)
        elif action == "withdraw":
            self.withdraw(context, amount, from_key)
        elif action == "zero_balance":
            self.zero_balance(context, amount, from_key)
        else:
            LOGGER.info("Unhandled action. Action should be deposit or withdraw")

    @classmethod
    def deposit(cls, context, deposit_amount, from_key):
        account_address = generate_address(from_key)
        state_entries = context.get_state([account_address])
        total_amount = 0.0
        if state_entries == []:
            LOGGER.info('No account exist ,creating the new one  %s.',
                        from_key)
            total_amount = float(deposit_amount)
        else:
            try:
                current_amount = float(state_entries[0].data)
                total_amount = float(deposit_amount) + float(current_amount)
            except:
                raise InvalidTransaction('Failed to load state data')

        state_data = str(total_amount).encode('utf-8')
        addresses = context.set_state({account_address: state_data})
        if len(addresses) < 1:
            raise InvalidTransaction("State Error")
        else:
            print("Success")

    @classmethod
    def withdraw(cls, context, withdraw_amount, from_key):
        account_address = generate_address(from_key)
        state_entries = context.get_state([account_address])
        total_amount = 0.0
        current_amount = 0.0
        if state_entries == []:
            LOGGER.info('No account exist ,creating the new one  %s.',
                        from_key)
        else:
            try:
                current_amount = float(state_entries[0].data)
            except:
                raise InvalidTransaction('Failed to load state data')

            if current_amount < float(withdraw_amount):
                raise InvalidTransaction('Not enough money to withdraw')

            else:
                total_amount = float(current_amount) - float(withdraw_amount)

        state_data = str(total_amount).encode('utf-8')
        addresses = context.set_state({account_address: state_data})
        if len(addresses) < 1:
            raise InvalidTransaction("State Error")

    @classmethod
    def zero_balance(cls, context, amount, from_key):
        account_address = generate_address(from_key)
        state_entries = context.get_state([account_address])
        if state_entries == []:
            LOGGER.info('No account exist ,creating the new one  %s.',
                        from_key)
            return
        state_data = str(0).encode('utf-8')
        addresses = context.set_state(
            {account_address: state_data})
        if len(addresses) < 1:
            raise InvalidTransaction("State update Error")
        LOGGER.info("SET global state success")


def main():
    '''Entry-point function for the cookiejar Transaction Processor.'''
    try:
        # Setup logging for this class.
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        # Register the Transaction Handler and start it.
        processor = TransactionProcessor(url=constants.DEFAULT_URL)
        namespace = generate_hash(constants.FAMILY_NAME)[0:6]
        handler = AccountTransactionHandler(namespace)
        print(namespace)
        processor.add_handler(handler)
        processor.start()
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if  __name__ == "__main__":
    main()