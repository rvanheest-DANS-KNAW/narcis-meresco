# Set defaultencoding to UTF-8:
export LANG=en_US.UTF-8

# To be used with testing only! Checks proper use of yield/return, according Thijs:
export WEIGHTLESS_COMPOSE_TEST="PYTHON"

Sets the integrationtest database path for the integration tests (defaults to: /tmp): 
export INTEGRATION_TEMPDIR_BASE="./integrationtest"