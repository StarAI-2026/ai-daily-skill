# -*- coding: utf-8 -*-
"""
typeset_gzh.py - 把 ai-daily-skill 产出的 article.md 排成 gzh-design-skill 摸鱼绿主题的
纯片段公众号 HTML（article.html）。

用法:
    python typeset_gzh.py <article.md> <output.html> [--date YYYY.MM.DD] [--brand "StarAI开源日报"]

特性:
    - 封面卡(组件2) + 横向目录(组件3) + 引言卡(组件9b) + 今日速览胶囊(组件11a)
    - ## 章节 -> PART 0X 章节标题(组件4)；### 子标题 -> 黄色下划线小节标题(组件9c)
    - 普通段落(组件5) 内联 **加粗->绿粗(6a)** / `code`(6g) / ++下划线(6e)** / ==高亮(6c)** / ~~删除线(6i)**
    - 图片(组件12a) 相对路径；结尾三连 CTA(组件13a)
    - 全内联样式 + <span leaf=""> 包裹，可直接被 wechat-api.ts 吃进去发布
    - 最后一个 hr 之后若只剩段落，自动归入“写在最后”(PART ///) 章节

依赖: 仅标准库
"""
import sys
import re
import os

# ---------- 设计变量（来自 theme-moyu-green.md） ----------
FONT_STACK = "-apple-system,BlinkMacSystemFont,'PingFang SC','Hiragino Sans GB','Microsoft YaHei',sans-serif"

# ---------- 内联标记正则 ----------
TOKEN_RE = re.compile(r'\*\*(.+?)\*\*|`(.+?)`|\+\+(.+?)\+\+|==(.+?)==|~~(.+?)~~')


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def normalize_quotes(text):
    """把英文直引号 \" 交替转成中文弯引号 “ ”，消除半角标点 warning。"""
    out = []
    open_q = True
    for ch in text:
        if ch == '"':
            out.append('“' if open_q else '”')
            open_q = not open_q
        else:
            out.append(ch)
    return ''.join(out)


def render_inline(text):
    """把一段文字按内联标记转成带 span leaf 包裹的 HTML 片段。"""
    text = normalize_quotes(text)
    segments = []
    pos = 0
    for m in TOKEN_RE.finditer(text):
        if m.start() > pos:
            segments.append(('text', text[pos:m.start()]))
        if m.group(1) is not None:
            segments.append(('bold', m.group(1)))
        elif m.group(2) is not None:
            segments.append(('code', m.group(2)))
        elif m.group(3) is not None:
            segments.append(('underline', m.group(3)))
        elif m.group(4) is not None:
            segments.append(('highlight', m.group(4)))
        elif m.group(5) is not None:
            segments.append(('strike', m.group(5)))
        pos = m.end()
    if pos < len(text):
        segments.append(('text', text[pos:]))

    out = []
    for typ, content in segments:
        c = esc(content)
        if typ == 'text':
            out.append('<span leaf="">' + c + '</span>')
        elif typ == 'bold':
            out.append('<strong style="color:#059669;"><span leaf="">' + c + '</span></strong>')
        elif typ == 'code':
            out.append('<span style="background:#F3F4F6;color:#1F2937;padding:2px 6px;border-radius:4px;font-size:13px;font-weight:600;"><span leaf="">' + c + '</span></span>')
        elif typ == 'underline':
            out.append('<span style="border-bottom:2px solid #A7F3D0;font-weight:600;"><span leaf="">' + c + '</span></span>')
        elif typ == 'highlight':
            out.append('<span style="background:linear-gradient(120deg,#FDE68A 0%,rgba(255,255,255,0) 100%);padding:0 4px;border-radius:2px;font-weight:600;color:#111827;"><span leaf="">' + c + '</span></span>')
        elif typ == 'strike':
            out.append('<span style="background:#F3F4F6;color:#6B7280;padding:2px 6px;border-radius:4px;font-size:13px;text-decoration:line-through;font-weight:600;"><span leaf="">' + c + '</span></span>')
    return ''.join(out)


