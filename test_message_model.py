"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

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


class   MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        user = User.signup("user", "user@test.com", "passWord4u", None)
        uid = 1111
        user.id = uid

        db.session.commit()

        user = User.query.get(uid)
    

        self.user = user
        self.uid = uid
    
        self.client = app.test_client()


    def tearDown(self):
        """Clean up any fouled transactions."""

        res = super().tearDown()
        db.session.rollback()
        return res


    def test_message_model(self):
        """Does basic model work?"""

        m = Message(
            text="a warble",
            user_id=self.uid
        )

        db.session.add(m)
        db.session.commit()

        # User should have 1 message 
        self.assertEqual(self.user.messages[0].text, "a warble")
        self.assertEqual(len(self.user.messages), 1)


    def test_message_likes(self):
        """This test method test message likes"""

        m1 = Message(
            text="first warble",
            user_id= self.uid
        )

        m2 = Message(
            text="second warble",
            user_id=self.uid
        )

        u = User.signup("newuser", "newuser@test.com", "passWord4newuser", None)
        uid1 = 2222
        u.id = uid1

        db.session.add_all([m1, m2])
        db.session.commit()

        u.likes.append(m1)

        db.session.commit()

        l = Likes.query.filter(Likes.user_id == uid1).all()

        # There should be only one liked message and it should be m1

        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].message_id, m1.id)

    