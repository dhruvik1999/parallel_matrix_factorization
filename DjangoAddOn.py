from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from User.models import Auth, Subreddit, Domain, Author, Post
from Utils.reddit_instance import reddit_instance
import random


@csrf_exempt
def reddit_login_view(request, *args, **kwargs):
    if request.method == 'GET':
        state = str(random.randint(0, 65000))
        scopes = ['identity', 'history', 'read', 'mysubreddits']
        reddit = reddit_instance(request)
        url = reddit.auth.url(scopes, state, 'permanent')
        response = redirect(url)
        return response


def delink_reddit(request, *args, **kwargs):
    if request.method == 'GET':
        tok_del = Auth.objects.filter(user=request.user.id).delete()
        dom_del = Domain.objects.filter(user=request.user.id).delete()
        author_del = Author.objects.filter(user=request.user.id).delete()
        post_del = Post.objects.filter(user=request.user.id).delete()
        subred_del = Subreddit.objects.filter(user=request.user.id).delete()

        return redirect('/')


def get_token_view(request, *arg, **kwargs):
    gt = Auth.objects.all()
    t_list = [{"token": x.refresh_token} for x in gt]
    data = {"response": t_list}
    return JsonResponse(data)


def home_view(request, *args, **kwargs):
    if request.method == 'GET':
        linked_reddit = False
        post_list = []
        if request.user.is_authenticated:
            # return redirect(settings.LOGIN_URL)
            if Auth.objects.filter(user=request.user.id).exists():
                linked_reddit = True

        if linked_reddit:
            reddit = reddit_instance(request)
            subreddits = Subreddit.objects.filter(user=request.user.id)
            post_list = [{"subreddit": x.name} for x in subreddits]

        data = {
            "response": post_list,
            "authenticated": request.user.is_authenticated,
            "redditlink": linked_reddit
        }
        return render(request, 'home/home.html',
                      {"response": post_list, "authenticated": request.user.is_authenticated,
                "redditlink": linked_reddit})