def strip_markers(text):
    return TOKEN_RE.sub(lambda m: m.group(1) or m.group(2) or m.group(3) or m.group(4) or m.group(5), text)


# ---------- 组件渲染 ----------
def cover_card(date_str, brand, title_main, title_hl, title_line2, subtitle, old_belief, tag1, tag2):
    return (
        '<section style="margin:0 0 32px;background:#fff;border:1.5px solid rgba(5,150,105,0.15);border-radius:20px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.06);width:100%;">'
        '<section style="padding:32px 28px 28px;">'
        '<section style="display:flex;align-items:center;gap:8px;margin-bottom:28px;">'
        '<span style="width:6px;height:6px;background:#059669;border-radius:50%;"><span leaf=""><br></span></span>'
        '<span style="font-size:11px;font-weight:700;letter-spacing:3px;color:#059669;"><span leaf="">' + esc(brand) + ' · ' + esc(date_str) + '</span></span>'
        '<section style="flex:1;height:1px;overflow:hidden;background:linear-gradient(to right,rgba(5,150,105,0.12),transparent);"><span leaf=""><br></span></section>'
        '<span style="font-size:10px;color:#D1D5DB;font-weight:600;"><span leaf="">BREAKING</span></span>'
        '</section>'
        '<section style="display:flex;align-items:center;gap:20px;">'
        '<section style="flex:1;min-width:0;">'
        '<p style="font-size:15px;color:#D1D5DB;margin:0 0 6px;text-decoration:line-through;letter-spacing:0.5px;"><span leaf="">' + esc(old_belief) + '</span></p>'
        '<p style="font-size:24px;font-weight:900;color:#111827;margin:0;line-height:1.05;letter-spacing:-2px;"><span leaf="">' + esc(title_main) + '</span><span style="color:#059669;"><span leaf="">' + esc(title_hl) + '</span></span></p>'
        '<p style="font-size:24px;font-weight:900;color:#059669;margin:0 0 16px;line-height:1.05;letter-spacing:-2px;"><span leaf="">' + esc(title_line2) + '</span></p>'
        '<section style="width:48px;height:3px;background:linear-gradient(to right,#059669,#34D399);border-radius:2px;margin-bottom:12px;"><span leaf=""><br></span></section>'
        '<p style="font-size:13px;color:#9CA3AF;margin:0;line-height:1.7;letter-spacing:0.5px;"><span leaf="">' + esc(subtitle) + '</span></p>'
        '</section>'
        '<section style="flex-shrink:0;width:110px;height:110px;border-radius:16px;overflow:hidden;border:1px solid rgba(5,150,105,0.1);box-shadow:0 4px 12px rgba(0,0,0,0.06);">'
        '<span leaf=""><img src="cover.png" style="width:100%;height:100%;object-fit:cover;display:block;"></span>'
        '</section>'
        '</section>'
        '</section>'
        '<section style="background:linear-gradient(135deg,#059669,#10B981);padding:12px 28px;display:flex;align-items:center;justify-content:space-between;">'
        '<p style="font-size:12px;color:rgba(255,255,255,0.9);margin:0;font-weight:600;letter-spacing:0.5px;"><span leaf="">' + esc(brand) + '</span></p>'
        '<section style="display:flex;gap:4px;">'
        '<span style="background:rgba(255,255,255,0.2);padding:1px 6px;border-radius:3px;font-size:8px;color:#fff;font-weight:600;"><span leaf="">' + esc(tag1) + '</span></span>'
        '<span style="background:rgba(255,255,255,0.2);padding:1px 6px;border-radius:3px;font-size:8px;color:#fff;font-weight:600;"><span leaf="">' + esc(tag2) + '</span></span>'
        '</section>'
        '</section>'
        '</section>'
    )


