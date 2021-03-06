import time
import datetime

from django import forms
from django.forms.util import ErrorDict
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils.crypto import salted_hmac, constant_time_compare
from django.utils.encoding import force_unicode
from django.utils.hashcompat import sha_constructor
from django.utils.text import get_text_list
from django.utils.translation import ungettext, ugettext_lazy as _

from comments2.models import Comment

COMMENT_MAX_LENGTH = getattr(settings,'COMMENT_MAX_LENGTH', 3000)

class CommentForm(forms.Form):
    """
    Handles the security aspects (anti-spoofing) for comment forms.
    """
    timestamp     = forms.IntegerField(widget=forms.HiddenInput)
    title         = forms.CharField(max_length=300)
    comment       = forms.CharField(
        label      = _('Comment'),
        widget     = forms.Textarea,
        max_length = COMMENT_MAX_LENGTH,
    )

    def __init__(self, target_object, data=None, initial=None):
        self.target_object = target_object
        if initial is None:
            initial = {}
        initial['timestamp'] = int(time.time())
        super(CommentForm, self).__init__(data=data, initial=initial)

    def clean_timestamp(self):
        """Make sure the timestamp isn't too far (> 2 hours) in the past."""
        ts = self.cleaned_data["timestamp"]
        if time.time() - ts > (2 * 60 * 60):
            raise forms.ValidationError("Timestamp check failed")
        return ts

    def get_comment_object(self):
        """
        Return a new (unsaved) comment object based on the information in this
        form. Assumes that the form is already validated and will throw a
        ValueError if not.

        Does not set any of the fields that would come from a Request object
        (i.e. ``user`` or ``ip_address``).
        """
        if not self.is_valid():
            raise ValueError("get_comment_object may only be called on valid forms")

        new = Comment(**self.get_comment_create_data())
        # new = self.check_for_duplicate_comment(new)

        return new

    def get_comment_create_data(self):
        """
        Returns the dict of data to be used to create a comment. Subclasses in
        custom comment apps that override get_comment_model can override this
        method to add extra fields onto a custom comment model.
        """
        return dict(
            content_type = ContentType.objects.get_for_model(self.target_object),
            object_id    = force_unicode(self.target_object._get_pk_val()),
            title        = self.cleaned_data["title"],
            comment      = self.cleaned_data["comment"],
            submit_date  = datetime.datetime.now(),
        )

    # def check_for_duplicate_comment(self, new):
    #     """
    #     Check that a submitted comment isn't a duplicate. This might be caused
    #     by someone posting a comment twice. If it is a dup, silently return the *previous* comment.
    #     """
    #     possible_duplicates = self.get_comment_model()._default_manager.using(
    #         self.target_object._state.db
    #     ).filter(
    #         content_type = new.content_type,
    #         object_id = new.object_id,
    #         user_name = new.user_name,
    #         user_email = new.user_email,
    #         user_url = new.user_url,
    #     )
    #     for old in possible_duplicates:
    #         if old.submit_date.date() == new.submit_date.date() and old.comment == new.comment:
    #             return old
    # 
    #     return new


    def clean_comment(self):
        """
        If COMMENTS_ALLOW_PROFANITIES is False, check that the comment doesn't
        contain anything in PROFANITIES_LIST.
        """
        comment = self.cleaned_data["comment"]
        if settings.COMMENTS_ALLOW_PROFANITIES == False:
            bad_words = [w for w in settings.PROFANITIES_LIST if w in comment.lower()]
            if bad_words:
                plural = len(bad_words) > 1
                raise forms.ValidationError(ungettext(
                    "Watch your mouth! The word %s is not allowed here.",
                    "Watch your mouth! The words %s are not allowed here.", plural) % \
                    get_text_list(['"%s%s%s"' % (i[0], '-'*(len(i)-2), i[-1]) for i in bad_words], 'and'))
        return comment
