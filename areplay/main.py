import sys
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
from gevent.pool import Pool

monkey.patch_socket()
monkey.patch_ssl()

__version__ = '0.6'

DEFAULT_LOG_FORMAT = "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-Agent}i\""
USER_AGENT = 'ApacheReplay/%s' % __version__

headers = {
    'User-agent': USER_AGENT,
}


class GeventTail():
    def __init__(self, *args, **kwargs):
        self.file_name = kwargs.pop('file_name')
        try:
            self.fd = os.open(self.file_name, os.O_RDONLY | os.O_NONBLOCK)
            os.lseek(self.fd, 0, os.SEEK_END)
        except:
            self.fd = None
        self.hub = gevent.get_hub()
        self.watcher = self.hub.loop.stat(self.file_name)

    def readline(self):
        while self.fd:
            lines = os.read(self.fd, 4096).splitlines()
            if lines:
                for line in lines:
                    yield line
            else:
                self.hub.wait(self.watcher)


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

    if (match and not ignore) or args.ignore_url:
        if args.ignore_url and not (match and not ignore):
            url = args.ignore_url
        if not args.dry_run:
            r = requests.get(url, auth=args.auth, verify=args.verify, headers=headers)
            print '%s %s' % (url, r.status_code)
        else:
            print '[dry run] %s' % (url)
    else:
        print '[ignored] %s' % (url)


def reader(args):
    line_parser = apache_log_parser.make_parser(args.format)

    if args.auth is not None:
        credentials = args.auth.split(':')
        args.auth = requests.auth.HTTPBasicAuth(credentials[0], credentials[1])

    pool = Pool(args.workers)

    gt = GeventTail(file_name=args.log_file)
    for line in gt.readline():
        pool.spawn(worker, args, line, line_parser)
    pool.join()


def main():

    gevent.signal(signal.SIGQUIT, gevent.kill)

    parser = argparse.ArgumentParser(
        prog='areplay',
        description='Apache Log live replay',
        formatter_class=lambda prog: argparse.HelpFormatter(prog, max_help_position=80)
    )

    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-a', '--auth', help='Basic authentication user:password', type=str)
    parser.add_argument('-w', '--workers', help='Workers pool size', type=int, default=50)
    parser.add_argument('-m', '--match', help='Only process matching requests', type=str)
    parser.add_argument('-i', '--ignore', help='Ignore matching requests', type=str)
    parser.add_argument('-d', '--dry-run', dest='dry_run', action='store_true', help='Only prints URLs')
    parser.add_argument('-f', '--format', help='Apache log format', type=str, default=DEFAULT_LOG_FORMAT)
    parser.add_argument('-sv', '--skip-verify', dest='verify', action='store_false', help='Skip SSL certificate verify')
    parser.add_argument('-iu', '--ignore-url', dest='ignore_url', help='URL to hit when URL from log is ignored', type=str)
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
