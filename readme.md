### BlockChain - SAWTOOTH ###

This project shows the example of the creation of simple transaction processor and running in the docker environment. For easy understanding I have removed the docker compose and split into multiple docker files.
These can be built separately, and docker.host.interal used as host name to communicate from the docker host machine.

In order to run the following example. You have to do the steps.

### Building Docker components ###

```
docker build -f DockerFile-RestAPI . -t rest-api
docker build -f DockerFile-SettingsTp . -t settp
docker build -f DockerfileValidator . -t validator
docker build -f DockerfileConsensus . -t consensus
```

#### Running Containers ####
```
docker run -p 4004:4004 -p 5050:5050 validator
docker run settp
docker run -p 8008:8008 rest-api
docker run  consensus
```


#### Running Transaction Processor ####
```
python3 transaction_processor.py
```

#### Running the client ####
```
python3 client.py
```

Private and public keys are already created and placed in the `utility.py`. You can generate the new keys using the function
`generate_keys()`
 
 At present transaction processor supports withdraw, deposit, zero_balance and state operations. For brevity in the example 
 I've added the following.
 
```
if __name__ == "__main__":
    cli = Client("http://localhost:8008", private_key)
    cli.deposit(500)
    print(cli.check_balance())
```
And that can be changed with any of the operations supported in the transaction processor.



 



