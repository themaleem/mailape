from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView, DeleteView, ListView
from mailinglist.forms import MailingListForm,SubscriberForm,MessageForm
from mailinglist.models import Subscriber, MailingList, Message
from django.urls import reverse_lazy,reverse
from mailinglist.mixins import UserCanUseMailingList
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied

# Create your views here.
class MailingListListView(LoginRequiredMixin, ListView):
    
    def get_queryset(self):
        return MailingList.objects.filter(owner=self.request.user)

class CreateMailingListView(LoginRequiredMixin, CreateView):
    form_class = MailingListForm
    template_name = 'mailinglist/mailinglist_form.html'

    def get_initial(self):
        return {
            'owner': self.request.user.id,
        }
    def get_success_url(self):
        return reverse('mailinglist:mailinglist_list')    

class DeleteMailingListView(LoginRequiredMixin, UserCanUseMailingList, DeleteView):
    model = MailingList
    success_url = reverse_lazy('mailinglist:mailinglist_list')

class MailingListDetailView(LoginRequiredMixin, UserCanUseMailingList, DetailView):
    model = MailingList

class SubscribeToMailingListView(CreateView):
    
    model = MailingList
    form_class = SubscriberForm
    template_name = 'mailinglist/subscriber_form.html'

    def get_initial(self):
        return {
            'mailing_list': self.kwargs['mailinglist_pk']
        }

    def get_success_url(self):
        return reverse('mailinglist:subscriber_thankyou', kwargs={
            'pk': self.object.mailinglist.id
        })

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        mailing_list_pk = self.kwargs['mailinglist_pk']
        ctx['mailing_list'] = get_object_or_404(
            MailingList,
            pk=mailing_list_pk)
        return ctx

class ThankYouForSubscribingView(DetailView):
    model = MailingList
    tenplate_name='mailinglist/subscription_thankyou.html'

class ConfirmSubscriptionView(DetailView):
    model = Subscriber
    template_name = 'mailinglist/confirm_subscription.html'

    def get_object(self, queryset=None):
        subscriber = super().get_object(queryset=queryset)
        subscriber.confirmed = True
        subscriber.save()
        return subscriber

class UnsubscribeView(DeleteView):
    model = Subscriber
    template_name = 'mailinglist/unsubscribe.html'

    def get_success_url(self):
        mailing_list = self.object.mailinglist
        return reverse('mailinglist:mailinglist_subscribe', kwargs={
            'mailinglist_pk': mailing_list.id
        })

class CreateMessageView(LoginRequiredMixin, CreateView):
    SAVE_ACTION = 'save'
    PREVIEW_ACTON = 'preview'
    form_class = MessageForm
    template_name = 'mailinglist/message_form.html'
    
    def get_success_url(self):
        return reverse('mailinglist:manage_mailinglist', kwargs={'pk': self.object.mailing_list.id
        })
    def get_initial(self):
        mailing_list = self.get_mailing_list()
        return {
            'mailing_list':mailing_list.id
        }
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        mailing_list = self.get_mailing_list()
        ctx.update({
            'mailing_list': mailing_list,
            'SAVE_ACTION': self.SAVE_ACTION,
            'PREVIEW_ACTON':self.PREVIEW_ACTON,
        })
        return ctx
    def form_valid(self, form):
        action = self.request.POST.get('action')
        if action == self.PREVIEW_ACTON:
            context=self.get_context_data(
                form=form,
                message=form.instance,
            )
            return self.render_to_response(context=context)
        elif action == self.SAVE_ACTION:
            return super().form_valid(form)
    def get_mailing_list(self):
        mailing_list = get_object_or_404(MailingList, id=self.kwargs['mailinglist_pk'])
        if not mailing_list.user_can_use_mailing_list(self.request.user):
            raise PermissionDenied()
        return mailing_list


class MessageDetailView(LoginRequiredMixin, UserCanUseMailingList, DetailView):
    model = Message