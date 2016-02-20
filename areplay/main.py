import os
import re
import gevent
import requests
import signal
import requests
import apache_log_parser
import argparse

from gevent.queue import Queue
from gevent import monkey

from .tail import GeventTail

monkey.patch_socket()

DEFAULT_LOG_FORMAT = "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\""


def match_keywords(keywords, request_url):
    for k in keywords:
        if k in request_url:
            return True
    return False


def worker(args, line, line_parser):
    l = line_parser(line)

    url = '%s%s' % (args.server.rstrip('/'), l['request_url'])

    match = args.match is None or match_keywords(args.match, l['request_url'])
    ignore = args.ignore is not None and match_keywords(args.ignore, l['request_url'])

    if match and not ignore:
        print url
        if not args.dry_run and match:
            r = requests.get(url, auth=args.auth)
    else:
        print '[ignored] %s' % (url)


def reader(args):
    line_parser = apache_log_parser.make_parser(args.format)

    if args.auth is not None:
        credentials = args.auth.split(':')
        args.auth = requests.auth.HTTPBasicAuth(credentials[0], credentials[1])

    gt = GeventTail(file_name=args.log_file)
    for line in gt.readline():
        gevent.spawn(worker, args, line, line_parser).join()


def main():

    gevent.signal(signal.SIGQUIT, gevent.kill)

    parser = argparse.ArgumentParser(
        prog='areplay',
        description='Apache Log live replay',
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=80)
    )

    parser.add_argument('-a', '--auth', help='Basic authentication user:password', type=str)

    parser.add_argument('-m', '--match', help='Only process matching requests', type=str)

    parser.add_argument('-i', '--ignore', help='Ignore matching requests', type=str)

    parser.add_argument('-d', '--dry-run', dest='dry_run', action='store_true', help='Only prints URLs')

    parser.add_argument('-f', '--format', help='Apache log format', type=str, default=DEFAULT_LOG_FORMAT)

    parser.add_argument('server', help='Remote Server')

    parser.add_argument('log_file', help='Apache log file path')

    args = parser.parse_args()

    if args.match is not None:
        args.match = args.match.split('|')

    if args.ignore is not None:
        args.ignore = args.ignore.split('|')

    try:
        gevent.spawn(reader, args).join()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
