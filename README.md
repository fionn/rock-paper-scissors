# rockpaperscissors

## Configuration

Set up a virtual environment with `make venv` and enter it with `source venv/bin/activate`.

Export the following environment variables for authenticating to the Twitter API:
* `API_KEY`,
* `API_SECRET`,
* `ACCESS_TOKEN`,
* `ACCESS_TOKEN_SECRET`.

(See [https://github.com/fionn/twitterauthenticator](twitterauthenticator) for how to generate access tokens.)

## Usage

Just run it directly.

## Deployment

### Heroku

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/fionn/rockpaperscissors)

Add the remote with `git remote add heroku git@heroku.com:app-name.git` and use `git push heroku` to update the deployment.

### Systemd

Add the above environment variables to `.env` in the repository root, without an `export` directive.
Make the virtual environment.
Then symlink or copy the unit files in [`system_units/`](system_units/) to `/etc/systemd/system/` and enable the timer.

### AWS Lambda

Deployment is managed by Terraform, with configuration in [`infrastructure/`](infrastructure/).
