import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import os

# ========================= 모듈 A =========================
class ModuleAFrame(tk.Frame):
    def __init__(self, parent, root):
        super().__init__(parent, bg='#1e1e1e')
        self.root = root
        self.parent = parent
        self.data_file = "malla_data.json"

        self.current_input = "0"
        self.first_operand = None
        self.operator = None
        self.waiting_for_second = False
        self.reset_next_input = False

        self.sw_running = False
        self.sw_time = 0.0
        self.sw_laps = []
        self.sw_after_id = None

        self.timers = [
            {"remaining": 0, "running": False, "after_id": None},
            {"remaining": 0, "running": False, "after_id": None},
            {"remaining": 0, "running": False, "after_id": None}
        ]

        self.setup_ui()
        self.load_state()
        self.update_display()

        self.root.bind('<Key>', self.on_key_press)
        self.display_entry.focus_set()

    def setup_ui(self):
        self.build_stopwatch_section()
        self.build_timer_section()
        self.build_history_section()

        self.display_var = tk.StringVar()
        self.display_var.set("0")
        self.display_entry = tk.Entry(
            self, textvariable=self.display_var,
            font=('Consolas', 36, 'bold'),
            justify='right',
            state='readonly',
            readonlybackground='#1e1e1e',
            fg='white',
            relief='flat',
            highlightthickness=0
        )
        self.display_entry.pack(fill='x', pady=(10, 5))

        button_frame = tk.Frame(self, bg='#1e1e1e')
        button_frame.pack(fill='x', pady=(0, 10))

        clear_history_btn = tk.Button(
            button_frame,
            text="🗑 기록 지우기",
            font=('Consolas', 10, 'bold'),
            bg='#3a3a3a',
            fg='white',
            activebackground='#555555',
            relief='flat',
            padx=10,
            pady=5,
            command=self.clear_history
        )
        clear_history_btn.pack(side='left')

        clear_btn = tk.Button(
            button_frame,
            text="C",
            font=('Consolas', 12, 'bold'),
            bg='#3a3a3a',
            fg='white',
            activebackground='#555555',
            relief='flat',
            padx=15,
            pady=5,
            command=self.input_clear
        )
        clear_btn.pack(side='right')

    def build_stopwatch_section(self):
        frame = tk.Frame(self, bg='#1e1e1e')
        frame.pack(fill='both', expand=True, pady=5)

        label = tk.Label(frame, text="⏱️ 스톱워치", font=('Consolas', 10, 'bold'),
                         bg='#1e1e1e', fg='#a0a0a0')
        label.pack(anchor='w')

        self.sw_display = tk.Label(frame, text="00:00:00.00",
                                   font=('Consolas', 24, 'bold'),
                                   bg='#1e1e1e', fg='white')
        self.sw_display.pack(pady=5)

        btn_frame = tk.Frame(frame, bg='#1e1e1e')
        btn_frame.pack()

        self.sw_start_btn = tk.Button(btn_frame, text="시작", font=('Consolas', 10),
                                      bg='#3a3a3a', fg='white', relief='flat',
                                      padx=10, command=self.sw_start)
        self.sw_start_btn.pack(side='left', padx=5)

        self.sw_lap_btn = tk.Button(btn_frame, text="기록", font=('Consolas', 10),
                                    bg='#3a3a3a', fg='white', relief='flat',
                                    padx=10, command=self.sw_lap, state='disabled')
        self.sw_lap_btn.pack(side='left', padx=5)

        self.sw_reset_btn = tk.Button(btn_frame, text="초기화", font=('Consolas', 10),
                                      bg='#3a3a3a', fg='white', relief='flat',
                                      padx=10, command=self.sw_reset)
        self.sw_reset_btn.pack(side='left', padx=5)

        self.sw_lap_list = scrolledtext.ScrolledText(
            frame, height=6, state='disabled',
            font=('Consolas', 8),
            bg='#2d2d2d', fg='#a0a0a0',
            borderwidth=0,
            relief='flat'
        )
        self.sw_lap_list.pack(fill='both', expand=True, pady=(5,0))

    def build_timer_section(self):
        frame = tk.Frame(self, bg='#1e1e1e')
        frame.pack(fill='x', pady=5)

        label = tk.Label(frame, text="⏲️ 타이머 (3개)", font=('Consolas', 10, 'bold'),
                         bg='#1e1e1e', fg='#a0a0a0')
        label.pack(anchor='w')

        self.timer_frames = []
        for i in range(3):
            tf = tk.Frame(frame, bg='#1e1e1e')
            tf.pack(fill='x', pady=2)

            name_entry = tk.Entry(tf, font=('Consolas', 9), width=8,
                                  bg='#2d2d2d', fg='white', relief='flat',
                                  insertbackground='white')
            name_entry.insert(0, f"T{i+1}")
            name_entry.pack(side='left', padx=2)

            time_lbl = tk.Label(tf, text="00:00:00", font=('Consolas', 14, 'bold'),
                                bg='#1e1e1e', fg='white', width=10)
            time_lbl.pack(side='left', padx=5)

            entry = tk.Entry(tf, font=('Consolas', 10), width=10,
                             bg='#2d2d2d', fg='white', relief='flat',
                             insertbackground='white')
            entry.insert(0, "00:00:00")
            entry.pack(side='left', padx=5)

            start_btn = tk.Button(tf, text="시작", font=('Consolas', 8),
                                  bg='#3a3a3a', fg='white', relief='flat',
                                  padx=5, command=lambda idx=i: self.timer_start(idx))
            start_btn.pack(side='left', padx=2)

            reset_btn = tk.Button(tf, text="초기화", font=('Consolas', 8),
                                  bg='#3a3a3a', fg='white', relief='flat',
                                  padx=5, command=lambda idx=i: self.timer_reset(idx))
            reset_btn.pack(side='left', padx=2)

            self.timer_frames.append({
                'name_entry': name_entry,
                'time_label': time_lbl,
                'entry': entry,
                'start_btn': start_btn,
                'reset_btn': reset_btn
            })

    def build_history_section(self):
        frame = tk.Frame(self, bg='#1e1e1e')
        frame.pack(fill='both', expand=True, pady=5)

        label = tk.Label(frame, text="📝 계산 기록", font=('Consolas', 10, 'bold'),
                         bg='#1e1e1e', fg='#a0a0a0')
        label.pack(anchor='w')

        self.history_text = scrolledtext.ScrolledText(
            frame, height=4, state='disabled',
            font=('Consolas', 9),
            bg='#2d2d2d', fg='#a0a0a0',
            borderwidth=0,
            relief='flat'
        )
        self.history_text.pack(fill='both', expand=True)

    # ----- 계산기 기능 -----
    def on_key_press(self, event):
        key = event.char
        keysym = event.keysym
    
        # 현재 포커스가 있는 위젯 확인
        focused_widget = self.root.focus_get()
    
        # 1. 계산기 입력 필드에 포커스가 있으면 → 기존 로직 실행
        if focused_widget == self.display_entry:
            self._process_calculator_key(key, keysym)
            return
    
        # 2. 타이머 입력 필드(이름 or 설정 시간)에 포커스가 있으면 → 아무것도 하지 않음 (해당 위젯이 처리)
        for timer_frame in self.timer_frames:
            if focused_widget in (timer_frame['name_entry'], timer_frame['entry']):
                return
    
        # 3. 그 외의 경우 (기록 필드, 빈 공간 등)
        #    숫자나 소수점이면 계산기 입력 필드로 포커스 이동 후 입력
        if key.isdigit() or key == '.':
            self.display_entry.focus_set()
            self.input_digit(key)
            self.update_display()
            self.display_entry.focus_set()  # 다시 포커스 유지
    
    def _process_calculator_key(self, key, keysym):
        """계산기 입력 필드에 포커스가 있을 때의 키 처리 (기존 로직)"""
        if key.isdigit() or key == '.':
            self.input_digit(key)
        elif key in ('+', '*', '/'):
            self.input_operator(key)
        elif key == '-':
            if self.current_input == "0" and self.first_operand is None and self.operator is None:
                self.current_input = "-"
            else:
                self.input_operator(key)
        elif key == '%':
            self.input_percent()
        elif keysym == 'BackSpace':
            self.input_backspace()
        elif keysym == 'Escape' or key.lower() == 'c':
            self.input_clear()
        elif keysym == 'Return' or key == '=':
            self.input_equals()
    
        self.update_display()
        self.display_entry.focus_set()

    def format_with_commas(self, value_str):
        if value_str in ("오류", ""):
            return value_str
        sign = ''
        if value_str.startswith('-'):
            sign = '-'
            value_str = value_str[1:]
        if '.' in value_str:
            int_part, dec_part = value_str.split('.')
        else:
            int_part, dec_part = value_str, ''
        if int_part:
            int_part = format(int(int_part), ',')
        else:
            int_part = '0'
        if dec_part:
            return f"{sign}{int_part}.{dec_part}"
        else:
            return f"{sign}{int_part}"

    def format_num(self, num):
        if isinstance(num, float):
            if num.is_integer():
                return self.format_with_commas(str(int(num)))
            else:
                return self.format_with_commas(str(round(num, 10)))
        return self.format_with_commas(str(num))

    def input_digit(self, digit):
        if self.reset_next_input:
            self.current_input = ""
            self.reset_next_input = False
        if self.waiting_for_second:
            self.current_input = "0"
            self.waiting_for_second = False
        if self.current_input == "0" and digit != '.':
            self.current_input = digit
        else:
            if digit == '.' and '.' in self.current_input:
                return
            self.current_input += digit

    def input_operator(self, op):
        self.reset_next_input = False
        if self.first_operand is not None and self.operator is not None and not self.waiting_for_second:
            self.input_equals()
        try:
            self.first_operand = float(self.current_input)
        except ValueError:
            self.first_operand = 0.0
        self.operator = op
        self.waiting_for_second = True

    def input_percent(self):
        self.reset_next_input = False
        if self.first_operand is None:
            try:
                val = float(self.current_input) / 100.0
                self.current_input = str(val)
            except:
                pass
        else:
            try:
                val = float(self.current_input)
                percent = self.first_operand * (val / 100.0)
                self.current_input = str(percent)
            except:
                pass
        self.waiting_for_second = False

    def input_backspace(self):
        if len(self.current_input) > 1:
            self.current_input = self.current_input[:-1]
        else:
            self.current_input = "0"

    def input_clear(self):
        self.current_input = "0"
        self.first_operand = None
        self.operator = None
        self.waiting_for_second = False
        self.reset_next_input = False
        self.update_display()

    def input_equals(self):
        if self.first_operand is None or self.operator is None:
            return
        try:
            second = float(self.current_input)
        except ValueError:
            return
        op = self.operator
        if op == '+':
            result = self.first_operand + second
        elif op == '-':
            result = self.first_operand - second
        elif op == '*':
            result = self.first_operand * second
        elif op == '/':
            if second == 0:
                result = "오류"
            else:
                result = self.first_operand / second
        else:
            return
        history_entry = (f"{self.format_num(self.first_operand)} {op} "
                         f"{self.format_num(second)} = {self.format_num(result)}")
        self.add_history(history_entry)
        if isinstance(result, str):
            self.current_input = result
        else:
            self.current_input = str(result)
        self.reset_next_input = True
        self.first_operand = None
        self.operator = None
        self.waiting_for_second = False

    def add_history(self, text):
        self.history_text.config(state='normal')
        self.history_text.insert(tk.END, text + "\n")
        self.history_text.see(tk.END)
        self.history_text.config(state='disabled')

    def clear_history(self):
        self.history_text.config(state='normal')
        self.history_text.delete(1.0, tk.END)
        self.history_text.config(state='disabled')

    def update_display(self):
        display_text = self.format_with_commas(self.current_input)
        if len(display_text) > 30:
            display_text = display_text[:30] + "…"
        self.display_var.set(display_text)

    # ----- 스톱워치 기능 -----
    def sw_start(self):
        if not self.sw_running:
            self.sw_running = True
            self.sw_start_btn.config(text="일시정지")
            self.sw_lap_btn.config(state='normal')
            self.sw_update()
        else:
            self.sw_running = False
            self.sw_start_btn.config(text="계속")
            if self.sw_after_id:
                self.root.after_cancel(self.sw_after_id)
                self.sw_after_id = None

    def sw_update(self):
        if self.sw_running:
            self.sw_time += 0.01
            self.sw_display.config(text=self.sw_format_time(self.sw_time))
            self.sw_after_id = self.root.after(10, self.sw_update)

    def sw_lap(self):
        if self.sw_running:
            self.sw_laps.append(self.sw_time)
            self.sw_update_lap_list()

    def sw_reset(self):
        self.sw_running = False
        if self.sw_after_id:
            self.root.after_cancel(self.sw_after_id)
            self.sw_after_id = None
        self.sw_time = 0.0
        self.sw_laps = []
        self.sw_display.config(text="00:00:00.00")
        self.sw_start_btn.config(text="시작")
        self.sw_lap_btn.config(state='disabled')
        self.sw_update_lap_list()

    def sw_update_lap_list(self):
        self.sw_lap_list.config(state='normal')
        self.sw_lap_list.delete(1.0, tk.END)

        if self.sw_laps:
            self.sw_lap_list.insert(tk.END, f"{'순번':<6} {'구간 시간':<14} {'누적 시간':<14}\n")
            self.sw_lap_list.insert(tk.END, "-" * 36 + "\n")

            lap_intervals = []
            prev = 0.0
            for lap in self.sw_laps:
                lap_intervals.append(lap - prev)
                prev = lap

            min_interval = min(lap_intervals) if lap_intervals else 0
            max_interval = max(lap_intervals) if lap_intervals else 0

            for i, (interval, cumulative) in enumerate(zip(lap_intervals, self.sw_laps), 1):
                tag = ""
                if interval == min_interval and len(lap_intervals) > 1:
                    tag = " ★ (가장 빠름)"
                elif interval == max_interval and min_interval != max_interval:
                    tag = " ★ (가장 느림)"
                self.sw_lap_list.insert(tk.END,
                    f"{i:<6} {self.sw_format_time(interval):<14} {self.sw_format_time(cumulative):<14}{tag}\n")

        self.sw_lap_list.config(state='disabled')

    def sw_format_time(self, seconds):
        if seconds < 0:
            seconds = 0
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        cent = int((seconds - int(seconds)) * 100)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}.{cent:02d}"

    # ----- 타이머 기능 -----
    def timer_start(self, idx):
        timer = self.timers[idx]
        if not timer["running"]:
            if timer["remaining"] == 0:
                entry = self.timer_frames[idx]['entry']
                time_str = entry.get().strip()
                try:
                    parts = time_str.split(':')
                    if len(parts) == 3:
                        h, m, s = map(int, parts)
                        if h < 0 or m < 0 or s < 0 or h > 23 or m > 59 or s > 59:
                            raise ValueError
                        total_seconds = h * 3600 + m * 60 + s
                    elif len(parts) == 2:
                        m, s = map(int, parts)
                        if m < 0 or s < 0 or m > 59 or s > 59:
                            raise ValueError
                        total_seconds = m * 60 + s
                    else:
                        total_seconds = int(time_str)
                    if total_seconds <= 0:
                        raise ValueError
                    timer["remaining"] = total_seconds
                except:
                    messagebox.showerror("오류", "올바른 시간을 입력하세요 (예: 01:30:00 또는 90)")
                    return

            timer["running"] = True
            self.timer_frames[idx]['start_btn'].config(text="일시정지")
            self.timer_frames[idx]['entry'].config(state='disabled')
            self.timer_update(idx)
        else:
            timer["running"] = False
            if timer["after_id"]:
                self.root.after_cancel(timer["after_id"])
                timer["after_id"] = None
            self.timer_frames[idx]['start_btn'].config(text="계속")

    def timer_update(self, idx):
        timer = self.timers[idx]
        if timer["running"] and timer["remaining"] > 0:
            timer["remaining"] -= 1
            h = int(timer["remaining"] // 3600)
            m = int((timer["remaining"] % 3600) // 60)
            s = int(timer["remaining"] % 60)
            self.timer_frames[idx]['time_label'].config(text=f"{h:02d}:{m:02d}:{s:02d}")

            if timer["remaining"] <= 0:
                timer["running"] = False
                self.timer_frames[idx]['start_btn'].config(text="시작")
                self.timer_frames[idx]['entry'].config(state='normal')
                name = self.timer_frames[idx]['name_entry'].get()
                messagebox.showinfo("타이머 알람", f"'{name}' 타이머 시간이 되었습니다!")
                import winsound
                winsound.Beep(1000, 500)
            else:
                timer["after_id"] = self.root.after(1000, lambda: self.timer_update(idx))
        elif timer["running"] and timer["remaining"] == 0:
            timer["running"] = False
            self.timer_frames[idx]['start_btn'].config(text="시작")
            self.timer_frames[idx]['entry'].config(state='normal')

    def timer_reset(self, idx):
        timer = self.timers[idx]
        if timer["running"]:
            timer["running"] = False
            if timer["after_id"]:
                self.root.after_cancel(timer["after_id"])
                timer["after_id"] = None
        timer["remaining"] = 0
        self.timer_frames[idx]['time_label'].config(text="00:00:00")
        self.timer_frames[idx]['start_btn'].config(text="시작")
        self.timer_frames[idx]['entry'].config(state='normal')
        self.timer_frames[idx]['entry'].delete(0, tk.END)
        self.timer_frames[idx]['entry'].insert(0, "00:00:00")

    # ----- 저장 / 불러오기 -----
    def save_state(self):
        try:
            history_text = self.history_text.get(1.0, tk.END).strip()

            timers_data = []
            for i, timer in enumerate(self.timers):
                timers_data.append({
                    "name": self.timer_frames[i]['name_entry'].get(),
                    "remaining": timer["remaining"],
                    "set_time": self.timer_frames[i]['entry'].get()
                })

            data = {
                "history": history_text,
                "sw_laps": self.sw_laps,
                "timers": timers_data
            }

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"저장 오류: {e}")

    def load_state(self):
        """malla_data.json에서 데이터를 불러와 복원"""
        if not os.path.exists(self.data_file):
            return
    
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
    
            # 1. 계산 기록 복원
            if "history" in data and data["history"]:
                self.history_text.config(state='normal')
                self.history_text.delete(1.0, tk.END)
                
                # ★ 마지막에 개행이 없으면 추가 (이어붙이기 방지)
                history = data["history"]
                if history and not history.endswith('\n'):
                    history += '\n'
                self.history_text.insert(tk.END, history)
                self.history_text.config(state='disabled')
    
            # 2. 스톱워치 랩 기록 복원
            if "sw_laps" in data and data["sw_laps"]:
                self.sw_laps = data["sw_laps"]
                self.sw_update_lap_list()
    
            # 3. 타이머 데이터 복원
            if "timers" in data and data["timers"]:
                for i, timer_data in enumerate(data["timers"]):
                    if i >= 3:
                        break
                    self.timer_frames[i]['name_entry'].delete(0, tk.END)
                    self.timer_frames[i]['name_entry'].insert(0, timer_data.get("name", f"T{i+1}"))
    
                    set_time = timer_data.get("set_time", "00:00:00")
                    self.timer_frames[i]['entry'].delete(0, tk.END)
                    self.timer_frames[i]['entry'].insert(0, set_time)
    
                    remaining = timer_data.get("remaining", 0)
                    self.timers[i]["remaining"] = remaining
                    self.timers[i]["running"] = False
    
                    h = int(remaining // 3600)
                    m = int((remaining % 3600) // 60)
                    s = int(remaining % 60)
                    self.timer_frames[i]['time_label'].config(text=f"{h:02d}:{m:02d}:{s:02d}")
    
                    self.timer_frames[i]['start_btn'].config(text="시작")
                    self.timer_frames[i]['entry'].config(state='normal')
    
        except Exception as e:
            print(f"불러오기 오류: {e}")


# ========================= 채팅 매크로 (저장/불러오기 버튼 제거) =========================
class MacroFrame(tk.Frame):
    def __init__(self, parent, root):
        super().__init__(parent, bg='#1e1e1e')
        self.root = root
        self.parent = parent

        self.macros = []
        self.macro_file = "macros.json"

        self.setup_ui()
        self.load_macros()

    def setup_ui(self):
        label = tk.Label(self, text="💬 채팅 매크로", font=('Consolas', 12, 'bold'),
                         bg='#1e1e1e', fg='#a0a0a0')
        label.pack(anchor='w', pady=(0, 10))

        list_frame = tk.Frame(self, bg='#1e1e1e')
        list_frame.pack(fill='both', expand=True, pady=5)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')

        self.macro_listbox = tk.Listbox(
            list_frame, height=10,
            bg='#2d2d2d', fg='white',
            selectmode=tk.SINGLE,
            relief='flat',
            yscrollcommand=scrollbar.set
        )
        self.macro_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.macro_listbox.yview)

        self.macro_listbox.bind('<Double-Button-1>', self.copy_selected_macro)

        entry_frame = tk.Frame(self, bg='#1e1e1e')
        entry_frame.pack(fill='x', pady=5)

        self.macro_entry = tk.Entry(
            entry_frame,
            font=('Consolas', 10),
            bg='#2d2d2d', fg='white',
            relief='flat',
            insertbackground='white'
        )
        self.macro_entry.pack(side='left', fill='x', expand=True, padx=(0, 5))
        self.macro_entry.bind('<Return>', lambda e: self.add_macro())

        add_btn = tk.Button(
            entry_frame,
            text="추가",
            font=('Consolas', 9, 'bold'),
            bg='#3a3a3a', fg='white',
            activebackground='#555555',
            relief='flat',
            padx=10,
            command=self.add_macro
        )
        add_btn.pack(side='left', padx=2)

        delete_btn = tk.Button(
            entry_frame,
            text="삭제",
            font=('Consolas', 9, 'bold'),
            bg='#3a3a3a', fg='white',
            activebackground='#555555',
            relief='flat',
            padx=10,
            command=self.delete_selected_macro
        )
        delete_btn.pack(side='left', padx=2)

        # ★ 저장/불러오기 버튼 제거됨

        info_label = tk.Label(
            self,
            text="📌 더블클릭: 클립보드에 복사 (팝업 없이 조용히 복사됨)",
            font=('Consolas', 8),
            bg='#1e1e1e', fg='#666666'
        )
        info_label.pack(anchor='w', pady=(10, 0))

    def add_macro(self):
        text = self.macro_entry.get().strip()
        if not text:
            messagebox.showwarning("경고", "메시지를 입력하세요.")
            return
        if text in self.macros:
            messagebox.showwarning("경고", "이미 존재하는 메시지입니다.")
            return
        self.macros.append(text)
        self.macro_listbox.insert(tk.END, text)
        self.macro_entry.delete(0, tk.END)
        self.save_macros()

    def delete_selected_macro(self):
        selection = self.macro_listbox.curselection()
        if not selection:
            messagebox.showwarning("경고", "삭제할 항목을 선택하세요.")
            return
        idx = selection[0]
        self.macro_listbox.delete(idx)
        del self.macros[idx]
        self.save_macros()

    def copy_selected_macro(self, event=None):
        selection = self.macro_listbox.curselection()
        if not selection:
            return
        idx = selection[0]
        text = self.macros[idx]

        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()

    def save_macros(self):
        try:
            with open(self.macro_file, 'w', encoding='utf-8') as f:
                json.dump(self.macros, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("오류", f"저장 실패: {e}")

    def load_macros(self):
        if not os.path.exists(self.macro_file):
            return
        try:
            with open(self.macro_file, 'r', encoding='utf-8') as f:
                self.macros = json.load(f)
            self.macro_listbox.delete(0, tk.END)
            for item in self.macros:
                self.macro_listbox.insert(tk.END, item)
        except Exception as e:
            messagebox.showerror("오류", f"불러오기 실패: {e}")


# ========================= 메인 앱 =========================
class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Malla")  # ★ 간단하게 "Malla"로 변경
        self.root.geometry("520x800")
        self.root.configure(bg='#1e1e1e')
        self.root.resizable(False, False)

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.module_a_frame = ModuleAFrame(self.notebook, root)
        self.notebook.add(self.module_a_frame, text="🧮 모듈 A")

        self.macro_frame = MacroFrame(self.notebook, root)
        self.notebook.add(self.macro_frame, text="💬 매크로")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.module_a_frame.save_state()
        self.macro_frame.save_macros()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
