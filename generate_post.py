#!/usr/bin/env python3
"""
generate_post.py - DeepSeek API로 Jekyll 블로그 포스트 자동 생성

Usage:
  # 단건 생성
  python generate_post.py --keyword "PDF 파일 합치기 무료" --kit pdf

  # 키워드 파일에서 N개 랜덤 생성
  python generate_post.py --batch 10

  # 특정 kit 키워드만 N개 생성
  python generate_post.py --batch 5 --kit pdf

  # 생성 후 GitHub 자동 push
  python generate_post.py --batch 10 --push
"""

import re
import json
import random
import argparse
import datetime
import subprocess
import unicodedata
from pathlib import Path
import requests

# ──── 설정 ────────────────────────────────────────────────────────────────────
SCRIPT_DIR    = Path(__file__).parent
POSTS_DIR     = SCRIPT_DIR / "_posts"
KEYWORDS_FILE = SCRIPT_DIR / "keywords.json"
API_KEY_PATH  = Path(r"C:\개인\개인 프로젝트\blogwriter_new\blogger_seo_bot\config\deepseek_api_key.txt")
BLOG_URL      = "https://blog.wooahouse.com"

KIT_INFO = {
    "pdf":    ("WooaPDF",    "https://pdfkit.wooahouse.com"),
    "이미지": ("WooaImage",  "https://imagekit.wooahouse.com"),
    "qr":     ("WooaQR",     "https://qrkit.wooahouse.com"),
    "텍스트": ("WooaText",   "https://textkit.wooahouse.com"),
    "색상":   ("WooaColor",  "https://colorkit.wooahouse.com"),
    "계산":   ("WooaCalc",   "https://calckit.wooahouse.com"),
    "ocr":    ("WooaOCR",    "https://wooaocr.wooahouse.com"),
    "오디오": ("WooaAudio",  "https://wooaaudio.wooahouse.com"),
    "동영상": ("WooaVideo",  "https://wooavideo.wooahouse.com"),
    "폰트":   ("FontKit",    "https://fontkit.wooahouse.com"),
    "개발":   ("WooaDev",    "https://wooadev.wooahouse.com"),
    "뷰어":   ("WooaViewer", "https://wooaviewer.wooahouse.com"),
    "시트":   ("WooaSheet",  "https://wooasheet.wooahouse.com"),
}

# 프롬프트 스타일 10가지 변주 (매번 랜덤 선택 → 글 구성이 달라짐)
PROMPT_STYLES = [
    "초보자도 쉽게 따라할 수 있는 친절한 단계별 가이드 스타일",
    "실무자를 위한 핵심만 담은 간결한 실용 정보 스타일",
    "문제 상황 → 원인 → 해결책 순으로 전개하는 문제 해결 스타일",
    "실제 사용해본 것처럼 자연스럽게 쓴 경험 공유 스타일",
    "자주 겪는 실수와 해결법을 중심으로 한 노하우 공유 스타일",
    "장단점을 솔직하게 짚어주는 균형 잡힌 리뷰 스타일",
    "시간 절약과 업무 효율에 초점을 맞춘 생산성 팁 스타일",
    "직장인·학생의 일상 속 실제 활용 시나리오 중심 스타일",
    "왜 이 방법이 최선인지 논리적으로 설명하는 설득형 스타일",
    "비교 분석을 통해 이 도구의 강점을 드러내는 비교 스타일",
]

# ──── 유틸 ────────────────────────────────────────────────────────────────────

def get_api_key() -> str:
    return API_KEY_PATH.read_text(encoding="utf-8").strip()

def slugify(text: str) -> str:
    """한글 포함 문자열을 Jekyll URL-safe slug로 변환"""
    # 한글은 그대로 유지, 특수문자 제거, 공백→하이픈
    text = re.sub(r'[^\w\s가-힣]', '', text)
    text = re.sub(r'\s+', '-', text.strip())
    return text[:60].strip('-')

def today_str() -> str:
    return datetime.date.today().isoformat()

# ──── 글 생성 ────────────────────────────────────────────────────────────────

