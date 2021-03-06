"""Database model for nerve
V3: six tables: User, UserChallenge and Challenge, ChallengeCategory, Category,
UserChallengeCategory

User will store id, username, password, email and phone (for verification)

UserChallenge will store id, challenge_id, user_id, is_completed, 
accepted_timestamp, completed_timestamp, lat, long, image_path, points_earned
and number of attempts.
Related to User and Challenge by .user and .challenge

Challenge will store id, title, description, difficulty, image_path 

ChallengeCategory stores id, category_id and challenge_id
Related to Challenge and Category by .challenge and .category

Category stores categories that were recieved via api at challenge creation

UserChallengeCategory stores information about the categories a user returned
upon sucessful attempt of a challenge.

Class names are singular - table names are plural
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    """Game user - basic info"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, 
                    nullable=False, 
                    autoincrement=True, 
                    primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(30))

    def __repr__(self):
        return '<User username:{username} id:{id}>'.format(username=self.username,
                                                            id=self.id)

class UserChallenge(db.Model):
    """This table maps users to challenges they've accepted.
    Related to User through .user, to Challenge through .challenge
    """

    __tablename__ = 'user_challenges'

    id = db.Column(db.Integer, 
                    nullable=False, 
                    autoincrement=True, 
                    primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))
    is_completed = db.Column(db.Boolean, nullable=False, default=False)
    is_removed = db.Column(db.Boolean, nullable=False, default=False)
    accepted_timestamp = db.Column(db.TIMESTAMP, nullable=False)
    completed_timestamp = db.Column(db.TIMESTAMP, nullable=True)
    image_path = db.Column(db.String(50))
    points_earned = db.Column(db.Integer, default=0, nullable=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)

    user = db.relationship('User', backref=db.backref('user_challenges'))
    challenge = db.relationship('Challenge', backref=db.backref('user_challenges'))

    user_challenges_index = db.Index('unique_user_challenge_constraint', user_id, challenge_id, unique=True)

    def __repr__(self):
        return '<UserChallenge challenge_id:{challenge_id} id:{id}>'.format(challenge_id=self.challenge_id, 
                                                                            id=self.id)

class Challenge(db.Model):
    """Stores information about individual user generated challenges"""

    __tablename__ = 'challenges'

    id = db.Column(db.Integer, 
                    nullable=False, 
                    autoincrement=True, 
                    primary_key=True)
    title = db.Column(db.String(35), nullable=False)
    description = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    image_path = db.Column(db.String(50))

    def __repr__(self):
        return '<Challenge title:{title} id:{id}>'.format(title=self.title, 
                                                            id=self.id)

