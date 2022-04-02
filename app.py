from asyncio.windows_events import NULL
from http import client
import json, requests, pprint
from tabnanny import check
import praw
import time
import os 
import re

"""
Goals

Basically, we aim to make a spider. 
We want to be able to target a  single subreddit. 
We want to get top posts.
We want to get all comments from that page.
We want to be able to keep track of posts as they are update? ## Is pgsql a good choice?
-> Crawl via subreddits related to user?

We want to find users
we want to be able to get all posts.
We want to be able to keep track.
"""

keys = open('secret.JSON')
auth = json.load(keys)
keys.close()

startTime = time.time()
bigTotal = time.time()

# print(auth)

reddit = praw.Reddit(
    client_id=auth['client_id'],
    client_secret=auth['client_secret'],
    user_agent=auth['user_agent']
)

Posts = []

def timeCheck(msg):
    global startTime

    print("{} : {}".format(msg,time.time()-startTime))
    startTime=time.time() #reset timer

def bigTimeCheck(msg):
    global bigTotal

    print("{} : {}".format(msg,time.time()-bigTotal))
    bigTotal=time.time() #reset big timer

def subreddit(sub,posts):
    for submission in reddit.subreddit(sub).hot(limit=posts):
        # print(submission.title)
        CollectSubmission(submission)
        # pprint.pprint((submission)['link_title'])


def userComments(user):
    #look intogenerator
    comments = reddit.redditor(user).comments.top('all',limit=None);

    cnt = 0;
    for x in comments:
        cnt+=1
        #print(x.body[:144],str(cnt))
        pprint.pprint(vars(x))
        #body
        #id
        #link_author    -
        #link_id        -
        #link_perma     -
        #link_title     - 
        #link_url       -
        #num_comments   -
        #permalink
        #score
        #subreddit_id   -
        #subreddit_name_prefixed    -
        #ups
        return

def CollectSubmission(submission):
    global Posts
    Posts.append(submission)

def CommentsFromSubmission(submission):
    
    # skip stickied posts
    if submission.stickied or submission.author.name == "AutoModerator":
        return 
    
    submission.comments.replace_more(limit=0)
    comments = submission.comments
    count = 0

    print("Found a post with {} comments. Running total: {}.".format(len(comments),len(Posts)))


    Deleted = lambda x: x == "[removed]";
    Null = lambda x:  x == "[deleted]"; 
    removeNL = lambda x: re.sub('\s{2,}','',x.replace("\n"," "))
    removePunc = lambda x: re.sub("[\n\!\(\)\-\[\]\{\}\;\:\'\"\,\<\>\.\?\@\#\$\%\^\&\*\_\~\’\“\”]",'',x);
    clean = lambda x: removeNL(removePunc(x))
    

    with open("comments.csv","a", encoding="utf-8") as f:
        if (os.stat("comments.csv").st_size == 0):
            f.write("NAME,SUBREDDIT,SCORE,BODY,DEPTH,AUTHOR,ORIGINALPOST,PERMALINK,CREATED,COLLECTED,LIFE\n")
        
        for comment in comments.list():

            # skip moderators
            if (comment.distinguished == "Moderator") or (comment.author and comment.author.name == "AutoModerator"):
                pprint.pprint(vars(comment))
                continue

            # skip empty comments
            if Deleted(comment.body) or Null(comment.body):
                continue
                

            f.write("{id},{subreddit},{score},{body},{depth},{author},{originalpost},{permalink},{created},{collected},{life}\n".format(
                id=comment.id,
                subreddit=comment.subreddit_name_prefixed,
                score=comment.score,
                body=clean(comment.body),
                depth=comment.depth,
                author=comment.author,
                originalpost=submission.id,
                permalink=comment.permalink,
                created=comment.created,
                collected=time.time(),
                life=time.time()-comment.created,
            ))

    pass

Subs = [
    # "wallstreetbets","superstonk",
    "worldnews",'politics','technology','news',
    "funny",
    "askreddit","gaming","aww","music","pics","worldnews","movies","science",
    "todayilearned","videos","news","showerthoughts","jokes","food","askscience","iama","earthporn","gifs",
    "nottheonion","books","diy","explainlikeimfive","art","lifeprotips","space","sports","mildlyinteresting","documentaries"
    ]

def stepThruSubs(count):
    global Subs
    c = 0
    for sub in Subs:
        c+=1
        print("[{}/{}] Collecting {} top posts from r/{}.".format(c,len(Subs),count,sub))
        timeCheck("Data Collection for r/{}".format(sub))
        subreddit(sub,count)

timeCheck("Init")
stepThruSubs(40)
bigTimeCheck("Fetched posts from subreddits.")


print(len(Posts))

for post in Posts:
    CommentsFromSubmission(post)

commentCount = 0
for post in Posts:
    commentCount+=len(post.comments)
    print("Found a post with {} comments. Running total: {}.".format(len(post.comments),commentCount))

bigTimeCheck("Fetched comments.")

# def process_comment(comment, depth=0):
#     """Generate comment bodies and depths."""
#     yield comment.body, depth
#     for reply in comment.replies:
#         yield from process_comment(reply, depth + 1)

# def get_post_comments(post, more_limit=32):
#     """Get a list of (body, depth) pairs for the comments in the post."""
#     comments = []
#     post.comments.replace_more(limit=more_limit)
#     for top_level in post.comments:
#         comments.extend(process_comment(top_level))
#     return comments