def generate_post(keyword: str, kit: str) -> dict:
    """DeepSeek API로 포스트 생성. title/desc/tags/body 딕셔너리 반환."""
    api_key = get_api_key()
    kit_name, kit_url = KIT_INFO.get(kit, ("WooaHouse", "https://wooahouse.com"))
    style = random.choice(PROMPT_STYLES)

    # 글 구조도 랜덤으로 약간씩 변주
    structures = [
        "① 도입(공감) ② 도구 소개 + URL ③ 주요 기능 ④ 활용 팁 ⑤ 마무리 + URL",
        "① 도입(문제 제시) ② 해결책으로 도구 소개 + URL ③ 사용법 단계별 ④ 주의사항 ⑤ 마무리 + URL",
        "① 도입(시나리오) ② 도구 첫 소개 + URL ③ 기능 상세 ④ 실제 사용 후기 ⑤ 마무리 + URL",
    ]
    structure = random.choice(structures)

    prompt = f"""당신은 SEO에 최적화된 한국어 블로그 글을 작성하는 전문 작가입니다.

[이번 글 정보]
▶ 타겟 키워드: {keyword}
▶ 소개할 도구: {kit_name} ({kit_url})
▶ 작성 스타일: {style}
▶ 글 구조: {structure}

[작성 조건]
■ 제목
  - 타겟 키워드를 제목 앞쪽에 포함
  - 30~60자, 검색 클릭을 유도하는 자연스러운 제목
  - 이모지·특수기호 사용 금지

■ 본문 (마크다운 형식, 1200~1800자)
  - ## 소제목으로 섹션 구분
  - URL은 위 구조의 ②번과 ⑤번 위치에 각 1회씩, 총 2회 포함
  - URL 형식: 텍스트 앞뒤에 공백 없이 그대로 입력 (링크 태그 불필요)
  - 과장 극찬 금지, 단점 1개 자연스럽게 언급 가능
  - 실제 사용하는 사람 관점에서 자연스럽게 작성

■ 메타 설명 (120~160자)
  - 타겟 키워드 포함, 클릭을 유도하는 문장

■ 태그 (5~8개, 쉼표 구분)
  - 타겟 키워드와 연관된 검색어

■ 출력 형식 (반드시 아래 형식만 사용)
[TITLE]제목[/TITLE]
[DESC]메타 설명[/DESC]
[TAGS]태그1,태그2,태그3[/TAGS]
[BODY]
마크다운 본문 내용
[/BODY]"""

    resp = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 3000,
            "temperature": 0.9,
        },
        timeout=90,
    )
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"]

    title_m = re.search(r"\[TITLE\](.*?)\[/TITLE\]", raw, re.DOTALL)
    desc_m  = re.search(r"\[DESC\](.*?)\[/DESC\]",   raw, re.DOTALL)
    tags_m  = re.search(r"\[TAGS\](.*?)\[/TAGS\]",   raw, re.DOTALL)
    body_m  = re.search(r"\[BODY\](.*?)\[/BODY\]",   raw, re.DOTALL)

    if not all([title_m, desc_m, tags_m, body_m]):
        raise ValueError(f"응답 파싱 실패. 앞 300자:\n{raw[:300]}")

    return {
        "title": title_m.group(1).strip(),
        "desc":  desc_m.group(1).strip(),
        "tags":  tags_m.group(1).strip(),
        "body":  body_m.group(1).strip(),
    }

# ──── 저장 ────────────────────────────────────────────────────────────────────

def save_post(data: dict, keyword: str, kit: str) -> Path:
    today = today_str()
    slug  = slugify(data["title"]) or slugify(keyword)
    filename = f"{today}-{slug}.md"
    filepath = POSTS_DIR / filename

    # 중복 파일명 처리
    counter = 1
    while filepath.exists():
        filepath = POSTS_DIR / f"{today}-{slug}-{counter}.md"
        counter += 1

    tags_list = [t.strip() for t in data["tags"].split(",") if t.strip()]
    tags_yaml = "\n".join(f'  - "{t}"' for t in tags_list)

    title_safe = data["title"].replace('"', "'")
    desc_safe  = data["desc"].replace('"', "'")

    front_matter = f"""---
layout: post
title: "{title_safe}"
date: {today}
description: "{desc_safe}"
categories:
  - "{kit}"
tags:
{tags_yaml}
kit: "{kit}"
---

"""
    filepath.write_text(front_matter + data["body"], encoding="utf-8")
    print(f"  [저장] {filepath.name}")
    return filepath

# ──── Git Push ────────────────────────────────────────────────────────────────

def git_push(count: int):
    msg = f"Add {count} blog post(s) {today_str()}"
    repo = str(SCRIPT_DIR)
    subprocess.run(["git", "-C", repo, "add", "_posts/"], check=True)
    subprocess.run(["git", "-C", repo, "commit", "-m", msg], check=True)
    subprocess.run(["git", "-C", repo, "push"], check=True)
    print(f"\n[push 완료] {msg}")

# ──── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="DeepSeek 블로그 포스트 자동 생성기")
    parser.add_argument("--keyword", type=str,  help="단건 생성할 키워드")
    parser.add_argument("--kit",     type=str,  default="pdf",
                        choices=list(KIT_INFO.keys()), help="Kit 종류 (기본: pdf)")
    parser.add_argument("--batch",   type=int,  help="키워드 파일에서 N개 생성")
    parser.add_argument("--push",    action="store_true", help="생성 후 git push")
    args = parser.parse_args()

    generated = 0

    if args.keyword:
        print(f"\n[생성중] '{args.keyword}' ...")
        data = generate_post(args.keyword, args.kit)
        save_post(data, args.keyword, args.kit)
        generated = 1

    elif args.batch:
        with open(KEYWORDS_FILE, encoding="utf-8") as f:
            all_keywords: list = json.load(f)

        # kit 필터
        if args.kit:
            pool = [k for k in all_keywords if k.get("kit") == args.kit]
        else:
            pool = all_keywords

        # 이미 생성된 키워드는 제외 (keywords.json의 "done" 필드)
        pending = [k for k in pool if not k.get("done")]
        if not pending:
            print("모든 키워드가 이미 생성되었습니다.")
            return

        selected = random.sample(pending, min(args.batch, len(pending)))
        print(f"\n{len(selected)}개 포스트 생성 시작...\n")

        for item in selected:
            kw  = item["keyword"]
            kit = item.get("kit", args.kit)
            print(f"  → {kw} ({kit})")
            try:
                data = generate_post(kw, kit)
                save_post(data, kw, kit)
                # 생성 완료 표시
                item["done"] = True
                generated += 1
            except Exception as e:
                print(f"  [실패] {e}")

        # done 상태 저장
        with open(KEYWORDS_FILE, "w", encoding="utf-8") as f:
            json.dump(all_keywords, f, ensure_ascii=False, indent=2)

        print(f"\n{generated}개 완료")

    else:
        parser.print_help()
        return

    if args.push and generated > 0:
        git_push(generated)


if __name__ == "__main__":
    main()
