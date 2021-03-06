import mongoengine as me
import datetime

class BlacklistToken(me.Document):

    token = me.StringField(max_length=500, required=True)
    date_blacklisted = me.DateTimeField(required=True, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    # Checks whether a provided auth token has been blacklisted.
    @staticmethod
    def check_blacklist(auth_token):
        match_token = BlacklistToken.objects(token=auth_token).first()
        if match_token:
            return True
        else:
            return False