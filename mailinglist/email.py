from django.template import Context, engines
from django.conf import settings
from django.urls import reverse
from django.core.mail import send_mail

CONFIRM_SUBSCRIPTION_LINK = 'mailinglist/email/confirmation.html'
CONFIRM_SUBSCRIPTION_TXT = 'mailinglist/email/confirmation.txt'

class EmailTemplateContext(Context):
    @staticmethod
    def make_link(path):
        return settings.MAILING_LIST_LINK_DOMAIN + path
    def __init__(self, subscriber, dict_=None, **kwargs):
        if dict_ ==None:
            dict_ = {}
            email_ctx = self.common_context(subscriber)
            email_ctx.update(dict_)
            super().__init__(email_ctx, **kwargs)
        
    def common_context(self, subscriber):
        subscriber_pk_kwargs={'pk': subscriber.id}
        unsubscribe_path = reverse('mailinglist:unsubscribe', kwargs=subscriber_pk_kwargs)
        return {
            'subscriber': subscriber,
            'mailinglist': subscriber.mailing_list,
            'unsubscribe_link': self.make_link(unsubscribe_path)
        }
    def send_email_confirmtation(subscriber):
        mailinglist = subscriber.mailing_list
        confirmation_link = EmailTemplateContext.make_link(reverse('mailinglist:confirm_subscription', kwargs={'pk': subscriber.id}))
        context = EmailTemplateContext(subscriber, {'confirmation': confirmation_link})
        subject = "Confirming subscripton to {}".format(mailinglist.name)
        dt_engine=engines['django'].engine
        text_body_template = dt_engine.get_template(CONFIRM_SUBSCRIPTION_TXT)
        text_body = text_body_template.render(context=context)
        html_body_template = dt_engine.get_template(CONFIRM_SUBSCRIPTION_LINK)
        html_body = html_body_template.render(context=context)
        
        send_mail(
            subject=subject,
            message=text_body,
            from_email=settings.MAILING_LIST_FROM_EMAIL,
            recipient_list=(subscriber.email),
            html_message=html_body
        )