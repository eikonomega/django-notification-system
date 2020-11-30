from django.test import TestCase, Client
from django.urls import reverse

from website.api_v3.tests import factories
from website.notifications.models import OptOut
from website.notifications.utils.opt_out_link import get_opt_out_link


class TestOptOutView(TestCase):

    def setUp(self) -> None:
        self.user = factories.UserFactory()
        self.client = Client()

    def test_normal_operation(self):
        """an anonymous user is able to unsubscribe"""
        link = get_opt_out_link(self.user)
        opt_out = OptOut.objects.get(user=self.user)
        response = self.client.get(link)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Click submit to completely unsubscribe", response.content)

        response2 = self.client.post("/unsubscribe/", data={"opt_out_uuid": str(opt_out.id)})

        self.assertEqual(response2.status_code, 302)
        self.assertEqual(response2.url, link)
        opt_out = OptOut.objects.get(user=self.user)
        self.assertEqual(opt_out.has_opted_out, True)


    def test_anonymous_bad_opt_out(self):
        """anonymous bad opt out redirects to the home page"""
        link = '/unsubscribe/?u=thats-not-a-uuid'
        response = self.client.get(link)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("portal2.landing_page"))

    def test_logged_in_bad_opt_out(self):
        """logged in users get redirected to a good opt out link"""
        good_link = get_opt_out_link(self.user)
        bad_link = '/unsubscribe/?u=thats-not-a-uuid'
        self.client.force_login(self.user)
        response = self.client.get(bad_link)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, good_link)

    def test_no_u_no_crash(self):
        """missing query param does not cause crash"""
        bad_link = '/unsubscribe/'
        response = self.client.get(bad_link)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("portal2.landing_page"))

    def test_logged_in_no_u(self):
        """logged in users get redirected to a good opt out link"""
        good_link = get_opt_out_link(self.user)
        bad_link = '/unsubscribe/'
        self.client.force_login(self.user)
        response = self.client.get(bad_link)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, good_link)

