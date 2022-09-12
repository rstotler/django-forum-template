from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from forum import models as forum_models
from .forms import ThreadCreateForm, ThreadEditForm, PostCreateForm, PostEditForm
from datetime import datetime

def subforumListView(request):
    subforumTitleList = getSubforumTitleURLList()
    return render(request, 'forum/subforum_list.html', {'subforumTitleList': subforumTitleList})

def threadListView(request, subforum_url):

    # Check If Subforum Exists #
    subforumData = forum_models.Subforum.objects.filter(titleURL=subforum_url).first()
    if subforumData == None:
        return render(request, 'forum/message.html', {'displayMessage': 'Subforum not found!'})
        
    # Prevent Guests & Level 1 Users From Accessing Locked Threads Subforum #
    if subforum_url == 'locked-threads' and (not request.user.is_authenticated or request.user.profile.userLevel == 1):
        return redirect(reverse('subforum-list'))
    
    # Load Thread List #
    else:
    
        # Get Pagination #
        threadDataList = forum_models.Thread.objects.filter(subforum=subforumData).order_by('-last_post_date')
        paginator = Paginator(threadDataList, settings.SUBFORUM_THREAD_LENGTH)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        # Set Session Data #
        request.session['previousURL'] = request.get_host() + request.get_full_path()
        request.session['previousSubforumURL'] = request.get_host() + request.get_full_path()
        request.session['targetSubforumPage'] = str(page_number)
        
        return render(request, 'forum/thread_list.html', {'subforumData': subforumData, 'threadDataList': page_obj, 'title': subforumData.title})
    
def threadCreateView(request, subforum_url):
    
    # Check If Subforum Exists & Prevent Creation Of Threads In "Locked Threads" Subforum #
    subforumData = forum_models.Subforum.objects.filter(titleURL=subforum_url).first()
    if subforumData == None or subforumData.titleURL == 'locked-threads':
        return render(request, 'forum/message.html', {'displayMessage': 'Subforum not found!'})
        
    # Thread Spam Check #
    secondsPassed = getTimeDifferenceStr(request.session.get('lastPostDate'))
    if secondsPassed < settings.SPAM_TIMER:
        return render(request, 'forum/message.html', {'displayMessage': 'Please wait ' + str(settings.SPAM_TIMER) + ' seconds between posting.'})
        
    else:
    
        # Submit Form #
        if request.method == 'POST':
            
            # Create New Thread #
            if request.user.is_authenticated : authorData = request.user
            else : authorData = None
            newThread = forum_models.Thread.objects.create(subforum=subforumData,
                                                           author=authorData,
                                                           title=request.POST['title'],
                                                           date_posted=timezone.now(),
                                                           last_post_date=timezone.now())
            newThread.save()
            
            # Create New Thread #
            newPost = forum_models.Post.objects.create(subforum=subforumData,
                                                       thread=newThread,
                                                       author=authorData,
                                                       content=request.POST['content'],
                                                       date_posted=timezone.now())
            newPost.save()
            
            # Set Session Data #
            request.session['lastPostDate'] = str(datetime.today())
            
            return redirect(reverse('post-list', kwargs={'subforum_url': subforum_url, 'thread_id': newThread.id}))
           
        # Initialize Form #
        else:
            form = ThreadCreateForm()
            return render(request, 'forum/thread_create.html', {'form': form, 'subforumData': subforumData, 'title': subforumData.title + ' - New Thread'})
        
