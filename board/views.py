from django.shortcuts import render, redirect, get_object_or_404
from .models import Thread, Reply
from .forms import ThreadForm, ReplyForm
from django.db.models import Q
from .models import Thread, Tag
from .utils import upload_to_r2_thread
from django.http import JsonResponse

def thread_list(request):
    # ▼ パラメータ取得
    sort = request.GET.get("sort")
    tag = request.GET.get("tag")
    search = request.GET.get("q")

    # ▼ 必ず最初に qs を作る（超重要）
    qs = Thread.objects.all()

    # ▼ 絞り込み
    if tag:
        qs = qs.filter(tags__name=tag)

    if search:
        qs = qs.filter(title__icontains=search)

    # ▼ 並び替え（sort が空なら updated）
    if not sort:
        sort = "updated"

    if sort == "updated":
        qs = qs.order_by("-updated_at")
    elif sort == "momentum":
        qs = qs.order_by("-momentum")
    elif sort == "reply_count":
        qs = qs.order_by("-reply_count")
    else:
        qs = qs.order_by("-updated_at")

    # ▼ 最初の20件
    threads = qs[:20]

    return render(request, "board/thread_list.html", {
        "threads": threads,
        "sort": sort,
        "tag": tag,
        "q": search,
        "all_tags": Tag.objects.all(),
    })


def load_more_threads(request):
    # ▼ パラメータ取得
    offset = int(request.GET.get("offset", 0))
    sort = request.GET.get("sort")
    tag = request.GET.get("tag")
    search = request.GET.get("q")

    # ▼ 必ず最初に qs を作る（超重要）
    qs = Thread.objects.all()

    # ▼ 絞り込み
    if tag:
        qs = qs.filter(tags__name=tag)

    if search:
        qs = qs.filter(title__icontains=search)

    # ▼ 並び替え（sort が空なら updated）
    if not sort:
        sort = "updated"

    if sort == "updated":
        qs = qs.order_by("-updated_at")
    elif sort == "momentum":
        qs = qs.order_by("-momentum")
    elif sort == "reply_count":
        qs = qs.order_by("-reply_count")
    else:
        qs = qs.order_by("-updated_at")

    # ▼ offset から20件
    threads = qs[offset:offset+20]

    # ▼ JSON 形式に変換
    data = []
    for t in threads:
        data.append({
            "id": t.id,
            "title": t.title,
            "content": t.content,
            "updated": t.updated_at.isoformat(),
            "reply_count": t.replies.count(),
            "momentum": t.momentum,
            "tags": [tag.name for tag in t.tags.all()],
            "icon": t.icon.url if t.icon else None,
        })

    return JsonResponse({"threads": data})


def thread_create(request):
    if request.method == 'POST':
        form = ThreadForm(request.POST, request.FILES)

        # ★ ここでログを出す（form.is_valid() の前）
        print("=== DEBUG START ===")
        print("FILES:", request.FILES)
        print("POST:", request.POST)

        if form.is_valid():
            print("FORM VALID")
            thread = form.save(commit=False)

            # ★ R2 にアップロードして URL を取得
            image = request.FILES.get("icon")
            print("IMAGE:", image)  # ここもログ追加

            if image:
                thread.icon = upload_to_r2_thread(image)

            thread.save()
            form.save_m2m()
            print("=== DEBUG END (SUCCESS) ===")
            return redirect('thread_detail', thread.id)

        else:
            # ★ form が invalid のときの詳細ログ
            print("FORM INVALID")
            print("FORM ERRORS:", form.errors)
            print("=== DEBUG END (INVALID) ===")

    else:
        form = ThreadForm()

    return render(request, 'board/thread_create.html', {'form': form})


def thread_detail(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)

    total = thread.replies.count()

    # 新しい順で50件
    replies = list(thread.replies.all().order_by("-id")[:50])

    # 番号付け（新しい順）
    numbered = []
    for i, r in enumerate(replies):
        number = total - i
        numbered.append({
            "obj": r,
            "number": number,
        })

    return render(request, "board/thread_detail.html", {
        "thread": thread,
        "replies": numbered,
        "total": total,
    })

def load_more_replies(request, thread_id):
    thread = get_object_or_404(Thread, id=thread_id)

    offset = int(request.GET.get("offset", 0))

    # 新しい順で offset 以降を取得
    qs = thread.replies.all().order_by("-id")[offset:]

    total = thread.replies.count()

    data = []
    for i, r in enumerate(qs):
        # ★ 新しい順の正しい番号付け
        number = total - (offset + i)
        data.append({
            "number": number,
            "content": r.content,
            "image": r.image,
            "video": r.video,
            "created_at": r.created_at.strftime("%Y-%m-%d %H:%M"),
        })

    return JsonResponse({"replies": data})