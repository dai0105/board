let offset = document.querySelectorAll("#thread-list .card").length;
let sort = SORT_FROM_TEMPLATE;
let tag = TAG_FROM_TEMPLATE;
let search = SEARCH_FROM_TEMPLATE;

document.getElementById("load-more-btn").addEventListener("click", function() {
    console.log("load more clicked. offset=", offset);

    fetch(`/threads/load_more/?offset=${offset}&sort=${sort}&tag=${tag}&q=${search}`)
        .then(res => res.json())
        .then(data => {
            console.log("load_more result:", data);

            if (!data.threads || data.threads.length === 0) {
                document.getElementById("load-more-btn").innerText = "これ以上ありません";
                return;
            }

            const list = document.getElementById("thread-list");

            data.threads.forEach(t => {
                const a = document.createElement("a");
                a.href = `/thread/${t.id}/`;
                a.classList.add("card");
                a.id = `thread-${t.id}`;

                a.innerHTML = `
                    <div class="icon">
                        ${t.icon ? `<img src="${t.icon}" alt="icon">` : ""}
                    </div>
                    <div class="info">
                        <div class="title">${t.title}</div>
                        <div class="preview">${(t.content || "").replace(/\n/g, "<br>")}</div>
                        <div class="tags">
                            ${(t.tags || []).map(tag => `<span class="tag">${tag}</span>`).join("")}
                        </div>
                        <div class="meta">
                            レス: ${t.reply_count}　
                            勢い: ${t.momentum}　
                            更新: ${timeSince(t.updated)}
                        </div>
                    </div>
                `;

                list.appendChild(a);
            });

            offset += data.threads.length;
        });
});