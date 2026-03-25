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

    # ▼ スマホSafari対策
    if isinstance(tag, list):
        tag = tag[0]

    if tag in ["", None]:
        tag = None

    # ▼ ベースのクエリ
    qs = Thread.objects.all()

    # ▼ 絞り込み
    if tag:
        qs = qs.filter(tags__name=tag)

    if search:
        qs = qs.filter(title__icontains=search)

    # ▼ 並び替え（デフォルトは updated）
    if not sort:
        sort = "updated"

    # ▼ updated（最新順）
    if sort == "updated":
        qs = qs.order_by("-updated_at")
        threads = qs[:20]

    # ▼ reply_count（レス数順）
    elif sort == "reply_count":
        qs = qs.annotate(num_replies=Count("replies")).order_by("-num_replies")
        threads = qs[:20]

    # ▼ momentum（勢い順）
    elif sort == "momentum":
        threads = sorted(qs, key=lambda t: t.momentum, reverse=True)[:20]

    # ▼ 想定外 → updated
    else:
        qs = qs.order_by("-updated_at")
        threads = qs[:20]

    # ▼ 件数
    count = qs.count()

    zucks_ad = '<script type="text/javascript" src="https://j.zucks.net.zimg.jp/j?f=722853"></script>'

    return render(request, "board/thread_list.html", {
        "threads": threads,
        "sort": sort,
        "tag": tag,
        "q": search,
        "count": count,
        "all_tags": Tag.objects.all(),
        "zucks_ad": zucks_ad,
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

    # ★ POST（返信投稿）処理
    if request.method == "POST":
        content = request.POST.get("content", "")
        image_file = request.FILES.get("image_file")
        video_file = request.FILES.get("video_file")

        image_url = upload_to_r2_thread(image_file) if image_file else None
        video_url = upload_to_r2_thread(video_file) if video_file else None

        Reply.objects.create(
            thread=thread,
            content=content,
            image=image_url,
            video=video_url,
        )

        return redirect("thread_detail", thread_id=thread.id)

    # ★ GET（表示）
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
            "image": r.image,
            "video": r.video,
        })

    # ★★★ ここに広告タグを置く（正しい位置） ★★★
    zucks_ad = '<script type="text/javascript" src="https://j.zucks.net.zimg.jp/j?f=722853"></script>'

    return render(request, "board/thread_detail.html", {
        "thread": thread,
        "replies": numbered,
        "total": total,
        "zucks_ad": zucks_ad,   # ← 追加
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
