from django.core.exceptions import ValidationError
from django.test import TestCase

from django_x509.tests import TestX509Mixin
from openwisp2.tests import TestOrganizationMixin

from .models import Ca, Cert


class TestPkiMixin(TestX509Mixin):
    def _create_ca(self, **kwargs):
        if 'organization' not in kwargs:
            kwargs['organization'] = None
        return super(TestPkiMixin, self)._create_ca(**kwargs)

    def _create_cert(self, **kwargs):
        if 'organization' not in kwargs:
            kwargs['organization'] = None
        return super(TestPkiMixin, self)._create_cert(**kwargs)


class TestPki(TestCase, TestPkiMixin, TestOrganizationMixin):
    ca_model = Ca
    cert_model = Cert

    def test_ca_creation_with_org(self):
        org = self._create_org()
        ca = self._create_ca(organization=org)
        self.assertEqual(ca.organization_id, org.pk)

    def test_ca_creation_without_org(self):
        ca = self._create_ca()
        self.assertIsNone(ca.organization)

    def test_cert_and_ca_different_organization(self):
        org1 = self._create_org()
        ca = self._create_ca(organization=org1)
        org2 = self._create_org(name='test org2', slug='test-org2')
        try:
            self._create_cert(ca=ca, organization=org2)
        except ValidationError as e:
            self.assertIn('organization', e.message_dict)
            self.assertIn('related CA match', e.message_dict['organization'][0])
        else:
            self.fail('ValidationError not raised')

    def test_cert_creation(self):
        org = self._create_org()
        ca = self._create_ca(organization=org)
        cert = self._create_cert(ca=ca, organization=org)
        self.assertEqual(ca.organization.pk, cert.organization.pk)
