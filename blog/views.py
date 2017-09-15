from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from blog.models import Post, Comment, Category
from django.utils import timezone
from blog.forms import PostForm, CommentForm, FacetedPostSearchForm

from django.views.generic import (TemplateView,ListView,
                                  DetailView,CreateView,
                                  UpdateView,DeleteView,
                                  FormView)

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from haystack.generic_views import FacetedSearchView as BaseFacetedSearchView
from haystack.query import SearchQuerySet

class AboutView(TemplateView):
    template_name = 'about.html'

class GrassToGraceView(TemplateView):
    template_name ='grass-to-grace.html'

# Category View
def show_category(request,hierarchy= None):
    category_slug = hierarchy.split('/')
    category_queryset = list(Category.objects.all())
    all_slugs = [ x.slug for x in category_queryset ]
    parent = None
    for slug in category_slug:
        if slug in all_slugs:
            parent = get_object_or_404(Category,slug=slug,parent=parent)
        else:
            instance = get_object_or_404(Post, slug=slug)
            breadcrumbs_link = instance.get_cat_list()
            category_name = [' '.join(i.split('/')[-1].split('-')) for i in breadcrumbs_link]
            breadcrumbs = zip(breadcrumbs_link, category_name)
            return render(request, "post_detail.html", {'instance':instance,'breadcrumbs':breadcrumbs})

    return render(request,"category.html",{'post_set':parent.post_set.all(),'sub_categories':parent.children.all()})


class PostListView(ListView):
    model = Post
    paginate_by = 5


    def get_context_data(self, **kwargs):
        context = super(PostListView, self).get_context_data(**kwargs)
        context['post_list'] = Post.objects.all()
        context['featured_posts'] = Post.objects.filter(featured_post=True).order_by('-created_date')
        context['trending_posts'] = Post.objects.filter(trending_post=True)
        context['latest_posts'] =  Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
        listed_post = Post.objects.all()
        paginator = Paginator(listed_post, self.paginate_by)

        page = self.request.GET.get('page')

        try:
            list_posts = paginator.page(page)
        except PageNotAnInteger:
            list_posts = paginator.page(1)
        except EmptyPage:
            list_posts = paginator.page(paginator.num_pages)

        context['listed_posts'] = list_posts
        return context

    def get_queryset(self):
        return Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')

class PostDetailView(DetailView):
    model = Post

    def get_context_data(self, **kwargs):
        context = super(PostDetailView, self).get_context_data(**kwargs)
        context['Comments'] = Comment.objects.all()
        context['post_list'] = Post.objects.all()
        context['featured_posts'] = Post.objects.filter(featured_post=True)
        context['recent_posts'] = Post.objects.filter(published_date__lte=timezone.now()).order_by('-published_date')
        context['form'] = CommentForm
        context['approved_comments'] = Comment.objects.filter(approved_comment=True)
        
        return context


class CreatePostView(LoginRequiredMixin, CreateView):
    login_url = 'account/login/'
    redirect_field_name = 'blog/post_detail.html'
    form_class = PostForm
    model = Post

    def form_valid(self, form):
        self.object=form.save(commit=False)
        self.object.author=self.request.user
        self.object.save()
        return super(CreatePostView, self).form_valid(form)

        
class PostUpdateView(LoginRequiredMixin,UpdateView):
    login_url = 'account/login/'
    redirect_field_name = 'blog/post_detail.html'

    form_class = PostForm

    model = Post


class DraftListView(LoginRequiredMixin,ListView):
    login_url = 'account/login/'
    redirect_field_name = 'blog/post_list.html'

    model = Post

    def get_queryset(self):
        return Post.objects.filter(published_date__isnull=True).order_by('-created_date')


class PostDeleteView(LoginRequiredMixin,DeleteView):
    model = Post
    success_url = reverse_lazy('post_list')


def autocomplete(request):
  sqs = SearchQuerySet().autocomplete(
  content_auto=request.GET.get(
  'query',
  ''))[
  :5]
  s = []
  for result in sqs:
    d = {"value": result.title, "data": result.object.slug}
    s.append(d)
    output = {'suggestions': s}
  return JsonResponse(output)


class FacetedSearchView(BaseFacetedSearchView):

  form_class = FacetedPostSearchForm
  facet_fields = ['text', 'title']
  template_name = 'search_result.html'
  paginate_by = 3
  context_object_name = 'object_list'

  def get_context_data(self, **kwargs):
        context = super(FacetedSearchView, self).get_context_data(**kwargs)
        context['post_list'] = Post.objects.all()

        return context


#######################################
## Functions that require a pk match ##
#######################################

@login_required
def post_publish(request, pk):
    post = get_object_or_404(Post, pk=pk)
    status=post.publish()
    if status:
        return redirect('post_detail', pk=pk)
    else:
        return render(request,'blog/post_detail.html', {'post':post, 'publish_error':True} )

@login_required
def add_comment_to_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect('post_detail', pk=post.pk)
    else:
        form = CommentForm()
    return render(request, 'blog/comment_form.html', {'form': form})


@login_required
def comment_approve(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    comment.approve()
    return redirect('post_detail', pk=comment.post.pk)


@login_required
def comment_remove(request, pk):
    comment = get_object_or_404(Comment, pk=pk)
    post_pk = comment.post.pk
    comment.delete()
    return redirect('post_detail', pk=post_pk)
