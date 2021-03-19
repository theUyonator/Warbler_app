"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        user1 = User.signup("user1", "user1@test.com", "passWord4u1", None)
        u1d1 = 1111
        user1.id = u1d1

        user2 = User.signup("user2", "user2@test.com", "passWord4u2", None)
        u2d2 = 2222
        user2.id = u2d2

        db.session.commit()

        user1 = User.query.get(u1d1)
        user2 = User.query.get(u2d2)

        self.user1 = user1
        self.u1d1 = u1d1
        self.user2 = user2
        self.u2d2 = u2d2

        self.client = app.test_client()


    def tearDown(self):
        """Clean up any fouled transactions."""

        res = super().tearDown()
        db.session.rollback()
        return res


    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr_method(self):
        """This test will make sure that the repr method works"""

        repr_u1 = self.user1.__repr__()

        self.assertEqual(repr_u1, '<User #1111: user1, user1@test.com>')

    ######################
    #
    # Following tests
    #
    #########

    def test_user_follows(self):
        """This test method checks to see if user1 is following user 2"""

        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertEqual(len(self.user1.following), 1)
        self.assertEqual(len(self.user1.followers), 0)
        self.assertEqual(len(self.user2.following), 0)
        self.assertEqual(len(self.user2.followers), 1)

        self.assertEqual(self.user1.following[0].id, self.user2.id)
        self.assertEqual(self.user2.followers[0].id, self.user1.id)

    def test_user_following(self):
        """This test method checks that the is_following method works"""

        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))

    #######################
    #
    # Signup Tests
    #
    ######################

    def test_user_valid_signup(self):
        """This test method tests to see if a valid signup method works"""

        test_user = User.signup("testUser", "testUser@unittest.com", "testpassword", None)
        test_id = 3333
        test_user.id = test_id

        db.session.commit()

        test_user = User.query.get(test_id)
        self.assertIsNotNone(test_user)
        self.assertEqual(test_user.id, test_id)
        self.assertEqual(test_user.username, "testUser")
        self.assertEqual(test_user.email, "testUser@unittest.com")
        self.assertNotEqual(test_user.password, "testpassword")

        # Since bcrypt strings should start with $2b$ we test for that as well

        self.assertTrue(test_user.password.startswith("$2b$"))


    def test_user_invalid_username(self):
        """This test method tests for an invalid user name"""

        invalid_test_user = User.signup(None, "testUser@unittest.com", "testpassword", None)
        test_id = 55555
        invalid_test_user.id = test_id

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit() 

    
    def test_user_invalid_email(self):
        """This test method tests for an invalid user name"""

        invalid_test_user = User.signup("testuser", None, "testpassword", None)
        test_id = 55555
        invalid_test_user.id = test_id

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit() 

    def test_user_invalid_password(self):
        """This test method tests for an invalid password"""

        with self.assertRaises(ValueError) as context:
            User.signup("testuser", "testUser@unittest.com", "", None)



    ###############################
    #
    #Authentication test
    #
    ##############################

    def test_user_authentication(self):
        """This tesm method tests the user authenticate method"""

        u = User.authenticate(self.user1.username, "passWord4u1")
        self.assertIsNotNone(u)
        self.assertEquals(u.id, self.u1d1)

    def test_invalid_username(self):
        """This test method test the authentication method with an invalid username"""

        self.assertFalse(User.authenticate("badusername", "passWord4u1"))

    def test_invalid_password(self):
        """This test method test the authentication method with an invalid password"""

        self.assertFalse(User.authenticate(self.user1.username, "badpassWord4u1"))

    