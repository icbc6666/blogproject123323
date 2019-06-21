import markdown
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404

# Create your views here.
from comments.forms import CommentForm
from .models import Post, Category, Tag
from django.views.generic import ListView,DetailView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.text import slugify
from markdown.extensions.toc import TocExtension


# 博客首页
class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = "post_list"
    paginate_by = 3

    def get_context_data(self, **kwargs):
        # 获得父类生成的的传递给模板的字典
        context = super().get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')
        # 调用自己写的paginator_data 方法获得显示分页导航需要的数据
        pagination_data = self.pagination_data(paginator, page, is_paginated)
        # 将分页导航条的模板变量到context中,注意pagination_data方法返回一个字典
        context.update(pagination_data)
        # 此时context字典中已有了显示分页导航所需的数据
        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
            # 如果没有分页,作为无需显示分页导航页,不用任何分页导航页的数据,因此返回一个空字典
            return {}
        # 当前页左边的页码号,初始值为空
        left = []
        # 当前页右边的页码号,初始值为空
        right = []
        # 标签第一页页码后是否需要显示省略号
        left_has_more = False
        # 表示最后一页页码前是否需要显示省略号
        right_has_more = False
        first = False
        # 表示是否需要显示最后一页的页码号
        last = False
        # 获取用户的当前的请求的页码号
        page_number = page.number
        #  获得分页的总页号
        total_pages = paginator.num_pages
        # 获得整个分页页码列表
        page_range = paginator.page_range

        if page_number == 1:
            # 如果用户请求的是第一页的数据,那么当前页左边的的不需要数据,因此left-[]
            right = page_range[page_number:page_number+2]
            # 如果最右边的页码比 最后一页的页码的页码号减去1还小
            if right[-1] < total_pages-1:
                right_has_more = True

            if right[-1] < total_pages:
                last = True
        elif page_number == total_pages:
            # 只获得当前页码的前面的页码
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0: page_number - 1]
        # 如果左边的页码比第二页的页码还大
        #  说明左边的页码和第一页的页码之间还有其它页  需要用省略号,通过left_has_more 来表示
            if left[0] > 2:
                left_has_more = True

            if left[0] > 1:
                first = True
        else:
            # 用户获取的既不是第一页 也不是最后一页,则需要获取当前页的左右两边的连续页码
            # 这里只获取了当前页码的前后连续2个页码,你可以通过改变数字来获取更多的页码
            left = page_range[(page_number - 3) if (page_number - 3) > 0 else 0: page_number - 1]
            right = page_range[page_number:page_number + 2]
            # 是否需要显示最后一页和最后一页前的页码
            if right[-1] < total_pages - 1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

            # 是否需要显示第一页和第一页后面的页码
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True

        data = {
            'left': left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
        }
        return data


# 博客详情页
def detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    post.increase_views()
    post.body = markdown.markdown(post.body,
                                  extensions = [
                                      'markdown.extensions.extra',
                                      'markdown.extensions.codehilite',
                                      'markdown.extensions.toc',

                                  ])
    # 导入commentform
    form = CommentForm()
    # 获取这篇文章下的全部评论
    comment_list = post.comment_set.all()
    # 将文章的,表单以及文章下的评论作为模板变量传给detail.html模板,以便渲染相应的数据
    context = {"post": post,
               "form": form,
               "comment_list": comment_list
    }
    return render(request, 'blog/detail.html', context=context)


# 博客的归档
class ArchivesView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = "post_list"

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchivesView, self).get_queryset().filter(created_time__year=year,
                                                              created_time__month=month)


# 分类页面
class CategoryView(IndexView):
    # model = Post
    # template_name = 'blog/index.html'
    # context_object_name = 'post_list'

    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get("pk"))
        return super(CategoryView, self).get_queryset().filter(category=cate)


class TagView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=tag)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        # get方法返回的就是一个HTTPresponse实例
        response = super(PostDetailView, self).get(request, *args, **kwargs)
        # 将阅读量+1
        self.object.increase_views()
        # 视图必须返回一个HTTPresponsed对象
        return response

    def get_object(self, queryset=None):
        # 复写 get_objectf方法需要对post和body渲染
        post = super(PostDetailView,self).get_object(queryset=None)
        md = markdown.Markdown(extensions=[
                                          'markdown.extensions.extra',
                                          'markdown.extensions.codehilite',
                                          'markdown.extensions.toc',
                                          TocExtension(slugify=slugify)
                                      ])
        post.body = md.convert(post.body)
        post.toc = md.toc
        return post

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        form = CommentForm()
        comment_list = self.object.comment_set.all()
        context.update({
            'form':form,
            'comment_list':comment_list,
        })
        return context


def full_width(request):
    return render(request, 'blog/full-width.html')


def about(request):
    return render(request, 'blog/about.html')


def contact(request):
    return render(request, 'blog/contact.html')