"""User views tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, User, Message, Likes, Follows
from bs4 import BeautifulSoup

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

# We turn off CSRF in WTFORMS because it makes the test process alot more difficult

app.config['WTF_CSRF_ENABLED'] = False


class UserViewsTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
    
        self.client = app.test_client()

        self.testuser = User.signup(
                                username="testuser",
                                email="test@test.com",
                                password="testuser",
                                image_url=None
                                )

        self.testuser_id = 911
        self.testuser.id = self.testuser_id

        self.u1 = User.signup(
                                username="testuser1",
                                email="testuser1@test.com",
                                password="testuser1",
                                image_url=None
                            )
        
        self.u1id = 837
        self.u1.id = self.u1id

        self.u2 = User.signup(
                                username="testuser2",
                                email="testuser2@test.com",
                                password="testuser2",
                                image_url=None
                            )
        
        self.u2id = 930
        self.u2.id = self.u2id

        self.u3 = User.signup(
                                username="three",
                                email="three@test.com",
                                password="testuser3",
                                image_url=None
                            )

        self.u4 = User.signup(
                                username="four",
                                email="four@test.com",
                                password="testuser4",
                                image_url=None
                            )

        db.session.commit()


    def tearDown(self):
        """Clean up any fouled transactions."""

        res = super().tearDown()
        db.session.rollback()
        return res

    def test_users_index(self):
        """This test methods test to confirm user 
        information is showing up on the /users route
        """

        with self.client as c:
            resp = c.get("/users")

            self.assertIn("@testuser", str(resp.data))
            self.assertIn("@testuser1", str(resp.data))
            self.assertIn("@testuser2", str(resp.data))


    def test_users_search(self):
        """This test method test to confim that
            when a search term that is part of a username
            is entered, all users having the same search term show up
        """

        with self.client as c:
            resp = c.get("/users?q=testuser")

            self.assertIn("@testuser", str(resp.data))
            self.assertIn("@testuser1", str(resp.data))
            self.assertIn("@testuser2", str(resp.data))

            self.assertNotIn("three", str(resp.data))
            self.assertNotIn("four", str(resp.data))

    def test_users_show(self):
        """This test method confirms that the correct user
          information corresponding to a particular user_id 
          is displayed.
        """

        with self.client as c :
            resp = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser", str(resp.data))

    def setup_likes(self):
        """This method sets up likes to be tested in 
            other test methods.
        """
        m1 = Message(text="warble 1", user_id=self.testuser_id)
        m2 = Message(text="I get my peaches out in Georgia", user_id=self.testuser_id)
        m3 = Message(id=1984, text="real recognize real", user_id=self.u1id )

        db.session.add_all([m1, m2, m3])
        db.session.commit()

        l1 =  Likes(user_id=self.testuser_id, message_id=1984)
        db.session.add(l1)
        db.session.commit()

    def test_user_shows_with_likes(self):
        """This test method tests to see user likes"""
        self.setup_likes()

        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser", str(resp.data))
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class" : "stat"})
            self.assertEqual(len(found), 4)

            # test for a count of message of 2 
            self.assertIn("2", found[0].text)

            # test for a count of following of 0 
            self.assertIn("0", found[1].text)

            # test for a count of followers of 0
            self.assertIn("0", found[2].text)

            # test for a count of likes of 1
            self.assertIn("1", found[3].text)

    def test_like_message(self):
        """This test method test the like_message 
           view functio in app.py
        """
        m = Message(id=2000, text="testing testing a wabler", user_id=self.u1id )

        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            
            resp = c.post("/messages/2000/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            likes = Likes.query.filter(Likes.message_id == 2000).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.testuser_id)


    def test_unlike_message(self):
        """This test method test the like_message view
            function to confirm it can also unlike 
            messaages.
        """
        self.setup_likes()
        m = Message.query.filter(Message.text == "real recognize real").one()
        self.assertIsNotNone(m)
        self.assertNotEqual(m.user_id, self.testuser_id)

        l = Likes.query.filter(Likes.user_id == self.testuser_id and Likes.message_id == m.id).one()

        # Now lets make sure that the testuser liked the message "real recognize real"
        self.assertIsNotNone(l)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            
            resp = c.post(f"/messages/{m.id}/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            likes = Likes.query.filter(Likes.message_id == m.id).all()
            # Nothing that this message has been unliked, we expect to get 
            # a length of 0 for likes
            self.assertEqual(len(likes), 0)
    

    def test_unauthorithed_like(self):
        """This test method test that an unauthorized user cannot like a meesage"""

        self.setup_likes()

        m = Message.query.filter(Message.text == "real recognize real").one()
        self.assertIsNotNone(m)

        like_count = Likes.query.count()

        with self.client as c:
        # To make an unauthorized like, we will not set the session_transaction
        # of current user. This way there isn't a logged in user
         
            resp = c.post(f"/messages/{m.id}/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
        # We will check that our flash message is displayed
            self.assertIn("Access unauthorized", str(resp.data))

        # We will also confirm that the number of likes did not change 
        self.assertEqual(like_count, Likes.query.count())


    def setup_followers(self):
        """This is a helper method used to set up followers
            to be used in the next few test methods.
        """

        f1 = Follows(user_being_followed_id=self.u1id, user_following_id=self.testuser_id)
        f2 = Follows(user_being_followed_id=self.u2id, user_following_id=self.testuser_id)
        f3 = Follows(user_being_followed_id=self.testuser_id, user_following_id=self.u1id)

        db.session.add_all([f1, f2, f3])
        db.session.commit()

    def test_user_show_with_follows(self):
        """This test method, test to confirm that the right number of 
            users following logged in user and the right number of users the logged in
            user is following are shown in the user.show page.
        """

        self.setup_followers()

        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser", str(resp.data))
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class" : "stat"})
            self.assertEqual(len(found), 4)

            # test for a count of message of 0 
            self.assertIn("0", found[0].text)

            # test for a count of following of 2
            self.assertIn("2", found[1].text)

            # test for a count of followers of 1
            self.assertIn("1", found[2].text)

            # test for a count of likes of 0
            self.assertIn("0", found[3].text)

    
    def test_show_following(self):
        """This test method, tests to confirm that when the following show following route is requested
            the right follower information appears.
        """

        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            
            resp = c.get(f"/users/{self.testuser_id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser1", str(resp.data))
            self.assertIn("@testuser2", str(resp.data))
            self.assertNotIn("@three", str(resp.data))
            self.assertNotIn("@four", str(resp.data))

    def test_show_followers(self):
        """This test method tests the user_following view function in the app.py
           to confirm that the acurate user accounts are following the current logge din user.
        """

        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id
            
            
            resp = c.get(f"/users/{self.testuser_id}/followers", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser1", str(resp.data))
            self.assertNotIn("@testuser2", str(resp.data))
            self.assertNotIn("@three", str(resp.data))
            self.assertNotIn("@four", str(resp.data))

    
    def test_unauthorithed_following_page_access(self):
        """This test method tests to confirm that an unauthorized user 
           cannnot access the following page.
        """

        self.setup_likes()

        with self.client as c:
         
            resp = c.get(f"/users/{self.testuser_id}/following", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
        # We will check that our flash message is displayed
            self.assertIn("Access unauthorized", str(resp.data))

        # We will also confirm that no users are shown in the following page
            self.assertNotIn("@testuser1", str(resp.data))

    
    def test_unauthorithed_followers_page_access(self):
        """This test method tests to confirm that an unauthorized user 
           cannnot access the followers page.
        """

        self.setup_likes()

        with self.client as c:
         
            resp = c.get(f"/users/{self.testuser_id}/followers", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
        # We will check that our flash message is displayed
            self.assertIn("Access unauthorized", str(resp.data))

        # We will also confirm that no users are shown in the following page
            self.assertNotIn("@testuser1", str(resp.data))
            self.assertNotIn("@testuser2", str(resp.data))

    






    






  