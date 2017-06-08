# Build system for Docker images proof of concept

This is a small proof of concept that demonstrates a `Makefile` and
accompanying scripts that allows multiple Dockerfiles that depend on each other
to express this dependency and have the makefile automatically handle this.

* For each Dockerfile `X.Dockerfile` there is a corresponding target named `X`.
* Each Dockerfile must contain a `FROM` directive. If that `FROM` directive refers
  to an image that the build system must handle then the comment line

```Dockerfile
# gen-docker-deps: from-is-local
```

must be present.

# Targets

* `make debug` - Shows various variables for debugging purposes
* `make foo` - Build "foo" image
* `make bar` - Build "bar" image
* `make clean-deps` - Remove dependency files

# Variables

* `VERBOSE` - Set to a value != 0 to see the commands being executed

Example usage:

```
$ make foo VERBOSE=1
```
