# ZenScanner

## Autonomous SAST tool runner and aggregator

## Getting Started

```
git clone https://github.com/zenika-open-source/zenscanner
cd zenscanner
```

Edit docker-compose according to your setup :

- POSTGRES_CHANGEME
- REDIS_CHANGEME

### Start the API

```
docker-compose up
```

And you should be ready to go ! Go to http://127.0.0.1:8080 or use [ZenScannerCli](https://github.com/zenika-open-source/zenscanner-cli) to test the API :)

### Create an account

By default, the registration is disabled. To enable it, add *REGISTRATION_ENABLED=1* in the API environment

### Limit email domains for registration

The registration can be limited to email domains by define the *REGISTRATION_DOMAINS* environment

Example:

> REGISTRATION_DOMAINS=example.com;example2.com