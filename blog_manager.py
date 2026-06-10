"""
blog_manager.py - 우아하우스 블로그 자동 포스팅 매니저 (GUI)
실행: python blog_manager.py
"""
import re
import json
import random
import threading
import datetime
import subprocess
from pathlib import Path

import requests
import customtkinter as ctk

# ──── 경로 ────────────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent
POSTS_DIR     = BASE_DIR / "_posts"
KEYWORDS_FILE = BASE_DIR / "keywords.json"
API_KEY_PATH  = Path(r"C:\개인\개인 프로젝트\blogwriter_new\blogger_seo_bot\config\deepseek_api_key.txt")

# ──── Kit 정보 ────────────────────────────────────────────────────────────────
KIT_INFO = {
    "전체":   None,
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

PROMPT_STYLES = [
    "초보자도 쉽게 따라할 수 있는 친절한 단계별 가이드 스타일",
    "실무자를 위한 핵심만 담은 간결한 실용 정보 스타일",
    "문제 상황 -> 원인 -> 해결책 순으로 전개하는 문제 해결 스타일",
    "실제 사용해본 것처럼 자연스럽게 쓴 경험 공유 스타일",
    "자주 겪는 실수와 해결법을 중심으로 한 노하우 공유 스타일",
    "장단점을 솔직하게 짚어주는 균형 잡힌 리뷰 스타일",
    "시간 절약과 업무 효율에 초점을 맞춘 생산성 팁 스타일",
    "직장인 학생의 일상 속 실제 활용 시나리오 중심 스타일",
    "왜 이 방법이 최선인지 논리적으로 설명하는 설득형 스타일",
    "비교 분석을 통해 이 도구의 강점을 드러내는 비교 스타일",
]

STRUCTURES = [
    "도입(공감) -> 도구 소개+URL -> 주요 기능 -> 활용 팁 -> 마무리+URL",
    "도입(문제 제시) -> 해결책으로 도구 소개+URL -> 사용법 단계별 -> 주의사항 -> 마무리+URL",
    "도입(시나리오) -> 도구 첫 소개+URL -> 기능 상세 -> 실제 사용 후기 -> 마무리+URL",
]

# ──── 핵심 함수 ───────────────────────────────────────────────────────────────

def get_api_key() -> str:
    return API_KEY_PATH.read_text(encoding="utf-8").strip()

def slugify(text: str) -> str:
    text = re.sub(r'[^\w\s가-힣]', '', text)
    text = re.sub(r'\s+', '-', text.strip())
    return text[:60].strip('-')

def generate_post(keyword: str, kit: str) -> dict:
    api_key = get_api_key()
    kit_entry = KIT_INFO.get(kit)
    if not kit_entry:
        kit_name, kit_url = "WooaHouse", "https://wooahouse.com"
    else:
        kit_name, kit_url = kit_entry

    style     = random.choice(PROMPT_STYLES)
    structure = random.choice(STRUCTURES)

    prompt = f"""당신은 SEO에 최적화된 한국어 블로그 글을 작성하는 전문 작가입니다.

[이번 글 정보]
타겟 키워드: {keyword}
소개할 도구: {kit_name} ({kit_url})
작성 스타일: {style}
글 구조: {structure}

[작성 조건]
- 제목: 타겟 키워드를 앞쪽에 포함, 30~60자, 이모지 금지
- 본문: 마크다운 형식, 1200~1800자, ## 소제목 사용
- URL은 글 구조 첫 소개 위치와 마무리 위치에 각 1회씩 총 2회 포함
- URL은 반드시 마크다운 링크 형식으로 작성: [WooaQR 무료 사용하기](https://qrkit.wooahouse.com) 처럼
- URL을 단독 줄에 텍스트만 쓰는 것 금지, 반드시 링크 문법 사용
- 메타 설명: 120~160자, 타겟 키워드 포함
- 태그: 5~8개 쉼표 구분

[출력 형식 - 반드시 이 형식만]
[TITLE]제목[/TITLE]
[DESC]메타 설명[/DESC]
[TAGS]태그1,태그2,태그3[/TAGS]
[BODY]
마크다운 본문
[/BODY]"""

    resp = requests.post(
        "https://api.deepseek.com/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": "deepseek-chat",
              "messages": [{"role": "user", "content": prompt}],
              "max_tokens": 3000, "temperature": 0.9},
        timeout=90,
    )
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"]

    title_m = re.search(r"\[TITLE\](.*?)\[/TITLE\]", raw, re.DOTALL)
    desc_m  = re.search(r"\[DESC\](.*?)\[/DESC\]",   raw, re.DOTALL)
    tags_m  = re.search(r"\[TAGS\](.*?)\[/TAGS\]",   raw, re.DOTALL)
    body_m  = re.search(r"\[BODY\](.*?)\[/BODY\]",   raw, re.DOTALL)

    if not all([title_m, desc_m, tags_m, body_m]):
        raise ValueError(f"응답 파싱 실패: {raw[:200]}")

    return {
        "title": title_m.group(1).strip(),
        "desc":  desc_m.group(1).strip(),
        "tags":  tags_m.group(1).strip(),
        "body":  body_m.group(1).strip(),
    }

