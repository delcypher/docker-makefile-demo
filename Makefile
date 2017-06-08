# See http://make.mad-scientist.net/papers/advanced-auto-dependency-generation/
# for hints on how to make this better
DOCKER_BUILD_FLAGS :=
DOCKER_BUILD := docker build $(DOCKER_BUILD_FLAGS)
DEPS_DIR := dep
VERBOSE := 0
NO_RUN := 0
EXTRA_DEP_GEN_DEPS := gen-docker-deps.py

ifneq ($(VERBOSE), 0)
  VERB :=
else
  VERB := @
endif

.PHONY: all debug clean-deps

ALL_TARGETS := $(basename $(wildcard *.Dockerfile))

ifeq ($(ALL_TARGETS),)
  $(error ALL_TARGETS is empty)
endif

all: $(ALL_TARGETS)

# Disable implicit rules
.SUFFIXES:

# Note we pipe the Dockerfile in to avoid
# passing a build context which could invalidate
# the cache.
% : %.Dockerfile
	$(VERB) $(DOCKER_BUILD) -t $@ - < $<

# Automatic dependency generation
# See https://www.gnu.org/software/make/manual/html_node/Automatic-Prerequisites.html
#
$(DEPS_DIR)/%.d : %.Dockerfile
	@echo "Generating deps for $*"
	$(VERB) mkdir -p "$(DEPS_DIR)"
	$(VERB) ./gen-docker-deps.py $< $* -o $@

# Add extra dependencies
DEP_FILES := $(addsuffix .d,$(addprefix $(DEPS_DIR)/,$(ALL_TARGETS)))
$(DEP_FILES) : $(EXTRA_DEP_GEN_DEPS)

# Include the dep files which will force their generation if they
# don't alreay exist
include $(DEP_FILES)

clean-deps:
	$(VERB) [ -d "$(DEPS_DIR)" ] && find $(DEPS_DIR) -iname '*.d' -delete || exit 0
	$(VERB) rmdir "$(DEPS_DIR)"

# Phony target for debugging
debug:
	@echo "DEBUG:"
	@echo "ALL_TARGETS := \"$(ALL_TARGETS)\""
	@echo "DEP_FILES := \"$(DEP_FILES)\""
	@echo "DOCKER_BUILD := \"$(DOCKER_BUILD)\""
	@echo "EXTRA_DEP_GEN_DEPS := \"$(EXTRA_DEP_GEN_DEPS)\""
	@echo "NO_RUN := $(NO_RUN)"
	@echo "VERBOSE := $(VERBOSE)"
