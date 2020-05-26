import mongoengine as me
import datetime

class BlacklistToken(me.Document):

    token = me.StringField(max_length=500, required=True)
    date_blacklisted = me.DateTimeField(required=True, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        match_token = BlacklistToken.objects(token=auth_token).first()
        print(auth_token)
        if match_token:
            return True
        else:
            return False