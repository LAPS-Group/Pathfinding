import redis
import json
import threading
import logging

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
            json.dumps(self.ident)
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
        running = True
        while running:
            # Redispy returns the key which was popped in addition to the value
            (_, response) = self.redis_instance.blpop(self.job_key)
            value = json.loads(response)
            job_id = value["job_id"]
            (running, response) = handler(self, value)

            # Push module result to redis
            response["job_id"] = job_id
            self.redis_instance.rpush(
                self.create_backend_redis_key("path-results"),
                json.dumps(response)
            )

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
