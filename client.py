import random
import time
import requests
import yaml
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader, Batch, BatchList
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader, Transaction
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_signing import CryptoFactory
from sawtooth_signing import create_context
from utility import generate_address, generate_hash, private_key
import constants
import base64


class Client():
    def __init__(self, base_url, private_key):
        self._base_url = base_url
        private_key = Secp256k1PrivateKey.from_hex(private_key)
        self._signer = CryptoFactory(create_context('secp256k1')) \
            .new_signer(private_key)
        self._public_key = self._signer.get_public_key().as_hex()
        self._address = generate_address(self._public_key)

    def deposit(self, amount):
        return self.construct_payload_and_send("deposit", amount, 10)

    def withdraw(self, amount):
        return self.construct_payload_and_send("withdraw", amount, 10)

    def zero_balance(self, amount=0):
        return self.construct_payload_and_send("zero_balance", amount,  10)

    def check_balance(self):
        result = self.talk_to_validator("state/{}".format(self._address))
        try:
            return base64.b64decode(yaml.safe_load(result)["data"])
        except BaseException:
            return None

    def talk_to_validator(self, endpoint, payload=None, content_type=None):
        url = "{}/{}".format(self._base_url, endpoint)
        print("END POINT: {}".format(url))
        headers = {}
        if content_type is not None:
            headers['Content-Type'] = content_type
        try:
            if payload is not None:
                result = requests.post(url, headers=headers, data=payload)
            else:
                result = requests.get(url, headers=headers)

            if not result.ok:
                raise Exception("Error {}: {}".format(
                    result.status_code, result.reason))
        except requests.ConnectionError as err:
            raise Exception(
                'Failed to connect to {}: {}'.format(url, str(err)))
        except BaseException as err:
            raise Exception(err)
        return result.text

    def _wait_for_status(self, batch_id, wait, result):
        '''Wait until transaction status is not PENDING (COMMITTED or error).
           'wait' is time to wait for status, in seconds.
        '''
        if wait and wait > 0:
            waited = 0
            start_time = time.time()
            while waited < wait:
                result = self.talk_to_validator("batch_statuses?id={}&wait={}"
                                                .format(batch_id, wait))
                status = yaml.safe_load(result)['data'][0]['status']
                waited = time.time() - start_time

                if status != 'PENDING':
                    return result
            return "Transaction timed out after waiting {} seconds." \
                .format(wait)
        else:
            return result

    def construct_payload_and_send(self, action, amount, wait_time=None):
        raw_payload = ",".join([action, str(amount)])
        input_and_output_address_list = [self._address]
        print(self._address)
        header = TransactionHeader(
            signer_public_key=self._public_key,
            family_name=constants.FAMILY_NAME,
            family_version="1.0",
            inputs=input_and_output_address_list,
            outputs=input_and_output_address_list,
            dependencies=[],
            payload_sha512=generate_hash(raw_payload),
            batcher_public_key=self._public_key,
            nonce=random.random().hex().encode()
        ).SerializeToString()

        transaction = Transaction(
            header=header,
            payload=raw_payload.encode(),
            header_signature=self._signer.sign(header)
        )

        transaction_list = [transaction]
        header = BatchHeader(
            signer_public_key=self._public_key,
            transaction_ids=[txn.header_signature for txn in transaction_list]
        ).SerializeToString()

        batch = Batch(
            header=header,
            transactions=transaction_list,
            header_signature=self._signer.sign(header))

        batch_list = BatchList(batches=[batch])
        batch_id = batch_list.batches[0].header_signature
        print(batch_id)
        result = self.talk_to_validator("batches",
                                        batch_list.SerializeToString(),
                                        'application/octet-stream')
        # Wait until transaction status is COMMITTED, error, or timed out

        return self._wait_for_status(batch_id, wait_time, result)


if __name__ == "__main__":
    cli = Client("http://localhost:8008", private_key)
    cli.deposit(500)
    print(cli.check_balance())

