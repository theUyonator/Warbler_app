"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 1981
        self.testuser.id = self.testuser_id

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            print(msg)
            self.assertEqual(msg.text, "Hello")
            
    def test_unauthorized_add_message(self):
        """This test method tests to confirm that an unauthoritzed 
           user is unable to add a message.
        """

        with self.client as c:
            resp = c.post("messages/new", data={"text": "I know I can't do this."}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_Invalid_User_add_message(self):
        """This test method tests to confirm that an invalid
           user is unable to add a message.
        """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 91001933902 #This user does not exist
            resp = c.post("messages/new", data={"text": "I know I can't do this."}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_message_show(self):
        """This test method tests to confirm that the logged in user views the correct message content."""

        m = Message(
            id=1234,
            text="What is up?",
            user_id=self.testuser_id
        )

        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY]=self.testuser_id

            m = Message.query.get(1234)

            resp = c.get(f"/messages/{m.id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn("What is up?", str(resp.data))

    def test_invalid_message(self):
        """This test method tests to confirm that an invalid message isn't shown in the message show page"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY]=self.testuser_id

            resp = c.get("/messages/901928902") #The message id used to make this request does not exist

            self.assertEqual(resp.status_code, 404)

    def test_message_delete(self):
        """This test method tests to confirm that a message is deleted when a delete request is sent."""

        m = Message(
            id=1234,
            text="a test message",
            user_id=self.testuser_id
        )

        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            resp = c.post(f"/messages/{m.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            m = Message.query.get(1234)
            self.assertIsNone(m)


    def test_unauthorized_message_delete(self):
        """This test method confirms that an unauthorized user 
           cannot delete a message.
        """

        # We create a separate user first
        u = User.signup(username="unauthorized_user",
                        email="unauthorized@test.com",
                        password="unauthorized",
                        image_url=None)

        u.id = 1777

        # Now we create a message made by testuser

        m = Message(
            id=1234,
            text="a test message",
            user_id=self.testuser_id
        )

        db.session.add_all([u,m])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 1777
            
            resp = c.post(f"/messages/{m.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            m = Message.query.get(1234)
            self.assertIsNone(m)

    
    def test_message_delete_no_authentication(self):
        """This test method confirms that when there isn't a looged in user
           a message cannot be deleted.
        """

        m = Message(
            id=1234,
            text="a test message",
            user_id=self.testuser_id
        )

        db.session.add(m)
        db.session.commit()

        with self.client as c:
            
            resp = c.post(f"/messages/{m.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

            m = Message.query.get(1234)
            self.assertIsNotNone(m)

