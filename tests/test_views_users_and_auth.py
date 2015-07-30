'''
    Testing user creation/deletion/modification.
'''

# pylint: disable=too-many-public-methods

import sys
import os

sys.path.append(os.path.dirname(__file__) + '/..')

import streetsign_server
import streetsign_server.models as models
from streetsign_server.views.users_and_auth import *

from unittest_helpers import StreetSignTestCase

USERNAME = 'test'
USERPASS = '123'

ADMINNAME = 'admin'
ADMINPASS = '42'

class BasicUsersTestCase(StreetSignTestCase):
    def setUp(self):
        super(BasicUsersTestCase, self).setUp()
        self.user = models.User(loginname=USERNAME,
                                emailaddress='test@test.com',
                                is_admin=False)
        self.user.set_password(USERPASS)
        self.user.save()


        self.admin = models.User(loginname=ADMINNAME,
                                 emailaddress='testadmin@test.com',
                                 is_admin=True)
        self.admin.set_password(ADMINPASS)
        self.admin.save()

class ChangingPasswords(BasicUsersTestCase):
    ''' Testing Passwords can be changed sensibly. '''

    def test_logged_out_cannot_see_users(self):
        with self.ctx():
            self.validate(url_for('users_and_groups'), code=403)

    def test_logged_out_cannot_see_user(self):
        with self.ctx():
            self.validate(url_for('user_edit', userid=self.user.id), code=403)
            self.validate(url_for('user_edit', userid=self.admin.id), code=403)

    def test_logged_out_cannot_set_password(self):
        with self.ctx():
            resp =self.client.post(url_for('user_edit', userid=self.user.id),
                                   data={"action":"update",
                                         "newpass": "200",
                                         "conf_newpass": "200"},
                                   follow_redirects=True)

        self.assertIn("Permission Denied", resp.data)

        # and make sure the password didn't get changed!

        usernow = User.get(id=self.user.id)
        self.assertEqual(usernow.passwordhash, self.user.passwordhash)

    def test_cannot_change_password_without_current_password(self):
        self.login(USERNAME, USERPASS)

        with self.ctx():
            resp =self.client.post(url_for('user_edit', userid=self.user.id),
                                   data={"action":"update",
                                         "newpass": "200",
                                         "conf_newpass": "200"},
                                   follow_redirects=True)

        self.assertNotIn("Password changed", resp.data)
        self.assertIn("You need to enter your current password", resp.data)

        usernow = User.get(id=self.user.id)
        self.assertEqual(usernow.passwordhash, self.user.passwordhash)


    def test_cannot_change_password_with_wrong_current_password(self):
        self.login(USERNAME, USERPASS)

        with self.ctx():
            resp =self.client.post(url_for('user_edit', userid=self.user.id),
                                   data={"action":"update",
                                         "newpass": "200",
                                         "conf_newpass": "200",
                                         "currpass": "bananas"},
                                   follow_redirects=True)

        self.assertNotIn("Password changed", resp.data)
        self.assertIn("You need to enter your current password", resp.data)

        usernow = User.get(id=self.user.id)
        self.assertEqual(usernow.passwordhash, self.user.passwordhash)


    def test_can_change_own_password(self):
        self.login(USERNAME, USERPASS)

        with self.ctx():
            resp =self.client.post(url_for('user_edit', userid=self.user.id),
                                   data={"action":"update",
                                         "newpass": "200",
                                         "currpass": USERPASS,
                                         "conf_newpass": "200"},
                                   follow_redirects=True)

        self.assertIn("Password changed", resp.data)

        usernow = User.get(id=self.user.id)
        self.assertNotEqual(usernow.passwordhash, self.user.passwordhash)

    def test_cannot_change_other_users_password(self):

        user2 = models.User(loginname="user2",
                            emailaddress='test@test.com',
                            is_admin=False)
        user2.set_password("userpass2")
        user2.save()

        self.login(USERNAME, USERPASS)

        with self.ctx():
            resp =self.client.post(url_for('user_edit', userid=user2.id),
                                   data={"action":"update",
                                         "newpass": "200",
                                         "conf_newpass": "200",
                                         "currpass": USERPASS},
                                   follow_redirects=True)

        self.assertIn("Permission Denied", resp.data)
        self.assertEquals(resp.status_code, 403)

        usernow = User.get(id=user2.id)
        self.assertEqual(usernow.passwordhash, user2.passwordhash)

    def test_admin_can_change_users_password(self):
        self.login(ADMINNAME, ADMINPASS)

        with self.ctx():
            resp =self.client.post(url_for('user_edit', userid=self.user.id),
                                   data={"action":"update",
                                         "newpass": "200",
                                         "currpass": ADMINPASS,
                                         "conf_newpass": "200"},
                                   follow_redirects=True)

        self.assertIn("Password changed", resp.data)

        usernow = User.get(id=self.user.id)
        self.assertNotEqual(usernow.passwordhash, self.user.passwordhash)

    def test_admin_can_change_own_password(self):
        self.login(ADMINNAME, ADMINPASS)

        with self.ctx():
            resp =self.client.post(url_for('user_edit', userid=self.admin.id),
                                   data={"action":"update",
                                         "newpass": "200",
                                         "currpass": ADMINPASS,
                                         "conf_newpass": "200"},
                                   follow_redirects=True)

        self.assertIn("Password changed", resp.data)

        usernow = User.get(id=self.admin.id)
        self.assertNotEqual(usernow.passwordhash, self.admin.passwordhash)

class CreatingUsers(BasicUsersTestCase):
    ''' Admin only can create new users. '''

    def logged_out_cannot_create_user(self):
        pass

    def normal_user_cannot_create_user(self):
        pass

    def admin_can_create_user(self):
        self.login(ADMINNAME, ADMINPASS)
        pass

    def cannot_have_empty_password(self):
        self.login(ADMINNAME, ADMINPASS)
        pass

    def cannot_have_matching_usernames(self):
        self.login(ADMINNAME, ADMINPASS)
        pass

class DeletingUsers(BasicUsersTestCase):
    ''' Only admin can delete users, and not themselves. '''

    def logged_out_cannot_delete_user(self):
        pass

    def normal_user_cannot_delete_user(self):
        pass

    def admin_can_delete_user(self):
        self.login(ADMINNAME, ADMINPASS)
        pass

    def admin_cannot_delete_self(self):
        self.login(ADMINNAME, ADMINPASS)
        pass

    def when_user_deleted_posts_also_deleted(self):
        self.login(ADMINNAME, ADMINPASS)
        pass