def linkify_urls(text: str) -> str:
    """단독 줄에 있는 bare URL을 마크다운 링크로 변환"""
    return re.sub(
        r'(?<!\()(?<!\[)(https?://[^\s\)\]]+)(?!\))',
        lambda m: f'[{m.group(1)}]({m.group(1)})',
        text
    )

def save_post(data: dict, keyword: str, kit: str) -> str:
    today = datetime.date.today().isoformat()
    slug  = slugify(data["title"]) or slugify(keyword)
    filepath = POSTS_DIR / f"{today}-{slug}.md"

    counter = 1
    while filepath.exists():
        filepath = POSTS_DIR / f"{today}-{slug}-{counter}.md"
        counter += 1

    body = linkify_urls(data["body"])
    tags_yaml = "\n".join(f'  - "{t.strip()}"' for t in data["tags"].split(",") if t.strip())
    content = f"""---
layout: post
title: "{data['title'].replace('"', "'")}"
date: {today}
description: "{data['desc'].replace('"', "'")}"
categories:
  - "{kit}"
tags:
{tags_yaml}
kit: "{kit}"
---

{body}"""
    filepath.write_text(content, encoding="utf-8")
    return filepath.name

def git_push(count: int):
    msg = f"Add {count} blog posts {datetime.date.today()}"
    subprocess.run(["git", "-C", str(BASE_DIR), "add", "_posts/"], check=True)
    subprocess.run(["git", "-C", str(BASE_DIR), "commit", "-m", msg], check=True)
    subprocess.run(["git", "-C", str(BASE_DIR), "push"], check=True)

def get_balance() -> str:
    try:
        api_key = get_api_key()
        resp = requests.get("https://api.deepseek.com/user/balance",
                            headers={"Authorization": f"Bearer {api_key}"}, timeout=10)
        bal = resp.json()["balance_infos"][0]["total_balance"]
        return f"DeepSeek 잔액: ${bal}"
    except Exception:
        return "잔액: 확인 불가"

