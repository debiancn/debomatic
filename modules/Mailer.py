# Deb-o-Matic - Mailer module
#
# Copyright (C) 2010 Alessio Treglia
#
# Authors: Alessio Treglia <quadrispro@ubuntu.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA.
#
# Send a reply to the uploader once the build has finished.

import os
from subprocess import Popen, PIPE
from smtplib import SMTP
from email.parser import Parser


class DebomaticModule_Mailer:

    DEFAULT_OPTIONS = (
        'smtphost',
        'smtpport',
        'authrequired',
        'smtpuser',
        'smtppass',
        'build_success_template',
        'build_failure_template',
        'fromaddr',
    )

    def write_reply(self, template, buildlog, args):
        with open(template, 'r') as fd:
            substdict = dict(args)
            substdict['buildlog'] = buildlog
            substdict['fromaddr'] = self.fromaddr
            reply = fd.read() % substdict
        msg = Parser().parsestr(reply)
        return msg.as_string()

    def __init__(self):
        if args[opts].has_section('mailer'):
            for opt in self.DEFAULT_OPTIONS:
                setattr(self, opt, args[opts].get('mailer', opt))

    def post_build(self, args):
        if not args['uploader']:
            return
        template = None
        uploader = args['uploader']
        resultdir = os.path.join(args['directory'], 'pool', args['package'])
        for filename in os.listdir(resultdir):
            if filename.endswith('.changes'):
                template = self.build_success_template
                break
        if not template:
            template = self.build_failure_template
        try:
            bp = '%(directory)s/pool/%(package)s/%(package)s.buildlog' % args
            buildlog_exc = Popen(['tail', '--lines=20', bp],
                                 stdout=PIPE).communicate()[0]
            msg = self.write_reply(template, buildlog_exc, args)
            self.smtp = SMTP(self.smtphost, int(self.smtpport))
            if int(self.authrequired):
                self.smtp.login(self.smtpuser, self.smtppass)
            self.smtp.sendmail(self.fromaddr, uploader, msg)
            self.smtp.quit()
        except Exception as e:
            raise e