def threadEditView(request, subforum_url, thread_id):
    
    # Check If Subforum Exists #
    subforumData = forum_models.Subforum.objects.filter(titleURL=subforum_url).first()
    if subforumData == None:
        return render(request, 'forum/message.html', {'displayMessage': 'Subforum not found!'})
        
    # Check If Thread Exists #
    threadData = forum_models.Thread.objects.filter(id=thread_id, subforum=subforumData).first()
    if threadData == None:
        return render(request, 'forum/message.html', {'displayMessage': 'Thread not found!'})
    
    # Prevent Guests & Level 1 Users From Editing Threads #
    if not request.user.is_authenticated or request.user.profile.userLevel == 1:
        return redirect(reverse('post-list', kwargs={'subforum_url': subforum_url, 'thread_id': thread_id}))
        
    else:

        # Submit Form #
        if request.method == 'POST':
            
            # Update Thread & Posts Subforum #
            targetSubforumTitleURL = getSubforumTitleURLList()[int(request.POST['subforumList'])]
            newSubforumData = forum_models.Subforum.objects.filter(titleURL=targetSubforumTitleURL).first()
            if threadData.subforum != newSubforumData:
                threadData.subforum = newSubforumData
                for postData in forum_models.Post.objects.filter(subforum=subforumData, thread=threadData):
                    postData.subforum = newSubforumData
                    postData.save()
                subforumURL = newSubforumData.titleURL
                
            else:
                subforumURL = threadData.subforum.titleURL
            
            # Set Previous URL #
            request.session['previousSubforumURL'] = request.get_host() + "\\" + subforumURL
            
            # Update Thread Title #
            threadData.title = request.POST['title']
            
            # Update Locked/Unlocked Status #
            if request.POST['isLocked'] == '1':
                threadData.isLocked = False
            else:
                threadData.isLocked = True
            threadData.save()
            
            return redirect(reverse('post-list', kwargs={'subforum_url': threadData.subforum.titleURL, 'thread_id': thread_id}))
        
        # Initialize Form #
        else:
            currentSubforumIndex = 0
            form = ThreadEditForm()
            form.fields['subforumList'].choices = [['0', 'General Discussions']]
            for i, subforumData in enumerate(forum_models.Subforum.objects.all().exclude(titleURL="general-discussions").exclude(titleURL="locked-threads")):
                form.fields['subforumList'].choices.append([str(i + 1), subforumData.title])
            form.fields['subforumList'].choices.append([str(len(form.fields['subforumList'].choices)), 'Locked Threads'])
            for subforumTitleData in form.fields['subforumList'].choices:
                if subforumTitleData[1] == threadData.subforum.title:
                    currentSubforumIndex = int(subforumTitleData[0])
                    break
            form.fields['subforumList'].initial = currentSubforumIndex
            form.fields['title'].initial = threadData.title
            if threadData.isLocked == False:
                form.fields['isLocked'].initial = 1
            else:
                form.fields['isLocked'].initial = 2
            
            return render(request, 'forum/thread_edit.html', {'form': form, 'threadData': threadData, 'title': threadData.title + ' - Edit Thread'})
            
def threadDeleteView(request, subforum_url, thread_id):
    
    # Check If Subforum Exists #
    subforumData = forum_models.Subforum.objects.filter(titleURL=subforum_url).first()
    if subforumData == None:
        return render(request, 'forum/message.html', {'displayMessage': 'Subforum not found!'})
        
    # Check If Thread Exists #
    threadData = forum_models.Thread.objects.filter(id=thread_id, subforum=subforumData).first()
    if threadData == None:
        return render(request, 'forum/message.html', {'displayMessage': 'Thread not found!'})
          
    # Prevent Guests, & Level 1 & 2 Users From Deleting Threads #
    if not request.user.is_authenticated or request.user.profile.userLevel != 3:
        return redirect(reverse('thread-list', kwargs={'subforum_url': subforum_url}))
        
    # Delete Posts & Thread #
    else:
        postDataList = forum_models.Post.objects.filter(subforum=subforumData, thread=threadData)
        for postData in postDataList:
            postData.delete()
            
        oldThreadDataList = forum_models.Thread.objects.filter(subforum=subforumData).order_by('-last_post_date')
        threadIndex = list(oldThreadDataList.values_list('id', flat=True)).index(threadData.id) + 1
        threadData.delete()
        
        # Get Pagination #
        threadDataList = forum_models.Thread.objects.filter(subforum=subforumData)
        if threadIndex > len(threadDataList):
            threadIndex -= 1
        targetPage = int(threadIndex / settings.SUBFORUM_THREAD_LENGTH)
        if threadIndex % settings.SUBFORUM_THREAD_LENGTH > 0:
            targetPage += 1
        request.session['targetSubforumPage'] = str(targetPage)
        
        return redirect('/' + subforum_url + '/?page=' + str(request.session['targetSubforumPage']))
        