def toc(parts):
    """parts: list of (part_label, title, subtitle) 含写在最后。"""
    cards = []
    for idx, (label, title, subtitle) in enumerate(parts):
        if idx == 0:
            card = (
                '<section style="display:inline-block;white-space:normal;vertical-align:top;width:110px;background:linear-gradient(135deg,#059669,#10B981);border-radius:12px;padding:12px;margin-right:8px;">'
                '<p style="font-size:9px;font-weight:700;color:rgba(255,255,255,0.7);letter-spacing:1px;margin:0 0 5px;"><span leaf="">' + esc(label) + '</span></p>'
                '<p style="font-size:13px;font-weight:800;color:#fff;margin:0 0 3px;"><span leaf="">' + esc(title) + '</span></p>'
                '<p style="font-size:10px;color:rgba(255,255,255,0.7);margin:0;"><span leaf="">' + esc(subtitle) + '</span></p>'
                '</section>'
            )
        else:
            card = (
                '<section style="display:inline-block;white-space:normal;vertical-align:top;width:110px;background:#fff;border:1px solid #E5E7EB;border-radius:12px;padding:12px;margin-right:8px;box-shadow:0 2px 6px rgba(0,0,0,0.04);">'
                '<p style="font-size:9px;font-weight:700;color:#9CA3AF;letter-spacing:1px;margin:0 0 5px;"><span leaf="">' + esc(label) + '</span></p>'
                '<p style="font-size:13px;font-weight:800;color:#111827;margin:0 0 3px;"><span leaf="">' + esc(title) + '</span></p>'
                '<p style="font-size:10px;color:#9CA3AF;margin:0;"><span leaf="">' + esc(subtitle) + '</span></p>'
                '</section>'
            )
        cards.append(card)
    n = len(parts) - 1  # 去掉写在最后
    return (
        '<section style="margin:0 20px 32px;">'
        '<section style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">'
        '<p style="font-size:10px;color:#9CA3AF;margin:0;text-transform:uppercase;letter-spacing:2px;font-weight:600;"><span leaf="">📦 ' + str(n) + ' Parts + Conclusion</span></p>'
        '<p style="font-size:10px;color:#9CA3AF;margin:0;"><span leaf="">👉 滑动</span></p>'
        '</section>'
        '<section style="overflow-x:scroll;-webkit-overflow-scrolling:touch;white-space:nowrap;padding-bottom:8px;">'
        + ''.join(cards) +
        '</section>'
        '</section>'
    )


def intro_card(lead, highlight):
    return (
        '<section style="background:#FFF;border:1px dashed #BBF7D0;border-radius:8px;padding:14px 16px;margin:0 20px 24px;text-align:center;">'
        '<p style="font-size:12px;color:#9CA3AF;margin:0 0 6px;line-height:1.5;"><span leaf="">' + esc(lead) + '</span></p>'
        '<p style="margin:0;line-height:1.6;"><span style="font-size:15px;color:#059669;font-weight:bold;border-bottom:3px solid #FDE68A;padding-bottom:2px;"><span leaf="">' + esc(highlight) + '</span></span></p>'
        '</section>'
    )


def overview_pills(items):
    """items: list of (label, desc)"""
    blocks = []
    for label, desc in items:
        blocks.append(
            '<section style="margin-bottom:14px;">'
            '<p style="margin:0 0 6px;">'
            '<span style="display:inline-block;font-size:13px;font-weight:700;color:#059669;background:rgba(5,150,105,0.08);padding:3px 10px;border-radius:999px;">'
            '<span style="display:inline-block;width:6px;height:6px;background:#059669;border-radius:50%;margin-right:5px;vertical-align:middle;"><span leaf=""><br></span></span>'
            '<span leaf="">' + esc(label) + '</span></span>'
            '</p>'
            '<p style="font-size:13px;color:#4B5563;margin:0;line-height:1.7;text-align:justify;"><span leaf="">' + esc(desc) + '</span></p>'
            '</section>'
        )
    return (
        '<section style="padding:0 20px;margin-top:32px;">'
        '<p style="font-size:15px;font-weight:900;color:#111827;margin-bottom:16px;">'
        '<span style="background:linear-gradient(180deg,transparent 65%,#FDE68A 65%);padding:0 4px;"><span leaf="">今日速览</span></span>'
        '</p>'
        + ''.join(blocks) +
        '</section>'
    )


