#!/usr/bin/env python
"""
Recursively parse docker file to generate makefile
dependencies
"""
import argparse
import os
import logging
import pprint
import re
import sys

RE_FROM_LINE = re.compile(r'^\s*FROM\s+([a-zA-Z0-9_-]+)(:|@)?')
RE_FROM_IS_LOCAL_LINE = re.compile(r'^#\s*gen-docker-deps:\s*from-is-local')

def parse_docker_file(docker_file):
    from_target = None
    from_is_local = False
    if not os.path.exists(docker_file):
        logging.error('"{}" does not exist'.format(docker_file))
        return (None, False)
    logging.debug('Reading "{}"'.format(docker_file))
    with open(docker_file, 'r') as f:
        for line in f:
            m = RE_FROM_LINE.match(line)
            if m:
                from_target = m.group(1)
                logging.debug('Found FROM target "{}"'.format(from_target))
                continue
            m = RE_FROM_IS_LOCAL_LINE
            if m:
                from_is_local = True
                logging.debug('Found from-is-local line')
    return (from_target, from_is_local)


def gen_dependency_str(docker_file, target_name, dependency_file_name):
    docker_target_deps = [ docker_file ]
    files_to_process = [ docker_file ]
    files_processed = []
    while len(files_to_process) > 0:
        file_to_process = files_to_process.pop()
        files_processed.append(file_to_process)
        from_target, from_is_local = parse_docker_file(file_to_process)
        if from_target is None:
            logging.error('Failed to get FROM target from "{}"'.format(
                file_to_process))
            return None
        if from_is_local:
            # The FROM directive references another local Dockerfile
            # to parse
            new_file_to_process = "{}.Dockerfile".format(from_target)
            files_to_process.append(new_file_to_process)
            docker_target_deps.append(from_target)

    output_str=""
    if len(docker_target_deps) > 0:
        output_str += "{target_name} : {dependencies}\n".format(
            target_name=target_name,
            dependencies= " ".join(docker_target_deps)
        )
    # Dependencies of the output file
    if len(files_processed) > 0:
        logging.debug('Files processed: {}'.format(
            pprint.pformat(files_processed))
        )
        output_str += "{target_name} : {dependencies}\n".format(
            target_name=dependency_file_name,
            dependencies=" ".join(files_processed)
        )
    return output_str


def main(args):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('docker_file')
    parser.add_argument('target_name')
    parser.add_argument('-o',
        '--output',
        type=argparse.FileType('w'),
        default=sys.stdout,
        help='Output file (default stdout)',
    )
    parser.add_argument('--add-extra-target',
        dest='add_extra_target',
        type=str,
        default=""
    )
    parser.add_argument("-l",
        "--log-level",
        type=str,
        default="info",
        dest="log_level",
        choices=['debug','info','warning','error']
    )
    args = parser.parse_args(args)
    # Setup logging
    logLevel = getattr(logging, args.log_level.upper(),None)
    logging.basicConfig(level=logLevel)

    # Generate output
    output_str = gen_dependency_str(
        args.docker_file,
        args.target_name,
        args.output.name)
    if output_str is None:
        logging.error('Failure')
        return 1

    logging.debug('Writing "{}" to "{}"'.format(
        output_str,
        args.output.name)
    )
    args.output.write(output_str)
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