def postListView(request, subforum_url, thread_id):
    
    # Check If Subforum Exists #
    subforumData = forum_models.Subforum.objects.filter(titleURL=subforum_url).first()
    if subforumData == None:
        return render(request, 'forum/message.html', {'displayMessage': 'Subforum not found!'})
        
    # Check If Thread Exists #
    threadData = forum_models.Thread.objects.filter(id=thread_id, subforum=subforumData).first()
    if threadData == None:
        return render(request, 'forum/message.html', {'displayMessage': 'Thread not found!'})
        
    # Check If Level 1 User Is Trying To Access Locked Thread #
    if threadData.isLocked == True and request.user.profile.userLevel == 1:
        return redirect(reverse('thread-list', kwargs={'subforum_url': subforum_url}))
        
    # Load Post List #
    else:
        threadData.viewCount += 1
        threadData.save()
        
        # Get Pagination #
        postDataList = forum_models.Post.objects.filter(subforum=subforumData, thread=threadData)
        paginator = Paginator(postDataList, settings.THREAD_POST_LENGTH)
        page_number = request.GET.get('page')
        if request.session.get('targetPage') != None:
            page_number = request.session.get('targetPage')
            request.session['targetPage'] = None
        page_obj = paginator.get_page(page_number)
        
        # Scroll To Post Check #
        scrollToPost = None
        if request.session.get('scrollToPost') != None:
            scrollToPost = request.session.get('scrollToPost')
        request.session['scrollToPost'] = None
            
        # Set Previous URL #
        request.session['previousURL'] = request.get_host() + request.get_full_path()
        request.session['previousThreadURL'] = request.get_host() + request.get_full_path()
        
        return render(request, 'forum/post_list.html', {'threadData': threadData, 'postDataList': page_obj, 'scrollToPost': scrollToPost, 'title': threadData.title})
    
def postCreateView(request, subforum_url, thread_id):
    
    # Check If Subforum Exists #
    subforumData = forum_models.Subforum.objects.filter(titleURL=subforum_url).first()
    if subforumData == None:
        return render(request, 'forum/message.html', {'displayMessage': 'Subforum not found!'})
        
    # Check If Thread Exists #
    threadData = forum_models.Thread.objects.filter(id=thread_id, subforum=subforumData).first()
    if threadData == None:
        return render(request, 'forum/message.html', {'displayMessage': 'Thread not found!'})
    
    # Check If Thread Is Locked #
    if threadData.isLocked == True:
        return render(request, 'forum/message.html', {'displayMessage': 'Thread locked!'})
    
    # Post Spam Check #
    secondsPassed = getTimeDifferenceStr(request.session.get('lastPostDate'))
    if not request.user.is_superuser and secondsPassed < settings.SPAM_TIMER:
        return render(request, 'forum/message.html', {'displayMessage': 'Please wait ' + str(settings.SPAM_TIMER) + ' seconds between posting.'})

    else:
        
        # Submit Form #
        if request.method == 'POST':
            createNewPost(subforum_url, thread_id, request.user, request.POST['content'])
            
            # Get Pagination #
            postCount = len(forum_models.Post.objects.filter(subforum=subforumData, thread=threadData))
            targetPage = int(postCount / settings.THREAD_POST_LENGTH)
            if postCount % settings.THREAD_POST_LENGTH > 0:
                targetPage += 1
            
            # Set Session Data #
            request.session['scrollToPost'] = str((postCount % settings.THREAD_POST_LENGTH) - 1)
            request.session['targetPage'] = str(targetPage)
            request.session['lastPostDate'] = str(datetime.today())
            
            return redirect('/' + subforum_url + '/thread-' + str(thread_id) + '/?page=' + str(request.session['targetPage']))
            
        # Initialize Form #
        else:
            form = PostCreateForm()
            return render(request, 'forum/post_create.html', {'form': form, 'threadData': threadData, 'title': threadData.title + ' - Reply To Thread'})
            
