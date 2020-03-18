import redis
import json
import threading
import logging
import signal, sys
import time

# Use a global variable to keep track of whether we're running or not.
# This is required in order to handle the signals properly.

g_running = True

class RunnerException(Exception):
    pass

class Runner:
    def __init__(self, name, version, redis_instance):
        self.name = name
        self.version = version
        # Redis-py does connection pooling by default
        self.redis_instance = redis_instance

        # Register module
        self.register_module()

        self.job_key = "laps.runner.{0}:{1}.work".format(self.name, self.version)

        #logging.info("Job key is", self.job_key)

        #logging.info("Registered as", self.name, "version", self.version)

    def __enter__(self):
        return self

    # Handle module shutdown on scope exit
    def __exit__(self, _exc_type, _exc_value, _traceback):
        self.redis_instance.rpush(
            self.create_backend_redis_key("module-shutdown"),
            self.ident
        )

    # Register a module with Redis, can throw an error
    def register_module(self):
        # For checking if a module exists, it has to be serialized in the exact same
        # way as the backend does it, with the same spacing and all.
        # There's no good way to do this, so we have to use a format string like this.
        # This might break when changing stuff in the backend.
        ident = "{{\"name\": \"{0}\", \"version\": \"{1}\"}}".format(self.name, self.version)
        self.ident = ident

        # Prod the registered_modules set to determine if we are already registered
        key = self.create_backend_redis_key("registered_modules")
        if self.redis_instance.sismember(key, ident):
            # We already exist, throw an error
            raise RunnerException("Already have registered a module {0} v{1}".format(self.name, self.version))

        self.redis_instance.rpush(
            self.create_backend_redis_key("register-module"),
            ident
        )

    # Main module loop
    def run(self, handler):
        global g_running
        blocking = True
        # Setup a signal handler to kill the loop before the next iteration when SIGINT is sent
        def signal_handler(sig, frame):
            print("Shutdown signal received, shutting down")

            # HACK: call __exit__, but only if we are waiting for a job right now.
            if blocking:
                self.__exit__(0, 0, 0)
                sys.exit(0)
            else:
                # otherwise, set running to False and exit the loop on the next iteration
                global g_running
                g_running = False

        signal.signal(signal.SIGINT, signal_handler)

        while g_running:
            # Redispy returns the key which was popped in addition to the value
            response = self.redis_instance.blpop(self.job_key, 0)
            blocking = False

            (_, response) = response
            value = json.loads(response)
            job_id = value["job_id"]
            (should_run, response) = handler(self, value)
            if not should_run:
                g_running = False

            # Push module result to redis
            response["job_id"] = job_id
            self.redis_instance.rpush(
                self.create_backend_redis_key("path-results"),
                json.dumps(response)
            )
            blocking = True

    def create_redis_key(self, name):
        return "laps.runner.{}:{}.{}".format(self.name, self.version, name)

    def create_backend_redis_key(self, name):
        return "laps.backend.{}".format(name)

    # Return a runtime error in the module
    def send_error(self, message, metadata=None):
        error = {"message": message}
        if not metadata is None:
            error["metadata"] = metadata

        self.redis_instance.rpush(
            self.create_backend_redis_key("errors"),
            json.dumps(error)
        )