def chapter_title(num, title, subtitle, is_first, is_last):
    margin_top = '16px' if is_first else '48px'
    part_label = 'LAST' if is_last else 'PART'
    num_label = '///' if is_last else num
    return (
        '<section style="margin-top:' + margin_top + ';margin-bottom:32px;padding:0 20px;">'
        '<section style="display:flex;align-items:center;gap:16px;margin-bottom:24px;">'
        '<section style="text-align:center;flex-shrink:0;">'
        '<p style="margin:0;font-size:28px;font-weight:900;color:#059669;line-height:1;letter-spacing:-2px;"><span leaf="">' + esc(num_label) + '</span></p>'
        '<p style="margin:0;font-size:8px;font-weight:700;color:#D1D5DB;letter-spacing:2px;"><span leaf="">' + esc(part_label) + '</span></p>'
        '</section>'
        '<span style="width:1px;height:36px;background:#E5E7EB;flex-shrink:0;"><span leaf=""><br></span></span>'
        '<section>'
        '<p style="margin:0 0 1px;font-size:17px;font-weight:900;color:#111827;letter-spacing:0.3px;"><span leaf="">' + esc(title) + '</span></p>'
        '<p style="margin:0;font-size:11px;font-weight:600;color:#9CA3AF;letter-spacing:1.5px;"><span leaf="">' + esc(subtitle) + '</span></p>'
        '</section>'
        '</section>'
    )


def subtitle_highlight(text):
    return (
        '<p style="font-size:15px;font-weight:900;color:#111827;margin-bottom:16px;margin-top:24px;">'
        '<span style="background:linear-gradient(180deg,transparent 65%,#FDE68A 65%);padding:0 4px;"><span leaf="">' + esc(strip_markers(text)) + '</span></span>'
        '</p>'
    )


def paragraph(text):
    return (
        '<p style="margin-bottom:16px;font-size:14px;line-height:1.9;text-align:justify;">'
        + render_inline(text) +
        '</p>'
    )


def image_block(src):
    return (
        '<section style="text-align:center;margin-bottom:24px;border-radius:12px;overflow:hidden;">'
        '<img src="' + esc(src) + '" style="max-width:100%;height:auto;display:block;margin:0 auto;">'
        '</section>'
    )


def quote_box(text):
    return (
        '<section style="background:#F9FAFB;border:1px dashed #D1D5DB;border-radius:8px;padding:12px 16px;margin-bottom:24px;text-align:justify;">'
        '<p style="font-size:13px;color:#374151;margin:0;line-height:1.6;">' + render_inline(text) + '</p>'
        '</section>'
    )


def content_wrap(inner):
    return (
        '<section style="padding:0 20px;">'
        + inner +
        '</section>'
    )


def ranked_list(items):
    """items: list of markdown 行（已去掉 'N. '）。渲染为带排名徽章的榜单行。"""
    rows = []
    for idx, it in enumerate(items, 1):
        rows.append(
            '<section style="display:flex;gap:12px;align-items:flex-start;padding:12px 0;border-bottom:1px solid #F3F4F6;">'
            '<span style="flex-shrink:0;width:26px;height:26px;border-radius:8px;background:linear-gradient(135deg,#059669,#10B981);'
            'color:#fff;font-size:13px;font-weight:900;display:flex;align-items:center;justify-content:center;">'
            '<span leaf="">' + str(idx) + '</span></span>'
            '<span style="flex:1;font-size:14px;line-height:1.7;color:#374151;"><span leaf="">'
            + render_inline(it) +
            '</span></span>'
            '</section>'
        )
    return (
        '<section style="background:#fff;border:1px solid #E5E7EB;border-radius:12px;padding:8px 16px;margin-bottom:24px;">'
        + ''.join(rows) +
        '</section>'
    )