def postCreateReplyView(request, subforum_url, thread_id, post_id):
    
    # Check If Subforum Exists #
    subforumData = forum_models.Subforum.objects.filter(titleURL=subforum_url).first()
    if subforumData == None:
        return render(request, 'forum/message.html', {'displayMessage': 'Subforum not found!'})
         
    # Check If Thread Exists #
    threadData = forum_models.Thread.objects.filter(id=thread_id, subforum=subforumData).first()
    if threadData == None:
        return render(request, 'forum/message.html', {'displayMessage': 'Thread not found!'})
    
    # Post Spam Check #
    secondsPassed = getTimeDifferenceStr(request.session.get('lastPostDate'))
    if not request.user.is_superuser and secondsPassed < settings.SPAM_TIMER:
        return render(request, 'forum/message.html', {'displayMessage': 'Please wait ' + str(settings.SPAM_TIMER) + ' seconds between posting.'})

    else:
    
        # Submit Form #
        if request.method == 'POST':
            createNewPost(subforum_url, thread_id, request.user, request.POST['content'].rstrip())
            
            # Get Pagination #
            postCount = len(forum_models.Post.objects.filter(subforum=subforumData, thread=threadData))
            targetPage = int(postCount / settings.THREAD_POST_LENGTH)
            if postCount % settings.THREAD_POST_LENGTH > 0:
                targetPage += 1
            
            # Set Session Data #
            request.session['scrollToPost'] = str((postCount % settings.THREAD_POST_LENGTH) - 1)
            request.session['targetPage'] = str(targetPage)
            request.session['lastPostDate'] = str(datetime.today())
            
            return redirect('/' + subforum_url + '/thread-' + str(thread_id) + '/?page=' + str(request.session['targetPage']))
            
        # Initialize Form #
        else:
            postData = forum_models.Post.objects.get(id=post_id, subforum=subforumData)
            
            postUsername = 'Anonymous'
            if postData.author != None:
                postUsername = postData.author.username
            
            postDate = postData.getDateString()
            
            # Get Quoted Post Content - Check If Post Content Already Contains A Quote #
            if '[quote=' in postData.content and '[/quote]' in postData.content:
                
                # Check If Number Of Previous Quotes Exceeds 3 #
                quotedPostContent = postData.content[0:postData.content.rindex('[/quote]')+8]
                tagCount = quotedPostContent.count('[quote=')
                if quotedPostContent.count('[/quote]') < tagCount:
                    tagCount = quotedPostContent.count('[/quote]')
                if tagCount > 2:
                    for i in range(tagCount - 2):
                        quotedPostContent = quotedPostContent[quotedPostContent.index('[/quote]')+8::].lstrip()
                
                newContent = postData.content[postData.content.rindex('[/quote]')+8::]
                if len(newContent) > 0:
                    quotedPostContent = quotedPostContent + '\r\r[quote=' + postUsername + ' date=' + postDate + ']' + newContent.lstrip() + '[/quote]'
                quotedPostContent = quotedPostContent + '\r\r'
                
            else:
                quotedPostContent = '[quote=' + postUsername + ' date=' + postDate + ']' + postData.content + '[/quote]\r\r'
            
            form = PostCreateForm(initial={'content': quotedPostContent})
            return render(request, 'forum/post_create.html', {'form': form, 'threadData': threadData, 'title': threadData.title + ' - Reply To Thread'})

def postEditView(request, subforum_url, thread_id, post_id):
    
    # Check If Subforum Exists #
    subforumData = forum_models.Subforum.objects.filter(titleURL=subforum_url).first()
    if subforumData == None:
        return render(request, 'forum/message.html', {'displayMessage': 'Subforum not found!'})
    
    # Check If Thread Exists #
    threadData = forum_models.Thread.objects.filter(id=thread_id, subforum=subforumData).first()
    if threadData == None:
        return render(request, 'forum/message.html', {'displayMessage': 'Thread not found!'})
       
    # Check If Post Exists #
    postData = forum_models.Post.objects.filter(id=post_id, subforum=subforumData).first()
    if postData == None:
        return render(request, 'forum/message.html', {'displayMessage': 'Post not found!'})
    
    # Prevent Guests & Users Who Are Not The Author From Editing Posts #
    if not request.user.is_authenticated or (request.user.profile.userLevel == 1 and postData.author == None) or ((not request.user.is_superuser and request.user.profile.userLevel == 1) and postData.author.username.lower() != request.user.username.lower()):
        return redirect(reverse('post-list', kwargs={'subforum_url': subforum_url, 'thread_id': thread_id}))
        
    else:

        # Get Pagination #
        postDataList = forum_models.Post.objects.filter(subforum=subforumData, thread=threadData)
        postIndex = list(postDataList.values_list('id', flat=True)).index(postData.id)
        targetPage = int((postIndex / settings.THREAD_POST_LENGTH) + 1)
        request.session['targetPage'] = targetPage
        
        # Set ScrollToPost #
        request.session['scrollToPost'] = str(postIndex % 5)
        
        # Submit Form #
        if request.method == 'POST':
            
            # Edit Post #
            postData.content = request.POST['content']
            postData.save()
            
            return redirect(reverse('post-list', kwargs={'subforum_url': subforum_url, 'thread_id': thread_id}))
            
        # Initialize Form #
        else:
            form = PostEditForm(initial={'content': postData.content})
            return render(request, 'forum/post_edit.html', {'form': form, 'threadData': threadData, 'title': threadData.title + ' - Edit Post'})
        
