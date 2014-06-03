# Copyright (c) 2011 X.commerce, a business unit of eBay Inc.
# Copyright 2011 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import iso8601
from lxml import etree
from oslo.config import cfg
import webob

from cinder.api.v1 import router
from cinder.api import xmlutil
from cinder.openstack.common import jsonutils
from cinder import test


NS = "{http://docs.openstack.org/common/api/v1.0}"


CONF = cfg.CONF


class ExtensionTestCase(test.TestCase):
    def setUp(self):
        super(ExtensionTestCase, self).setUp()
        ext_list = CONF.osapi_volume_extension[:]
        fox = ('cinder.tests.api.extensions.foxinsocks.Foxinsocks')
        if fox not in ext_list:
            ext_list.append(fox)
            self.flags(osapi_volume_extension=ext_list)


class ExtensionControllerTest(ExtensionTestCase):

    def setUp(self):
        super(ExtensionControllerTest, self).setUp()
        self.ext_list = ["TypesManage", "TypesExtraSpecs", ]
        self.ext_list.sort()

    def test_list_extensions_json(self):
        app = router.APIRouter()
        request = webob.Request.blank("/fake/extensions")
        response = request.get_response(app)
        self.assertEqual(200, response.status_int)

        # Make sure we have all the extensions, extra extensions being OK.
        data = jsonutils.loads(response.body)
        names = [str(x['name']) for x in data['extensions']
                 if str(x['name']) in self.ext_list]
        names.sort()
        self.assertEqual(names, self.ext_list)

        # Ensure all the timestamps are valid according to iso8601
        for ext in data['extensions']:
            iso8601.parse_date(ext['updated'])

        # Make sure that at least Fox in Sox is correct.
        (fox_ext, ) = [
            x for x in data['extensions'] if x['alias'] == 'FOXNSOX']
        self.assertEqual({'namespace': 'http://www.fox.in.socks/api/ext/pie/v1.0',
                      'name': 'Fox In Socks',
                      'updated': '2011-01-22T13:25:27-06:00',
                      'description': 'The Fox In Socks Extension.',
                      'alias': 'FOXNSOX',
                      'links': []}, fox_ext)

        for ext in data['extensions']:
            url = '/fake/extensions/%s' % ext['alias']
            request = webob.Request.blank(url)
            response = request.get_response(app)
            output = jsonutils.loads(response.body)
            self.assertEqual(output['extension']['alias'], ext['alias'])

    def test_get_extension_json(self):
        app = router.APIRouter()
        request = webob.Request.blank("/fake/extensions/FOXNSOX")
        response = request.get_response(app)
        self.assertEqual(200, response.status_int)

        data = jsonutils.loads(response.body)
        self.assertEqual(
            data['extension'],
            {"namespace": "http://www.fox.in.socks/api/ext/pie/v1.0",
             "name": "Fox In Socks",
             "updated": "2011-01-22T13:25:27-06:00",
             "description": "The Fox In Socks Extension.",
             "alias": "FOXNSOX",
             "links": []})

    def test_get_non_existing_extension_json(self):
        app = router.APIRouter()
        request = webob.Request.blank("/fake/extensions/4")
        response = request.get_response(app)
        self.assertEqual(404, response.status_int)

    def test_list_extensions_xml(self):
        app = router.APIRouter()
        request = webob.Request.blank("/fake/extensions")
        request.accept = "application/xml"
        response = request.get_response(app)
        self.assertEqual(200, response.status_int)

        root = etree.XML(response.body)
        self.assertEqual(NS, root.tag.split('extensions')[0])

        # Make sure we have all the extensions, extras extensions being OK.
        exts = root.findall('{0}extension'.format(NS))
        self.assertGreaterEqual(len(exts), len(self.ext_list))

        # Make sure that at least Fox in Sox is correct.
        (fox_ext, ) = [x for x in exts if x.get('alias') == 'FOXNSOX']
        self.assertEqual('Fox In Socks', fox_ext.get('name'))
        self.assertEqual('http://www.fox.in.socks/api/ext/pie/v1.0',
            fox_ext.get('namespace'))
        self.assertEqual('2011-01-22T13:25:27-06:00', fox_ext.get('updated'))
        self.assertEqual('The Fox In Socks Extension.',
            fox_ext.findtext('{0}description'.format(NS)))

        xmlutil.validate_schema(root, 'extensions')

    def test_get_extension_xml(self):
        app = router.APIRouter()
        request = webob.Request.blank("/fake/extensions/FOXNSOX")
        request.accept = "application/xml"
        response = request.get_response(app)
        self.assertEqual(200, response.status_int)
        xml = response.body

        root = etree.XML(xml)
        self.assertEqual(NS, root.tag.split('extension')[0])
        self.assertEqual('FOXNSOX', root.get('alias'))
        self.assertEqual('Fox In Socks', root.get('name'))
        self.assertEqual('http://www.fox.in.socks/api/ext/pie/v1.0',
            root.get('namespace'))
        self.assertEqual('2011-01-22T13:25:27-06:00', root.get('updated'))
        self.assertEqual('The Fox In Socks Extension.',
            root.findtext('{0}description'.format(NS)))

        xmlutil.validate_schema(root, 'extension')
