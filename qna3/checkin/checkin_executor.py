import os
import check_in
import logging

logging.basicConfig(level=logging.DEBUG)


private_keys_file = '../private_keys.txt'
if not os.path.exists(private_keys_file):
    logging.error(f"file '{private_keys_file}' not found.")
    exit(1)

with open(private_keys_file, 'r') as file:
    private_keys = file.readlines()

private_keys = [key.strip() for key in private_keys if key.strip()]
if len(private_keys) == 0:
    raise Exception("no private keys")


for private_key in private_keys:
    logging.info(f"executing sign in private key: '{private_key}'")
    (address, tx_hash_id, new_private_key) = check_in.do_check_in(private_key)
    logging.info("==================================== SIGN IN SUCCESS ===============================================")
    logging.info("                                                                                                    ")
    logging.info("                                                                                                    ")
    logging.info("                                                                                                    ")
    logging.info(f'SIGN IN SUCCESSFUL, ADDRESS: {address}, PRIVATE_KEY: {private_key}, TX_HASH_ID: {tx_hash_id}')
    logging.info("                                                                                                    ")
    logging.info("                                                                                                    ")
    logging.info("                                                                                                    ")
    logging.info("==================================== SIGN IN SUCCESS ===============================================")


logging.info(" ALL SIGN IN SUCCESSFUL !")