def postDeleteView(request, subforum_url, thread_id, post_id):
    
    # Check If Subforum Exists #
    subforumData = forum_models.Subforum.objects.filter(titleURL=subforum_url).first()
    if subforumData == None:
        return render(request, 'forum/message.html', {'displayMessage': 'Subforum not found!'})
        
    # Check If Thread Exists #
    threadData = forum_models.Thread.objects.filter(id=thread_id, subforum=subforumData).first()
    if threadData == None:
        return render(request, 'forum/message.html', {'displayMessage': 'Thread not found!'})
       
    # Check If Post Exists #
    postData = forum_models.Post.objects.filter(id=post_id, subforum=subforumData).first()
    if postData == None:
        return render(request, 'forum/message.html', {'displayMessage': 'Post not found!'})
   
    # Prevent Guests & Level 1 Users From Deleting Posts #
    if not request.user.is_authenticated or (not request.user.is_superuser and request.user.profile.userLevel == 1):
        return redirect(reverse('post-list', kwargs={'subforum_url': subforum_url, 'thread_id': thread_id}))
    
    # Prevent Deletion Of Last Post In Thread #
    oldPostDataList = forum_models.Post.objects.filter(subforum=subforumData, thread=threadData)
    if len(oldPostDataList) == 1:
        return redirect(reverse('post-list', kwargs={'subforum_url': subforum_url, 'thread_id': thread_id}))
    
    # Delete Post #
    else:
        postIndex = list(oldPostDataList.values_list('id', flat=True)).index(postData.id) + 1
        postData.delete()
        postDataList = forum_models.Post.objects.filter(subforum=subforumData, thread=threadData)
        
        # Get Pagination #
        if postIndex > len(postDataList):
            postIndex -= 1
        targetPage = int(postIndex / settings.THREAD_POST_LENGTH)
        scrollToPost = str((postIndex - 1) % settings.THREAD_POST_LENGTH)
        if postIndex % settings.THREAD_POST_LENGTH > 0:
            targetPage += 1
        else:
            scrollToPost = '0'
        request.session['targetPage'] = targetPage
        
        # Set ScrollToPost #
        request.session['scrollToPost'] = scrollToPost
        
        return redirect('/' + subforum_url + '/thread-' + str(thread_id) + '/?page=' + str(request.session['targetPage']))

# Utility Functions #
def getSubforumTitleURLList():

    # Create Custom Subforum List Order #
    subforumTitleList = []
    subforumDataList = forum_models.Subforum.objects.all()
    for subforumData in subforumDataList:
        if subforumData.titleURL not in ['general-discussions', 'locked-threads']:
            subforumTitleList.append(subforumData.titleURL)
    subforumTitleList.insert(0, 'general-discussions')
    subforumTitleList.append('locked-threads')
    
    return subforumTitleList

def createNewPost(subforum_url, thread_id, user, postContent):
    subforumData = forum_models.Subforum.objects.filter(titleURL=subforum_url).first()
    if subforumData != None:
        threadData = forum_models.Thread.objects.filter(id=thread_id, subforum=subforumData).first()
        if threadData != None:
            threadData.last_post_date = timezone.now()
            threadData.save()
            
            if user.is_authenticated : authorData = user
            else : authorData = None
            newPost = forum_models.Post.objects.create(subforum=subforumData,
                                                       thread=threadData,
                                                       author=authorData,
                                                       content=postContent,
                                                       date_posted=timezone.now())
            newPost.save()
            
def getTimeDifferenceStr(strLastPostDate):
    if strLastPostDate == None:
        return settings.SPAM_TIMER
        
    else:
        dateYear = strLastPostDate[0:4]
        dateMonth = strLastPostDate[5:7]
        dateDay = strLastPostDate[8:10]
        timeHour = strLastPostDate[11:13]
        timeMinute = strLastPostDate[14:16]
        timeSeconds = strLastPostDate[17:19]
        lastPostDate = datetime.fromisoformat(dateYear + "-" + dateMonth + "-" + dateDay + "T" + timeHour + ":" + timeMinute + ":" + timeSeconds)
        
        return int((datetime.today() - lastPostDate).total_seconds())
