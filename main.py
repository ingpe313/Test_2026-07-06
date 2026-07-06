import tkinter as tk
from tkinter import messagebox, Toplevel, Listbox, Scrollbar
import re

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("사칙연산 계산기 v2.8")
        self.root.geometry("350x550")
        self.root.resizable(False, False)
        self.root.configure(bg='#2c2c2c')
        
        # 계산기 상태 변수
        self.current_input = ""      # 현재 입력 중인 숫자 (실제 값)
        self.display_text = ""       # 디스플레이에 표시할 텍스트 (콤마 포함)
        self.previous_input = ""     # 이전에 입력한 숫자
        self.operator = ""           # 현재 선택된 연산자
        self.result_shown = False    # 결과가 표시된 상태인지
        self.just_entered_operator = False  # 방금 연산자 입력했는지
        self.history = []            # 계산 기록 저장 (최대 50개)
        self.history_window = None   # 히스토리 창 참조
        
        # ===== 상단 메뉴 영역 (히스토리 버튼) =====
        top_frame = tk.Frame(root, bg='#2c2c2c', height=40)
        top_frame.pack(fill='x', padx=10, pady=(5, 0))
        top_frame.pack_propagate(False)
        
        # 시계 모양 히스토리 버튼 (우측 정렬)
        self.history_btn = tk.Button(top_frame, text="🕐", font=("Arial", 18),
                                    bg='#2c2c2c', fg='white', bd=0, relief='flat',
                                    command=self.show_history, cursor='hand2')
        self.history_btn.pack(side='right')
        
        # ===== 디스플레이 (Label) =====
        self.display = tk.Label(root, font=("Arial", 32), bg='white', fg='black',
                               justify='right', anchor='e', relief='sunken', bd=10)
        self.display.pack(fill='both', padx=10, pady=10, ipady=15)
        self.display_text = "0"
        self.display.config(text="0")
        
        # ===== 키보드 이벤트 바인딩 =====
        self.root.focus_set()
        self.root.bind('<Key>', self.on_key_press)
        self.root.bind('<Button-1>', self.on_click)
        
        # ===== 버튼 프레임 =====
        btn_frame = tk.Frame(root, bg='#2c2c2c')
        btn_frame.pack(padx=10, pady=5)
        
        # 버튼 스타일
        btn_style = {'width': 6, 'height': 2, 'font': ("Arial", 14, "bold"), 'relief': 'flat'}
        
        # 1행: MC, MR, M+, M-
        memory_btns = ['MC', 'MR', 'M+', 'M-']
        for i, text in enumerate(memory_btns):
            btn = tk.Button(btn_frame, text=text, bg='#3d3d3d', fg='white', **btn_style,
                          command=lambda t=text: self.memory_action(t))
            btn.grid(row=0, column=i, padx=2, pady=2, sticky='nsew')
        
        # 2행: %, CE, C, ÷
        row1_btns = ['%', 'CE', 'C', '÷']
        for i, text in enumerate(row1_btns):
            if text == '÷':
                btn = tk.Button(btn_frame, text=text, bg='#f9a825', fg='white', **btn_style,
                              command=lambda: self.add_operator('÷'))
            else:
                btn = tk.Button(btn_frame, text=text, bg='#3d3d3d', fg='white', **btn_style,
                              command=lambda t=text: self.function_action(t))
            btn.grid(row=1, column=i, padx=2, pady=2, sticky='nsew')
        
        # 3행: 7, 8, 9, ×
        row2_btns = ['7', '8', '9', '×']
        for i, text in enumerate(row2_btns):
            if text == '×':
                btn = tk.Button(btn_frame, text=text, bg='#f9a825', fg='white', **btn_style,
                              command=lambda: self.add_operator('×'))
            else:
                btn = tk.Button(btn_frame, text=text, bg='#4a4a4a', fg='white', **btn_style,
                              command=lambda t=text: self.add_number(t))
            btn.grid(row=2, column=i, padx=2, pady=2, sticky='nsew')
        
        # 4행: 4, 5, 6, −
        row3_btns = ['4', '5', '6', '−']
        for i, text in enumerate(row3_btns):
            if text == '−':
                btn = tk.Button(btn_frame, text=text, bg='#f9a825', fg='white', **btn_style,
                              command=lambda: self.add_operator('−'))
            else:
                btn = tk.Button(btn_frame, text=text, bg='#4a4a4a', fg='white', **btn_style,
                              command=lambda t=text: self.add_number(t))
            btn.grid(row=3, column=i, padx=2, pady=2, sticky='nsew')
        
        # 5행: 1, 2, 3, +
        row4_btns = ['1', '2', '3', '+']
        for i, text in enumerate(row4_btns):
            if text == '+':
                btn = tk.Button(btn_frame, text=text, bg='#f9a825', fg='white', **btn_style,
                              command=lambda: self.add_operator('+'))
            else:
                btn = tk.Button(btn_frame, text=text, bg='#4a4a4a', fg='white', **btn_style,
                              command=lambda t=text: self.add_number(t))
            btn.grid(row=4, column=i, padx=2, pady=2, sticky='nsew')
        
        # 6행: +/−, 0, ., =
        row5_btns = ['+/−', '0', '.', '=']
        for i, text in enumerate(row5_btns):
            if text == '=':
                btn = tk.Button(btn_frame, text=text, bg='#f9a825', fg='white', **btn_style,
                              command=self.calculate)
            elif text == '+/−':
                btn = tk.Button(btn_frame, text=text, bg='#4a4a4a', fg='white', **btn_style,
                              command=self.toggle_sign)
            elif text == '.':
                btn = tk.Button(btn_frame, text=text, bg='#4a4a4a', fg='white', **btn_style,
                              command=self.add_decimal)
            else:
                btn = tk.Button(btn_frame, text=text, bg='#4a4a4a', fg='white', **btn_style,
                              command=lambda t=text: self.add_number(t))
            btn.grid(row=5, column=i, padx=2, pady=2, sticky='nsew')
        
        # 그리드 가중치 설정
        for i in range(6):
            btn_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            btn_frame.grid_columnconfigure(i, weight=1)
        
        # 모든 버튼이 포커스를 받지 않도록 설정
        for child in btn_frame.winfo_children():
            child.config(takefocus=0)
    
    def on_click(self, event):
        """클릭 시 포커스를 루트로 유지"""
        self.root.focus_set()
    
    def format_number(self, num_str):
        """숫자 문자열에 천 단위 콤마 추가"""
        if not num_str:
            return "0"
        
        is_negative = num_str.startswith('-')
        if is_negative:
            num_str = num_str[1:]
        
        if '.' in num_str:
            integer_part, decimal_part = num_str.split('.')
            formatted_int = f"{int(integer_part):,}" if integer_part else "0"
            return f"-{formatted_int}.{decimal_part}" if is_negative else f"{formatted_int}.{decimal_part}"
        else:
            formatted = f"{int(num_str):,}" if num_str else "0"
            return f"-{formatted}" if is_negative else formatted
    
    def update_display(self, value):
        """디스플레이 업데이트 (콤마 포함)"""
        self.display_text = value
        self.display.config(text=self.format_number(value))
    
    def get_display_value(self):
        """디스플레이에서 실제 숫자값 가져오기 (콤마 제거)"""
        return self.display_text
    
    def on_key_press(self, event):
        """키보드 입력 처리"""
        # Enter 키 처리 (최우선)
        if event.keysym == 'Return' or event.keysym == 'KP_Enter':
            self.calculate()
            return
        
        # 특수 키 무시
        if event.keysym in ['Shift_L', 'Shift_R', 'Control_L', 'Control_R', 
                           'Alt_L', 'Alt_R', 'Tab', 'Caps_Lock', 'Escape',
                           'Up', 'Down', 'Left', 'Right', 'Home', 'End',
                           'Page_Up', 'Page_Down', 'Insert', 'Delete']:
            return
        
        # H 키 - 히스토리
        if event.keysym == 'h' or event.keysym == 'H':
            self.show_history()
            return
        
        # 숫자 키
        if event.char and event.char.isdigit():
            self.add_number(event.char)
            return
        
        # 소수점
        if event.char == '.':
            self.add_decimal()
            return
        
        # 연산자 처리
        if event.char == '+':
            self.add_operator('+')
            return
        if event.char == '-':
            self.add_operator('−')
            return
        if event.char == '*':
            self.add_operator('×')
            return
        if event.char == '/':
            self.add_operator('÷')
            return
        
        # Backspace
        if event.keysym == 'BackSpace':
            current = self.get_display_value()
            if len(current) > 1:
                self.update_display(current[:-1])
            else:
                self.update_display("0")
            self.current_input = self.get_display_value()
            return
    
    def add_number(self, num):
        """숫자 입력"""
        if self.result_shown:
            self.update_display("")
            self.result_shown = False
            self.previous_input = ""
            self.operator = ""
        
        current = self.get_display_value()
        
        if self.just_entered_operator:
            current = ""
            self.just_entered_operator = False
        
        if current == "0" and num != ".":
            current = ""
        
        self.update_display(current + num)
        self.current_input = self.get_display_value()
    
    def add_decimal(self):
        """소수점 추가"""
        if self.result_shown:
            self.update_display("0.")
            self.result_shown = False
            self.current_input = self.get_display_value()
            return
        
        current = self.get_display_value()
        
        if self.just_entered_operator:
            current = "0."
            self.just_entered_operator = False
            self.update_display(current)
            self.current_input = current
            return
        
        if '.' not in current:
            if current == "" or current == "0":
                current = "0."
            else:
                current += "."
            self.update_display(current)
            self.current_input = current
    
    def add_operator(self, op):
        """연산자 입력"""
        current = self.get_display_value()
        
        if current == "" or current in ['+', '−', '×', '÷']:
            return
        
        if self.previous_input != "" and self.operator != "" and not self.just_entered_operator:
            if current != "" and self.current_input != "":
                self.calculate()
                current = self.get_display_value()
        
        if not self.just_entered_operator:
            self.previous_input = current
            self.current_input = ""
        
        self.operator = op
        self.just_entered_operator = True
        self.result_shown = False
        
        self.display.config(text=self.previous_input + " " + op)
    
    def calculate(self):
        """= 버튼 또는 엔터키 - 실제 계산 수행"""
        display_text = self.get_display_value()
        
        if not display_text:
            return
        
        # 공백 제거 (키보드 입력: "100+100" → "100+100")
        # 공백이 있으면 제거 ("100 + 100" → "100+100")
        clean_text = display_text.replace(" ", "")
        
        # 연산자 찾기 (지원하는 모든 연산자)
        op_symbols = ['+', '−', '×', '÷', '-', '*', '/']
        op_found = ''
        op_pos = -1
        
        for op_symbol in op_symbols:
            pos = clean_text.find(op_symbol)
            if pos != -1:
                if op_pos == -1 or pos < op_pos:
                    op_pos = pos
                    op_found = op_symbol
        
        if op_pos == -1 or op_found == '':
            # 연산자가 없으면 그냥 현재 값 유지
            return
        
        # 숫자 부분 추출
        num1_str = clean_text[:op_pos]
        num2_str = clean_text[op_pos + 1:]
        
        # 숫자가 비어있으면 무시
        if not num1_str or not num2_str:
            return
        
        # UI 연산자로 변환
        op_map = {
            '+': '+',
            '-': '−',
            '*': '×',
            '/': '÷',
            '−': '−',
            '×': '×',
            '÷': '÷'
        }
        op = op_map.get(op_found, op_found)
        
        # 상태 업데이트
        self.previous_input = num1_str
        self.current_input = num2_str
        self.operator = op
        
        # 숫자 변환
        try:
            num1 = float(num1_str)
            num2 = float(num2_str)
        except ValueError:
            messagebox.showerror("오류", f"숫자를 정확히 입력해주세요!\n(예: 10+20)")
            return
        
        # 계산 실행
        try:
            if op == '+' or op == '+':
                result = num1 + num2
            elif op == '−' or op == '-':
                result = num1 - num2
            elif op == '×' or op == '*':
                result = num1 * num2
            elif op == '÷' or op == '/':
                if num2 == 0:
                    messagebox.showerror("오류", "0으로 나눌 수 없습니다!")
                    self.clear_all()
                    return
                result = num1 / num2
            else:
                return
            
            # 결과 표시
            result_str = str(result).rstrip('0').rstrip('.') if '.' in str(result) else str(result)
            
            # 히스토리에 저장
            history_entry = f"{num1_str} {op} {num2_str} = {result_str}"
            self.history.append(history_entry)
            if len(self.history) > 50:
                self.history.pop(0)
            
            self.update_display(result_str)
            self.current_input = result_str
            self.previous_input = ""
            self.operator = ""
            self.result_shown = True
            self.just_entered_operator = False
            
            self.update_history_badge()
            self.root.focus_set()
            
        except Exception as e:
            messagebox.showerror("오류", f"계산 중 오류 발생: {str(e)}")
            self.clear_all()
    
    def update_history_badge(self):
        count = len(self.history)
        if count > 0:
            self.history_btn.config(text=f"🕐 {count}")
        else:
            self.history_btn.config(text="🕐")
    
    def show_history(self):
        if not self.history:
            messagebox.showinfo("기록", "아직 계산 기록이 없습니다.")
            return
        
        if self.history_window is not None and self.history_window.winfo_exists():
            self.history_window.destroy()
        
        self.history_window = Toplevel(self.root)
        self.history_window.title("계산 기록")
        self.history_window.geometry("350x400")
        self.history_window.configure(bg='#2c2c2c')
        self.history_window.resizable(False, False)
        
        tk.Label(self.history_window, text="📜 계산 기록", font=("Arial", 16, "bold"),
                bg='#2c2c2c', fg='white').pack(pady=10)
        
        frame = tk.Frame(self.history_window, bg='#2c2c2c')
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox = Listbox(frame, font=("Arial", 12), bg='#3d3d3d', fg='white',
                         selectbackground='#f9a825', selectforeground='black',
                         yscrollcommand=scrollbar.set, height=15)
        
        for entry in reversed(self.history):
            listbox.insert(tk.END, entry)
        
        listbox.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.config(command=listbox.yview)
        
        def on_double_click(event):
            selection = listbox.curselection()
            if selection:
                idx = selection[0]
                real_idx = len(self.history) - 1 - idx
                entry = self.history[real_idx]
                if ' = ' in entry:
                    result_part = entry.split(' = ')[1]
                    self.update_display(result_part)
                    self.current_input = result_part
                    self.result_shown = True
                    self.history_window.destroy()
                    self.history_window = None
        
        listbox.bind('<Double-Button-1>', on_double_click)
        
        tk.Button(self.history_window, text="닫기", font=("Arial", 12),
                 bg='#555', fg='white', width=10, relief='flat',
                 command=lambda: self.close_history()).pack(pady=10)
        
        self.history_window.protocol("WM_DELETE_WINDOW", self.close_history)
    
    def close_history(self):
        if self.history_window is not None:
            self.history_window.destroy()
            self.history_window = None
    
    def toggle_sign(self):
        current = self.get_display_value()
        if current == "" or current == "0":
            return
        
        if current.startswith('-'):
            current = current[1:]
        else:
            current = '-' + current
        self.update_display(current)
        self.current_input = current
        self.root.focus_set()
    
    def function_action(self, func):
        if func == 'C':
            self.clear_all()
        elif func == 'CE':
            self.update_display("0")
            self.current_input = ""
        elif func == '%':
            current = self.get_display_value()
            if current != "" and current != "0":
                try:
                    val = float(current) / 100
                    result_str = str(val).rstrip('0').rstrip('.') if '.' in str(val) else str(val)
                    self.update_display(result_str)
                    self.current_input = result_str
                except:
                    pass
        self.root.focus_set()
    
    def clear_all(self):
        self.current_input = ""
        self.previous_input = ""
        self.operator = ""
        self.result_shown = False
        self.just_entered_operator = False
        self.update_display("0")
        self.root.focus_set()
    
    def memory_action(self, cmd):
        messagebox.showinfo("알림", f"{cmd} 기능은 준비 중입니다!")
        self.root.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    app = Calculator(root)
    root.mainloop()
