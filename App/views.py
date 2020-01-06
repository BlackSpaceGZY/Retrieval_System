from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.auth.models import User
from .forms import SearchForm, CommentForm, PaperForm, UserRegistrationForm, \
    UserEditForm, ProfileEditForm
from .models import Paper, Comment, Profile
from django.contrib import messages
from django.http import FileResponse
import os


# Create your views here.
"""
@login_required
def dashboard(request):
    return render(request,
                  'account/dashboard.html',
                  {'section': 'dashboard'})
"""


@login_required
def homepage(request):
    new_publish_paper = Paper.published.all()[:3]
    paper_list = Paper.published.all()[3:10]
    return render(request,
                  'index.html',
                  {'paper_list': paper_list,
                   'new_publish_paper': new_publish_paper})


@login_required
# 搜索Paper
def search_paper(request):
    # 搜索表单
    form = SearchForm()
    query, choice = None, None
    results = []
    if 'query' and 'choice' in request.GET:
        # 获得表单参数
        form = SearchForm(request.GET)
        # 判断表单是否有效
        if form.is_valid():
            # 获取对应参数
            query = form.cleaned_data['query']
            choice = form.cleaned_data['choice']
            # 判断搜索条件
            # 题目搜索（包含关系，不区分大小写）
            if choice == 'title':
                results = Paper.objects.filter(title__icontains=query)
            # 关键词搜索，查找题目和摘要（包含关系，不区分大小写）
            elif choice == 'key words':
                results = Paper.objects.filter(Q(abstract__icontains=query) |
                                               Q(title__icontains=query))
            # 作者搜索，查找对作者所发表的Paper
            elif choice == 'author':
                results = Paper.objects.filter(Q(author__username=query) |
                                               Q(author__first_name=query) |
                                               Q(author__last_name=query))
            # 时间搜索，查找到当前时间为止发表的Paper（日期必须符合格式）
            elif choice == 'time':
                results = Paper.objects.filter(publish__range=['2010-01-01', query])
            # 分类搜索，查找该分类的文章
            else:
                results = Paper.objects.filter(category__in=[query])
    # 分页
    # 获得分类对象，默认为4个对象为一页
    paginator = Paginator(results, 4)  # 4 posts in each page
    # 获得当前页数
    page = request.GET.get('page')
    try:
        # 获得当前页的对象
        paper_list = paginator.page(page)
    except PageNotAnInteger:
        # page为空则为第一页对象
        paper_list = paginator.page(1)
    except EmptyPage:
        # page超出则为最后一页的对象
        paper_list = paginator.page(paginator.num_pages)

    return render(request,
                  'search.html',
                  {'form': form,
                   'results': results,
                   'query': query,
                   'choice': choice,
                   'page': page,
                   'paper_list': paper_list})


@login_required
def paper_list(request):
    object_list = Paper.published.all()
    paginator = Paginator(object_list, 4)  # 3 posts in each page
    page = request.GET.get('page')
    try:
        paper_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer deliver the first page
        paper_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range deliver last page of results
        paper_list = paginator.page(paginator.num_pages)
    return render(request,
                  'paper/list.html',
                  {'page': page,
                   'paper_list': paper_list})


@login_required
def paper_detail(request, year, month, day, paper):
    # 检索期望的Paper（可能存在重名情况）
    paper = get_object_or_404(Paper, slug=paper,
                              status='published',
                              publish__year=year,
                              publish__month=month,
                              publish__day=day)

    # List of active comments for this paper
    comments = paper.comments.filter(active=True)
    new_comment = None

    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current paper to the comment
            new_comment.paper = paper
            # user
            new_comment.name = request.user.username
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()
    return render(request,
                  'paper/detail.html',
                  {'paper': paper,
                   'comments': comments,
                   'new_comment': new_comment,
                   'comment_form': comment_form})


@login_required
def submit_paper(request):
    paper_object = None
    if request.method == 'POST':
        paper_form = PaperForm(data=request.POST)
        if paper_form.is_valid():
            pdf_file = request.FILES.get('pdf_file', None)
            if pdf_file:
                pdf_url = os.path.join('data', str(request.user.profile.student_id),
                                            'pdf', pdf_file.name)
                destination = open(pdf_url, 'wb+')
                for chunk in pdf_file.chunks():
                    destination.write(chunk)
                destination.close()
                # 创建了Paper对象实例
                paper_object = paper_form.save(commit=False)
                paper_object.author = request.user
                paper_object.pdf_url = pdf_url
                paper_object.save()
                messages.success(request, 'Paper submitting successfully')
            else:
                messages.error(request, 'Error submitting your paper')
        else:
            messages.error(request, 'Error submitting your paper')
    else:
        paper_form = PaperForm()
    return render(request,
                  'submit.html',
                  {'paper_form': paper_form,
                   'paper_object': paper_object})


@login_required
def user_information(request):
    paper_list = Paper.published.filter(author=request.user)
    comment_list = Comment.objects.filter(name=request.user.username)
    return render(request,
                  'user/information.html',
                  {'paper_list': paper_list,
                   'comment_list': comment_list})


def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # 创建新用户对象
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            # 创建扩展模型保存
            Profile.objects.create(user=new_user)
            return render(request,
                          'user/register_done.html',
                          {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request,
                  'user/register.html',
                  {'user_form': user_form})


@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user,
                                 data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user.profile, data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated '\
                             'successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)

    return render(request,
                  'user/edit.html',
                  {'user_form': user_form,
                   'profile_form': profile_form})


# 文件下载
def download(request):
    file_url = request.GET.get('file_url')
    print('paper_url', file_url)
    file = open(file_url, 'rb')
    response = FileResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename=' + file_url[5:]
    return response