class ChallengeCategory(db.Model):
    """Stores the image tags that map back to an individual challenge."""

    __tablename__ = 'challenge_categories'

    id = db.Column(db.Integer, 
                    nullable=False, 
                    autoincrement=True, 
                    primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'))

    challenge = db.relationship('Challenge', backref=db.backref('challenge_categories'))
    category = db.relationship('Category', backref=db.backref('challenge_categories'))

    challenge_categories_index = db.Index('quicksearchCC', challenge_id, category_id, unique=True)

    def __repr__(self):
        return '<ChallengeCategory id: {id}>'.format(id=self.id)

class Category(db.Model):
    """Stores all of the categories that map to all of the challenges"""

    __tablename__ = 'categories'

    id = db.Column(db.Integer, 
                    nullable=False, 
                    autoincrement=True, 
                    primary_key=True)
    tag = db.Column(db.String(50), unique=True, nullable=False)

    def __repr__(self):
        return '<Category: {tag} id: {id}>'.format(tag=self.tag, id=self.id)


class UserChallengeCategory(db.Model):
    """Stores all of the categories that led to a user winning a challenge"""

    __tablename__ = 'user_challenge_categories'

    id = db.Column(db.Integer, 
                    nullable=False, 
                    autoincrement=True, 
                    primary_key=True)
    user_challenge_id = db.Column(db.Integer, db.ForeignKey('user_challenges.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))

    user_challenge = db.relationship('UserChallenge', backref=db.backref('user_challenge_categories'))
    category = db.relationship('Category', backref=db.backref('user_challenge_categories'))

    user_challenge_categories_index = db.Index('quicksearchUCC', user_challenge_id, category_id, unique=True)

    def __repr__(self):
        return '<UserChallengeCategory UC: {UCID} C: {CID}>'.format(UCID=self.user_challenge_id,
                                                                    CID=self.category_id)

################################################################################

def init_app():
    """Creating Flask app in order to run SQLAlchemy"""

    from flask import Flask
    app = Flask(__name__)

    connect_to_db(app, 'postgres:///nerve') # the actual db is specified in the server
    print "Connected to DB."


def connect_to_db(app, database_URI):
    """Connect the database to Flask app."""

    app.config['SQLALCHEMY_DATABASE_URI'] = database_URI
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)

def example_data():
    """Generates example data for test purposes. Create users with
    different characteristics:

    - One with no challenges
    - One with one pending
    - One with many pending
    - One with one pending and one complete
    - One with one complete
    - One with many complete

    And their corresponding user_challenges and challenges and the categories
    for those challenges.
    """
    import datetime

    # Amazing. A dimension where all proper nouns begin with "Schmla":
    u1 = User(username='Shmlony', password='123', email='shmlony@email.com', 
                phone='111-222-3333')
    u2 = User(username='Shmlantha', password='123', email='shmlantha@email.com', 
                phone='111-222-3333')
    u3 = User(username='Schmlona', password='123', email='schmlona@email.com', 
                phone='111-222-3333')
    u4 = User(username='Schmlove', password='123', email='schmlove@email.com', 
                phone='111-222-3333')
    u5 = User(username='Schmlandula', password='123', email='schmlandula@email.com', 
                phone='111-222-3333')
    u6 = User(username='Schmlonathan', password='123', email='schmlonathan@email.com', 
                phone='111-222-3333')

    accepted = datetime.datetime(2017, 3, 30)
    # you shouldn't be able to accept two challenges at the exact same instant 
    accepted2 = datetime.datetime(2017, 4, 30) 
    completed = datetime.datetime.now() # does not take into account time travel

    # Starting with user_id 2 because user_id 1 should have no challenges
    # user 2, one pending
    uc1 = UserChallenge(user_id=2, challenge_id=1, is_completed=False, 
                                                    accepted_timestamp=accepted)
    # user 3, two pending
    uc2 = UserChallenge(user_id=3, challenge_id=1, is_completed=False, 
                                                    accepted_timestamp=accepted)
    uc3 = UserChallenge(user_id=3, challenge_id=2, is_completed=False, 
                                                    accepted_timestamp=accepted2)
    # user 4, pending and complete
    uc4 = UserChallenge(user_id=4, challenge_id=1, is_completed=False, 
                                                    accepted_timestamp=accepted )
    uc5 = UserChallenge(user_id=4, challenge_id=2, is_completed=True, 
                        accepted_timestamp=accepted2, completed_timestamp=completed, 
                        image_path='static/images/currency.png')
    # user 5, one complete
    uc6 = UserChallenge(user_id=5, challenge_id=2, is_completed=True, 
                        accepted_timestamp=accepted, completed_timestamp=completed, 
                        image_path='static/images/currency.png')
    # user 6, many complete
    uc7 = UserChallenge(user_id=6, challenge_id=1, is_completed=True, 
                        accepted_timestamp=accepted, completed_timestamp=completed, 
                        image_path='static/images/butter.png')
    uc8 = UserChallenge(user_id=6, challenge_id=2, is_completed=True, 
                        accepted_timestamp=accepted2, completed_timestamp=completed,
                        image_path='static/images/currency.png')

    # Challenges

    c1 = Challenge(title='Existential Crisis', 
            description='Build an unnecessarily complex robot to do a simple task', 
            difficulty=5, image_path='/static/images/butter.png')
    c2 = Challenge(title='Bring Down the Federation', 
            description='Take down the Galactic Federation by changing a 1 to a 0', 
            difficulty=2, image_path='/static/images/currency.png')

    # Challenge categories

    cc1 = ChallengeCategory(challenge_id=1, category_id=1)
    cc2 = ChallengeCategory(challenge_id=1, category_id=2)
    cc3 = ChallengeCategory(challenge_id=1, category_id=3)
    cc4 = ChallengeCategory(challenge_id=1, category_id=4)
    cc5 = ChallengeCategory(challenge_id=2, category_id=6)
    cc6 = ChallengeCategory(challenge_id=2, category_id=1)
    cc7 = ChallengeCategory(challenge_id=2, category_id=5)
    cc8 = ChallengeCategory(challenge_id=2, category_id=7)

    # Categories

    cg1 = Category(tag='cartoon')
    cg2 = Category(tag='art')
    cg3 = Category(tag='machine')
    cg4 = Category(tag='illustration')
    cg5 = Category(tag='font')
    cg6 = Category(tag='text')
    cg7 = Category(tag='games')


    db.session.add_all([u1, u2, u3, u4, u5, u6,
                    uc1, uc2, uc3, uc4, uc5, uc6, uc7, uc8,
                    c1, c2, cc1, cc2, cc3, cc4, cc5, cc6, cc7, cc8,
                    cg1, cg2, cg3, cg4, cg5, cg6, cg7])

    db.session.commit()


if __name__ == '__main__':

# in terminal: createdb nerve

        init_app()
        db.create_all()


