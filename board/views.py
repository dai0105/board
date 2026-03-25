from django.shortcuts import render, redirect, get_object_or_404
from .models import Thread, Reply
from .forms import ThreadForm, ReplyForm
from django.db.models import Q, Count
from .models import Thread, Tag
from .utils import upload_to_r2_thread
from django.http import JsonResponse

def thread_list(request):
    sort = request.GET.get("sort")
    tag = request.GET.get("tag")
    search = request.GET.get("q")

    if isinstance(tag, list):
        tag = tag[0]

    if tag in ["", None]:
        tag = None

    qs = Thread.objects.all()

    if tag:
        qs = qs.filter(tags__name=tag)

    if search:
        qs = qs.filter(title__icontains=search)

    if not sort:
        sort = "updated"

    if sort == "updated":
        qs = qs.order_by("-updated_at")
        threads = qs[:20]

    elif sort == "reply_count":
        qs = qs.annotate(num_replies=Count("replies")).order_by("-num_replies")
        threads = qs[:20]

    elif sort == "momentum":
        threads = sorted(qs, key=lambda t: t.momentum, reverse=True)[:20]

    else:
        qs = qs.order_by("-updated_at")
        threads = qs[:20]

    count = qs.count()

    return render(request, "board/thread_list.html", {
        "threads": threads,
        "sort": sort,
        "tag": tag,
        "q": search,
        "count": count,
        "all_tags": Tag.objects.all(),
    })



def load_more_threads(request):
    offset = int(request.GET.get("offset", 0))
    sort = request.GET.get("sort")
    tag = request.GET.get("tag")
    search = request.GET.get("q")

    qs = Thread.objects.all()

    # ▼ 絞り込み
    if tag:
        qs = qs.filter(tags__name=tag)

    if search:
        qs = qs.filter(title__icontains=search)

    # ▼ 並び替え
    if not sort:
        sort = "updated"

    if sort == "updated":
        qs = qs.filter(updated_at__isnull=False).order_by("-updated_at")

    elif sort == "reply_count":
        qs = qs.annotate(num_replies=Count("replies")).order_by("-num_replies")

    elif sort == "momentum":
        # momentum だけは Python リストに変換
        qs = list(qs)
        qs = sorted(qs, key=lambda t: t.momentum, reverse=True)

        # offset → 20件切り出し
        threads = qs[offset:offset+20]

        # 空なら空配列
        if not threads:
            return JsonResponse({"threads": []})

        # JSON 生成
        data = []
        for t in threads:
            data.append({
                "id": t.id,
                "title": t.title,
                "content": t.content,
                "updated": t.updated_at.isoformat() if t.updated_at else "",
                "reply_count": t.replies.count(),
                "momentum": t.momentum,
                "tags": [tag.name for tag in t.tags.all()],
                "icon": t.icon.url if t.icon else None,
            })
        return JsonResponse({"threads": data})

    else:
        qs = qs.filter(updated_at__isnull=False).order_by("-updated_at")

    # ▼ offset が範囲外なら空を返す（ここが重要）
    total = qs.count()
    if offset >= total:
        return JsonResponse({"threads": []})

    # ▼ 最後に threads を切り出す
    threads = qs[offset:offset+20]

    # ▼ JSON 生成
    data = []
    for t in threads:
        data.append({
            "id": t.id,
            "title": t.title,
            "content": t.content,
            "updated": t.updated_at.isoformat() if t.updated_at else "",
            "reply_count": t.replies.count(),
            "momentum": t.momentum,
            "tags": [tag.name for tag in t.tags.all()],
            "icon": t.icon.url if t.icon else None,
        })

    return JsonResponse({"threads": data})


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