# ──── GUI ─────────────────────────────────────────────────────────────────────

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class BlogManager(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("우아하우스 블로그 매니저")
        self.geometry("660x740")
        self.resizable(False, False)

        self._running       = False
        self._schedule_timer = None

        self._build_ui()
        self._refresh_stats()

    # ──── UI 빌드 ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        # 타이틀
        ctk.CTkLabel(self, text="우아하우스 블로그 매니저",
                     font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(20, 2))
        ctk.CTkLabel(self, text="blog.wooahouse.com",
                     font=ctk.CTkFont(size=12), text_color="#10B981").pack(pady=(0, 14))

        # ── 기본 설정 ──
        cfg = ctk.CTkFrame(self)
        cfg.pack(fill="x", padx=24, pady=6)

        ctk.CTkLabel(cfg, text="기본 설정",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=16, pady=(12, 6))

        # Kit
        r1 = ctk.CTkFrame(cfg, fg_color="transparent")
        r1.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(r1, text="Kit 선택", width=110, anchor="w").pack(side="left")
        self.kit_var = ctk.StringVar(value="전체")
        ctk.CTkOptionMenu(r1, variable=self.kit_var,
                          values=list(KIT_INFO.keys()), width=180).pack(side="left", padx=8)

        # 생성 개수
        r2 = ctk.CTkFrame(cfg, fg_color="transparent")
        r2.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(r2, text="생성 개수", width=110, anchor="w").pack(side="left")
        self.count_var   = ctk.IntVar(value=10)
        self.count_label = ctk.CTkLabel(r2, text="10개", width=44, anchor="w")
        ctk.CTkSlider(r2, from_=1, to=20, variable=self.count_var,
                      number_of_steps=19, width=180,
                      command=lambda v: self.count_label.configure(
                          text=f"{int(v)}개")).pack(side="left", padx=8)
        self.count_label.pack(side="left")

        # Push 여부
        r3 = ctk.CTkFrame(cfg, fg_color="transparent")
        r3.pack(fill="x", padx=16, pady=(4, 14))
        ctk.CTkLabel(r3, text="GitHub Push", width=110, anchor="w").pack(side="left")
        self.push_var = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(r3, text="생성 후 자동 push", variable=self.push_var).pack(side="left", padx=8)

        # ── 자동 스케줄 ──
        sch = ctk.CTkFrame(self)
        sch.pack(fill="x", padx=24, pady=6)

        ctk.CTkLabel(sch, text="자동 스케줄",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=16, pady=(12, 6))

        r4 = ctk.CTkFrame(sch, fg_color="transparent")
        r4.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(r4, text="실행 간격", width=110, anchor="w").pack(side="left")
        self.interval_entry = ctk.CTkEntry(r4, width=70)
        self.interval_entry.insert(0, "60")
        self.interval_entry.pack(side="left", padx=8)
        ctk.CTkLabel(r4, text="분마다 자동 실행").pack(side="left")

        # 다음 실행 시간 표시
        r5 = ctk.CTkFrame(sch, fg_color="transparent")
        r5.pack(fill="x", padx=16, pady=(4, 14))
        ctk.CTkLabel(r5, text="", width=110).pack(side="left")
        self.next_run_label = ctk.CTkLabel(r5, text="스케줄 대기 중",
                                           text_color="#6B7280", font=ctk.CTkFont(size=12))
        self.next_run_label.pack(side="left", padx=8)

        # ── 버튼 ──
        btn = ctk.CTkFrame(self, fg_color="transparent")
        btn.pack(fill="x", padx=24, pady=10)

        self.run_btn = ctk.CTkButton(
            btn, text="지금 바로 실행",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=46, fg_color="#10B981", hover_color="#059669",
            command=self._on_run)
        self.run_btn.pack(side="left", expand=True, fill="x", padx=(0, 8))

        self.sch_btn = ctk.CTkButton(
            btn, text="자동 시작", height=46, width=120,
            command=self._toggle_schedule)
        self.sch_btn.pack(side="left")

        # ── 로그 ──
        log_frame = ctk.CTkFrame(self)
        log_frame.pack(fill="both", expand=True, padx=24, pady=(6, 0))

        ctk.CTkLabel(log_frame, text="실행 로그",
                     font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", padx=14, pady=(10, 4))

        self.log_box = ctk.CTkTextbox(log_frame, font=ctk.CTkFont(family="Consolas", size=12))
        self.log_box.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        # ── 상태바 ──
        stat = ctk.CTkFrame(self, height=38)
        stat.pack(fill="x", padx=24, pady=10)
        stat.pack_propagate(False)

        self.stats_label = ctk.CTkLabel(stat, text="남은 키워드: -",
                                        font=ctk.CTkFont(size=12))
        self.stats_label.pack(side="left", padx=14)

        self.balance_label = ctk.CTkLabel(stat, text="잔액 확인 중...",
                                          font=ctk.CTkFont(size=12), text_color="#10B981")
        self.balance_label.pack(side="right", padx=14)

    # ──── 로그 ────────────────────────────────────────────────────────────────

    def _log(self, msg: str):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_box.insert("end", f"[{now}] {msg}\n")
        self.log_box.see("end")

    # ──── 통계 갱신 ───────────────────────────────────────────────────────────

    def _refresh_stats(self):
        try:
            with open(KEYWORDS_FILE, encoding="utf-8") as f:
                kws = json.load(f)
            pending = sum(1 for k in kws if not k.get("done"))
            self.stats_label.configure(text=f"남은 키워드: {pending}개 / 전체 {len(kws)}개")
        except Exception:
            self.stats_label.configure(text="키워드 파일 오류")

        threading.Thread(target=self._fetch_balance, daemon=True).start()

    def _fetch_balance(self):
        text = get_balance()
        self.after(0, lambda: self.balance_label.configure(text=text))

    # ──── 즉시 실행 ───────────────────────────────────────────────────────────

    def _on_run(self):
        if self._running:
            self._log("이미 실행 중입니다.")
            return
        threading.Thread(target=self._run_generation, daemon=True).start()

    def _run_generation(self):
        self._running = True
        self.after(0, lambda: self.run_btn.configure(state="disabled", text="실행 중..."))

        kit_sel = self.kit_var.get()
        count   = int(self.count_var.get())
        do_push = self.push_var.get()

        self.after(0, lambda: self._log(f"=== 생성 시작: {count}개 | Kit: {kit_sel} ==="))

        try:
            with open(KEYWORDS_FILE, encoding="utf-8") as f:
                all_kws = json.load(f)

            if kit_sel == "전체":
                pool = [k for k in all_kws if not k.get("done")]
            else:
                pool = [k for k in all_kws if k.get("kit") == kit_sel and not k.get("done")]

            if not pool:
                self.after(0, lambda: self._log("남은 키워드가 없습니다."))
                return

            selected  = random.sample(pool, min(count, len(pool)))
            generated = 0

            for item in selected:
                kw  = item["keyword"]
                kit = item.get("kit", "pdf")
                self.after(0, lambda k=kw: self._log(f"생성중: {k}"))
                try:
                    data  = generate_post(kw, kit)
                    fname = save_post(data, kw, kit)
                    item["done"] = True
                    generated += 1
                    self.after(0, lambda n=fname: self._log(f"저장: {n}"))
                except Exception as e:
                    err = str(e)[:80]
                    self.after(0, lambda m=err: self._log(f"[실패] {m}"))

            with open(KEYWORDS_FILE, "w", encoding="utf-8") as f:
                json.dump(all_kws, f, ensure_ascii=False, indent=2)

            self.after(0, lambda: self._log(f"=== 완료: {generated}개 생성 ==="))

            if do_push and generated > 0:
                self.after(0, lambda: self._log("GitHub push 중..."))
                try:
                    git_push(generated)
                    self.after(0, lambda: self._log("push 완료!"))
                except Exception as e:
                    self.after(0, lambda: self._log(f"push 실패: {e}"))

        except Exception as e:
            self.after(0, lambda: self._log(f"오류: {e}"))
        finally:
            self._running = False
            self.after(0, lambda: self.run_btn.configure(state="normal", text="지금 바로 실행"))
            self.after(0, self._refresh_stats)

    # ──── 자동 스케줄 ─────────────────────────────────────────────────────────

    def _toggle_schedule(self):
        if self._schedule_timer:
            self._stop_schedule()
        else:
            self._start_schedule()

    def _start_schedule(self):
        try:
            interval_min = int(self.interval_entry.get())
            if interval_min < 1:
                raise ValueError
        except ValueError:
            self._log("간격을 1 이상의 숫자(분)로 입력하세요.")
            return

        self._log(f"자동 스케줄 시작: {interval_min}분마다 실행")
        self.sch_btn.configure(text="자동 중지", fg_color="#EF4444", hover_color="#DC2626")
        self._schedule_tick(interval_min * 60 * 1000)

    def _schedule_tick(self, ms: int):
        self._on_run()
        next_time = (datetime.datetime.now() + datetime.timedelta(milliseconds=ms)).strftime("%H:%M")
        self.after(0, lambda: self.next_run_label.configure(
            text=f"다음 실행: {next_time}", text_color="#10B981"))
        self._schedule_timer = self.after(ms, lambda: self._schedule_tick(ms))

    def _stop_schedule(self):
        if self._schedule_timer:
            self.after_cancel(self._schedule_timer)
            self._schedule_timer = None
        self._log("자동 스케줄 중지")
        self.sch_btn.configure(text="자동 시작",
                               fg_color=["#2CC985", "#2FA572"],
                               hover_color=["#0D9B6C", "#106A43"])
        self.next_run_label.configure(text="스케줄 대기 중", text_color="#6B7280")

    def on_close(self):
        if self._schedule_timer:
            self.after_cancel(self._schedule_timer)
        self.destroy()


if __name__ == "__main__":
    app = BlogManager()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