def footer_cta():
    return (
        '<section style="background:radial-gradient(circle at center,#F9FAFB 0%,#FFFFFF 100%);border:1px solid #E5E7EB;border-radius:16px;padding:32px 20px;text-align:center;box-shadow:0 4px 12px rgba(0,0,0,0.03);margin:0 0 24px;">'
        '<p style="font-size:13px;font-weight:bold;color:#111827;margin-bottom:20px;line-height:1.6;"><span leaf="">既然看到这里了，如果觉得有用，随手点个赞、在看、转发三连吧。</span></p>'
        '<section style="display:flex;justify-content:center;gap:24px;margin-bottom:16px;">'
        '<section style="text-align:center;cursor:pointer;color:#4B5563;">'
        '<section style="width:40px;height:40px;display:flex;align-items:center;justify-content:center;margin:0 auto 6px;background:#fff;border-radius:12px;box-shadow:0 2px 4px rgba(0,0,0,0.05);border:1px solid #F3F4F6;">'
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path></svg>'
        '</section><span style="font-size:10px;font-weight:600;"><span leaf="">点赞</span></span></section>'
        '<section style="text-align:center;cursor:pointer;color:#4B5563;">'
        '<section style="width:40px;height:40px;display:flex;align-items:center;justify-content:center;margin:0 auto 6px;background:#fff;border-radius:12px;box-shadow:0 2px 4px rgba(0,0,0,0.05);border:1px solid #F3F4F6;">'
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="12" r="3"></circle><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path></svg>'
        '</section><span style="font-size:10px;font-weight:600;"><span leaf="">在看</span></span></section>'
        '<section style="text-align:center;cursor:pointer;color:#059669;">'
        '<section style="width:40px;height:40px;display:flex;align-items:center;justify-content:center;margin:0 auto 6px;background:#ECFDF5;border-radius:12px;box-shadow:0 2px 4px rgba(5,150,105,0.15);border:1px solid #A7F3D0;">'
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 18v-4a8 8 0 0 1 8-8h8"></path><polyline points="16 2 20 6 16 10"></polyline></svg>'
        '</section><span style="font-size:10px;font-weight:600;"><span leaf="">转发</span></span></section>'
        '</section>'
        '<p style="font-size:10px;color:#9CA3AF;letter-spacing:1px;margin:0;"><span leaf="">THANKS FOR READING</span></p>'
        '</section>'
    )


# ---------- 解析 ----------
def parse_frontmatter(md):
    lines = md.split('\n')
    if not lines or lines[0].strip() != '---':
        return {}, md
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end = i
            break
    if end is None:
        return {}, md
    fm = {}
    for ln in lines[1:end]:
        if ':' in ln:
            k, v = ln.split(':', 1)
            fm[k.strip()] = v.strip()
    return fm, '\n'.join(lines[end + 1:])


def parse_blocks(body):
    lines = body.split('\n')
    blocks = []
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        if line.strip() == '':
            i += 1
            continue
        # hr
        if re.match(r'^-{3,}\s*$', line.strip()):
            blocks.append(('hr', ''))
            i += 1
            continue
        if line.startswith('## '):
            blocks.append(('h2', line[3:].strip()))
            i += 1
            continue
        if line.startswith('### '):
            blocks.append(('h3', line[4:].strip()))
            i += 1
            continue
        if line.lstrip().startswith('![') and '](' in line:
            m = re.search(r'!\[([^\]]*)\]\(([^)]+)\)', line)
            if m:
                blocks.append(('img', m.group(2).strip()))
            i += 1
            continue
        if line.startswith('> '):
            buf = []
            while i < n and lines[i].startswith('> '):
                buf.append(lines[i][2:].strip())
                i += 1
            blocks.append(('quote', ' '.join(buf)))
            continue
        if line.startswith('- '):
            buf = []
            while i < n and lines[i].startswith('- '):
                buf.append(lines[i][2:].strip())
                i += 1
            blocks.append(('list', buf))
            continue
        if re.match(r'^\d+\.\s', line.lstrip()):
            buf = []
            while i < n and re.match(r'^\d+\.\s', lines[i].lstrip()):
                buf.append(re.sub(r'^\d+\.\s', '', lines[i].lstrip()))
                i += 1
            blocks.append(('olist', buf))
            continue
        # paragraph: gather consecutive plain lines
        buf = [line.strip()]
        i += 1
        while i < n and lines[i].strip() != '' and not re.match(r'^(## |### |!\[|> |-{3,}\s*$)', lines[i].strip()):
            buf.append(lines[i].strip())
            i += 1
        blocks.append(('p', ' '.join(buf)))
    return blocks


