# DSW Email Submission Service

[![GitHub release (latest SemVer)](https://img.shields.io/github/v/release/ds-wizard/email-submission-service)](https://github.com/ds-wizard/email-submission-service/releases)
[![Docker Pulls](https://img.shields.io/docker/pulls/datastewardshipwizard/email-submission-service)](https://hub.docker.com/r/datastewardshipwizard/email-submission-service)
[![GitHub](https://img.shields.io/github/license/ds-wizard/email-submission-service)](LICENSE)

DSW submission service for email notifications

## Usage

### Configuration file

- To enable security via `Authorization` bearer token, set `security.enabled` to `true` and list your tokens in `security.tokens`.
- Set your email settings under `mail` (it is the same as for DSW configuration).

See [`config.example.yml`](config.example.yml) for reference.

### Docker-Compose

Add to your DSW deployment:

```yml
  email-submission:
    image: datastewardshipwizard/email-submission-service:develop
    restart: unless-stopped
    volumes:
      - ./submission-config.yml:/app/config.yml:ro
```

### DSW Submission Service

Go to *Settings* and *Document Submission*, create a new service:

- Set any unique ID you need, e.g. `email-submission`.
- Name the submission and fill description to explain it for the users.
- Add supported template and format that can be submitted.
- Method is POST and URL is based on your deployment, if you use docker-compose as above, it will be `http://email-submission/submit`.
- Add headers:
  - `Content-Type` based on your selected format (e.g. `application/json` or `application/pdf`)
  - `Authorization` in case you enabled security in the config file (prefix the token with `Bearer <token>`)
  - `X-Msg-Recipient` specify recipient (email address) for the notification.
  - `X-Msg-Intro` any string that will be part of the notification.
  - `X-Location` URL where will be the user pointed after notification is sent.

## License

This project is licensed under the Apache License v2.0 - see the
[LICENSE](LICENSE) file for more details.