def parse_overview_item(item):
    """ '- **Name** ⭐446 — desc' -> (Name, '⭐446 — desc')"""
    item = item.strip()
    name = None
    rest = item
    m = re.match(r'^\*\*(.+?)\*\*\s*(.*)$', item)
    if m:
        name = m.group(1).strip()
        rest = m.group(2).strip()
    else:
        # 没有加粗：取第一个空格前
        if ' ' in item:
            name, rest = item.split(' ', 1)
        else:
            name, rest = item, ''
    return name, rest


def build(md_path, out_path, date_str, brand):
    with open(md_path, 'r', encoding='utf-8') as f:
        md = f.read()
    fm, body = parse_frontmatter(md)
    title = fm.get('title', '每日日报')
    author = fm.get('author', 'Star_Ai')
    description = fm.get('description', '')

    blocks = parse_blocks(body)

    # 找 今日速览 头
    overview_items = None
    overview_header_idx = -1
    for idx, b in enumerate(blocks):
        if b[0] == 'p' and strip_markers(b[1]).strip().rstrip('：:') == '今日速览':
            overview_header_idx = idx
            break
    if overview_header_idx >= 0 and overview_header_idx + 1 < len(blocks) and blocks[overview_header_idx + 1][0] == 'list':
        overview_items = [parse_overview_item(it) for it in blocks[overview_header_idx + 1][1]]
        # 删除 header 和 list 块
        blocks = blocks[:overview_header_idx] + blocks[overview_header_idx + 2:]

    # 找最后一个 hr，其后的纯段落作为“写在最后”
    closing = []
    last_hr = -1
    for idx, b in enumerate(blocks):
        if b[0] == 'hr':
            last_hr = idx
    if last_hr >= 0 and all(b[0] == 'p' for b in blocks[last_hr + 1:]):
        closing = [b[1] for b in blocks[last_hr + 1:]]
        blocks = blocks[:last_hr]

    # 拆章节：按第一个 h2 把 blocks 分为 pre（前言/封面）与 chapters
    first_h2 = next((i for i, b in enumerate(blocks) if b[0] == 'h2'), None)
    pre_blocks = blocks[:first_h2] if first_h2 is not None else []
    chapters = []
    cur = None
    chapter_blocks = []
    for b in (blocks[first_h2:] if first_h2 is not None else []):
        if b[0] == 'h2':
            if cur is not None:
                chapters.append((cur, chapter_blocks))
            cur = b[1]
            chapter_blocks = []
        else:
            chapter_blocks.append(b)
    if cur is not None:
        chapters.append((cur, chapter_blocks))

    # 提取封面图（pre 中第一个 img）
    cover_src = None
    pre_paras = []
    for b in pre_blocks:
        if b[0] == 'img' and cover_src is None:
            cover_src = b[1]
        elif b[0] == 'p':
            pre_paras.append(b[1])
        elif b[0] == 'quote':
            pre_paras.append(b[1])
    if cover_src is None:
        cover_src = 'cover.png'
    greeting = pre_paras[0] if pre_paras else '欢迎阅读今日日报'
    preface = pre_paras[1:] if len(pre_paras) > 1 else []

    # 封面卡文案（视角错开，不照搬标题关键词）
    cover_old = 'GitHub只是程序员看的？'
    cover_main = '今天GitHub'
    cover_hl = '冒出一批AI神器'
    cover_line2 = '语音编排·运动生成·命令行'
    cover_sub = '交互门槛再降一层'
    if 'AI' in title and 'GitHub' not in title:
        cover_old = '巨头之间不会互相拆台？'
        cover_main = '今天AI圈'
        cover_line2 = '多条动态速览'

    # 目录 parts
    toc_parts = []
    for ci, (ctitle, cblocks) in enumerate(chapters):
        h3_count = sum(1 for b in cblocks if b[0] == 'h3')
        t = ctitle.replace('【', '').replace('】', '').replace('[', '').replace(']', '')
        toc_parts.append(('PART ' + ('0' + str(ci + 1) if ci + 1 < 10 else str(ci + 1)),
                           t, str(h3_count) + ' 个开源项目'))
    toc_parts.append(('PART ///', '写在最后', '明天见'))

    # 组装
    html = []
    html.append('<section style="max-width:677px;margin:0 auto;background:#ffffff;font-family:' + FONT_STACK + ';color:#374151;line-height:1.75;letter-spacing:0.5px;overflow-x:hidden;">')

    html.append(cover_card(date_str, brand, cover_main, cover_hl, cover_line2, cover_sub, cover_old, '开源', 'AI'))
    html.append(toc(toc_parts))
    html.append(intro_card(strip_markers(greeting), description[:40] if description else '今日热门项目盘点'))
    # 前言
    if preface:
        html.append(content_wrap(''.join(paragraph(p) for p in preface)))
    # 今日速览
    if overview_items:
        html.append(overview_pills(overview_items))

    # 章节
    n_ch = len(chapters)
    for ci, (ctitle, cblocks) in enumerate(chapters):
        is_first = (ci == 0)
        is_last = (ci == n_ch - 1)
        t = ctitle.replace('【', '').replace('】', '').replace('[', '').replace(']', '')
        sub = str(sum(1 for b in cblocks if b[0] == 'h3')) + ' 个开源项目'
        html.append(chapter_title('0' + str(ci + 1) if ci + 1 < 10 else str(ci + 1), t, sub, is_first, is_last))
        inner = []
        for b in cblocks:
            if b[0] == 'h3':
                inner.append(subtitle_highlight(b[1]))
            elif b[0] == 'p':
                inner.append(paragraph(b[1]))
            elif b[0] == 'img':
                if b[1] == cover_src:
                    continue
                inner.append(image_block(b[1]))
            elif b[0] == 'quote':
                inner.append(quote_box(b[1]))
            elif b[0] == 'list':
                for it in b[1]:
                    nm, ds = parse_overview_item(it)
                    inner.append('<p style="margin-bottom:8px;font-size:14px;line-height:1.9;"><span leaf="">· </span>' + render_inline('**' + nm + '** ' + ds) + '</p>')
            elif b[0] == 'olist':
                inner.append(ranked_list(b[1]))
        html.append(content_wrap(''.join(inner)))

    # 写在最后
    if closing:
        html.append(chapter_title('///', '写在最后', '明天见', False, True))
        html.append(content_wrap(''.join(paragraph(p) for p in closing)))

    # 三连
    html.append(footer_cta())
    html.append('</section>')

    out = '\n'.join(html)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(out)
    return out


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: python typeset_gzh.py <article.md> <output.html> [--date YYYY.MM.DD] [--brand "StarAI开源日报"]')
        sys.exit(1)
    md_path = sys.argv[1]
    out_path = sys.argv[2]
    date_str = '2026.07.12'
    brand = 'StarAI开源日报'
    if '--date' in sys.argv:
        date_str = sys.argv[sys.argv.index('--date') + 1]
    if '--brand' in sys.argv:
        brand = sys.argv[sys.argv.index('--brand') + 1]
    build(md_path, out_path, date_str, brand)
    print('OK -> ' + out_path)
