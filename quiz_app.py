import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import docx
import re
import random
from pathlib import Path
import json

class ModernQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("人力资源服务刷题系统")
        self.root.geometry("1000x750")
        self.root.configure(bg='#f8f9fa')

        # 设置窗口最小尺寸
        self.root.minsize(800, 600)

        # 题目数据
        self.questions = []
        self.filtered_questions = []
        self.current_question_index = 0
        self.selected_options = set()
        self.is_answered = False
        self.correct_count = 0
        self.total_answered = 0
        self.option_vars = []  # 存储选项变量
        self.option_widgets = []  # 存储选项widget

        # 清新的白色配色方案
        self.colors = {
            'bg': '#f8f9fa',           # 主背景色
            'card_bg': '#ffffff',      # 卡片背景
            'primary': '#4285f4',      # 主色调-谷歌蓝
            'success': '#34a853',      # 成功-绿色
            'error': '#ea4335',        # 错误-红色
            'warning': '#fbbc05',      # 警告-黄色
            'text': '#202124',         # 主文字色
            'text_light': '#5f6368',   # 次要文字色
            'border': '#e0e0e0',       # 边框色
            'hover': '#f1f3f4',        # 悬停背景
            'option_bg': '#f8f9fa',    # 选项背景
            'option_selected': '#e8f0fe', # 选中背景-浅蓝
            'option_border': '#dadce0', # 选项边框
            'shadow': 'rgba(0,0,0,0.1)' # 阴影
        }

        # 设置字体
        self.fonts = {
            'title': ('Microsoft YaHei UI', 24, 'bold'),
            'subtitle': ('Microsoft YaHei UI', 14, 'bold'),
            'question': ('Microsoft YaHei UI', 16),
            'option': ('Microsoft YaHei UI', 14),
            'button': ('Microsoft YaHei UI', 11, 'bold'),
            'stats': ('Microsoft YaHei UI', 12)
        }

        # 创建界面
        self.setup_ui()

        # 自动加载题库
        self.auto_load_questions()

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        """设置用户界面"""
        # 创建主容器
        main_container = tk.Frame(self.root, bg=self.colors['bg'])
        main_container.pack(fill='both', expand=True, padx=20, pady=20)

        # 顶部标题和统计区域
        self.create_header(main_container)

        # 中间主要内容区域
        content_frame = tk.Frame(main_container, bg=self.colors['bg'])
        content_frame.pack(fill='both', expand=True, pady=(10, 0))

        # 左侧题目列表
        self.create_sidebar(content_frame)

        # 右侧题目内容（带滚动功能）
        self.create_question_area(content_frame)

        # 底部控制按钮（固定位置）
        self.create_controls(main_container)

    def create_header(self, parent):
        """创建顶部标题栏"""
        header_frame = tk.Frame(parent, bg=self.colors['card_bg'], height=80, relief='raised', bd=1)
        header_frame.pack(fill='x')
        header_frame.pack_propagate(False)

        # 标题
        title_label = tk.Label(header_frame,
                               text="📚 人力资源服务刷题系统",
                               font=self.fonts['title'],
                               fg=self.colors['primary'],
                               bg=self.colors['card_bg'])
        title_label.pack(side='left', padx=30, pady=20)

        # 右侧区域
        right_frame = tk.Frame(header_frame, bg=self.colors['card_bg'])
        right_frame.pack(side='right', padx=30, pady=20)

        # 统计信息
        self.progress_var = tk.StringVar(value="题目: 0/0")
        progress_label = tk.Label(right_frame,
                                 textvariable=self.progress_var,
                                 font=self.fonts['stats'],
                                 fg=self.colors['text_light'],
                                 bg=self.colors['card_bg'])
        progress_label.pack(side='right', padx=20)

        # 题目类型筛选
        filter_container = tk.Frame(right_frame, bg=self.colors['card_bg'])
        filter_container.pack(side='right', padx=20)

        tk.Label(filter_container,
                text="题型:",
                font=self.fonts['stats'],
                fg=self.colors['text_light'],
                bg=self.colors['card_bg']).pack(side='left', padx=(0, 5))

        self.filter_var = tk.StringVar(value="全部")
        self.filter_btn = tk.Button(filter_container,
                                   textvariable=self.filter_var,
                                   command=self.show_filter_menu,
                                   font=self.fonts['stats'],
                                   bg=self.colors['primary'],
                                   fg='white',
                                   activebackground='#3367d6',
                                   borderwidth=0,
                                   padx=15,
                                   pady=5,
                                   cursor='hand2',
                                   relief='flat')
        self.filter_btn.pack(side='left')

    def create_sidebar(self, parent):
        """创建左侧题目列表"""
        sidebar = tk.Frame(parent, bg=self.colors['card_bg'], width=250, relief='raised', bd=1)
        sidebar.pack(side='left', fill='y', padx=(0, 10))
        sidebar.pack_propagate(False)

        # 题目列表标题
        list_title = tk.Label(sidebar,
                             text="题目列表",
                             font=self.fonts['subtitle'],
                             fg=self.colors['text'],
                             bg=self.colors['card_bg'])
        list_title.pack(pady=10)

        # 题目列表容器
        list_frame = tk.Frame(sidebar, bg=self.colors['card_bg'])
        list_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # 创建滚动条和列表框（隐藏滚动条）
        scrollbar = tk.Scrollbar(list_frame, width=0)
        scrollbar.pack(side='right', fill='y')

        self.question_listbox = tk.Listbox(list_frame,
                                          yscrollcommand=scrollbar.set,
                                          font=self.fonts['option'],
                                          bg=self.colors['option_bg'],
                                          fg=self.colors['text'],
                                          selectbackground=self.colors['option_selected'],
                                          selectforeground=self.colors['text'],
                                          borderwidth=0,
                                          highlightthickness=0,
                                          activestyle='none',
                                          relief='flat')
        self.question_listbox.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.question_listbox.yview)

        self.question_listbox.bind('<<ListboxSelect>>', self.on_question_select)

    def create_question_area(self, parent):
        """创建右侧题目内容区域（带滚动）"""
        # 创建主容器
        question_container = tk.Frame(parent, bg=self.colors['card_bg'], relief='raised', bd=1)
        question_container.pack(side='right', fill='both', expand=True)

        # 创建Canvas和隐藏的Scrollbar
        self.canvas = tk.Canvas(question_container,
                               bg=self.colors['card_bg'],
                               highlightthickness=0,
                               bd=0)
        scrollbar = tk.Scrollbar(question_container,
                                orient='vertical',
                                command=self.canvas.yview,
                                width=0)  # 设置为0隐藏滚动条
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['card_bg'])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor='nw')
        self.canvas.configure(yscrollcommand=scrollbar.set)

        # 题目卡片（在scrollable_frame内）
        self.question_card = tk.Frame(self.scrollable_frame, bg=self.colors['card_bg'])
        self.question_card.pack(fill='both', expand=True, padx=30, pady=30)

        # 题目类型标签
        self.type_label = tk.Label(self.question_card,
                                   text="",
                                   font=self.fonts['subtitle'],
                                   fg=self.colors['primary'],
                                   bg=self.colors['card_bg'])
        self.type_label.pack(anchor='w', pady=(0, 15))

        # 题目内容
        self.question_text = tk.Text(self.question_card,
                                     wrap='word',
                                     font=self.fonts['question'],
                                     bg=self.colors['card_bg'],
                                     fg=self.colors['text'],
                                     borderwidth=0,
                                     padx=0,
                                     pady=0,
                                     height=4,
                                     state='disabled',
                                     relief='flat')
        self.question_text.pack(fill='x', pady=(0, 25))

        # 选项容器
        self.options_container = tk.Frame(self.question_card, bg=self.colors['card_bg'])
        self.options_container.pack(fill='both', expand=True)

        # 答案和解析区域
        self.result_frame = tk.Frame(self.question_card, bg=self.colors['card_bg'])

        # 打包Canvas和Scrollbar
        self.canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind('<MouseWheel>', _on_mousewheel)

        # 绑定键盘事件
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        self.canvas.bind('<Enter>', _bind_to_mousewheel)
        self.canvas.bind('<Leave>', _unbind_from_mousewheel)

    def create_controls(self, parent):
        """创建底部控制按钮"""
        control_frame = tk.Frame(parent, bg=self.colors['bg'], height=60)
        control_frame.pack(fill='x', pady=(10, 0))
        control_frame.pack_propagate(False)

        # 按钮容器
        button_container = tk.Frame(control_frame, bg=self.colors['bg'])
        button_container.pack(expand=True)

        # 上一题按钮
        self.prev_btn = self.create_modern_button(button_container, "⬅ 上一题",
                                                 self.prev_question, 'normal')
        self.prev_btn.pack(side='left', padx=5)

        # 提交答案按钮
        self.submit_btn = self.create_modern_button(button_container, "✓ 提交答案",
                                                   self.submit_answer, 'primary')
        self.submit_btn.pack(side='left', padx=5)

        # 下一题按钮
        self.next_btn = self.create_modern_button(button_container, "下一题 ➡",
                                                 self.next_question, 'normal')
        self.next_btn.pack(side='left', padx=5)

        # 随机题目按钮
        self.random_btn = self.create_modern_button(button_container, "🎲 随机",
                                                   self.random_question, 'normal')
        self.random_btn.pack(side='left', padx=5)

        # 重置按钮
        self.reset_btn = self.create_modern_button(button_container, "⟲ 重置",
                                                   self.reset_quiz, 'warning')
        self.reset_btn.pack(side='left', padx=5)

        # 加载文件按钮
        self.load_btn = self.create_modern_button(button_container, "📁 加载文件",
                                                  self.load_file, 'normal')
        self.load_btn.pack(side='left', padx=5)

    def create_modern_button(self, parent, text, command, style='normal'):
        """创建现代化按钮"""
        bg_color = self.colors['primary'] if style == 'primary' else \
                  self.colors['warning'] if style == 'warning' else \
                  '#ffffff'
        text_color = 'white' if style in ['primary', 'warning'] else self.colors['text']

        btn = tk.Button(parent,
                       text=text,
                       command=command,
                       font=self.fonts['button'],
                       bg=bg_color,
                       fg=text_color,
                       activebackground=self.colors['hover'],
                       activeforeground=text_color,
                       borderwidth=1,
                       relief='solid',
                       cursor='hand2',
                       padx=20,
                       pady=8)
        return btn

    def show_filter_menu(self):
        """显示筛选菜单"""
        # 创建弹出菜单
        filter_menu = tk.Menu(self.root, tearoff=0, bg='white',
                             fg=self.colors['text'], activebackground=self.colors['option_selected'],
                             activeforeground=self.colors['text'], borderwidth=1,
                             relief='solid')

        options = ["全部", "单选题", "多选题", "判断题"]
        for option in options:
            filter_menu.add_command(label=option,
                                   command=lambda o=option: self.set_filter(o))

        # 在按钮下方显示菜单
        x = self.filter_btn.winfo_rootx()
        y = self.filter_btn.winfo_rooty() + self.filter_btn.winfo_height()
        filter_menu.tk_popup(x, y)
        filter_menu.grab_release()

    def set_filter(self, filter_type):
        """设置筛选类型"""
        self.filter_var.set(filter_type)
        self.filter_questions()

    def auto_load_questions(self):
        """自动加载题库文件"""
        # 优先加载docx文件
        docx_path = Path("sets/人力资源服务赛项模块一题库.docx")
        if docx_path.exists():
            self.load_docx_file(docx_path)
            return

        # 如果没有docx，查找txt文件
        txt_files = list(Path("sets").glob("*.txt"))
        if txt_files:
            self.load_txt_file(txt_files[0])
            return

        # 都没有则提示
        messagebox.showinfo("提示", "未找到题库文件，请点击'加载文件'按钮手动加载")

    def load_file(self):
        """手动加载文件"""
        file_path = filedialog.askopenfilename(
            title="选择题库文件",
            filetypes=[("Word文档", "*.docx"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if file_path:
            if file_path.endswith('.docx'):
                self.load_docx_file(Path(file_path))
            elif file_path.endswith('.txt'):
                self.load_txt_file(Path(file_path))
            else:
                messagebox.showerror("错误", "不支持的文件格式")

    def load_docx_file(self, docx_path):
        """加载Word文档"""
        try:
            if not docx_path.exists():
                messagebox.showerror("错误", "文件不存在！")
                return

            # 读取Word文档
            doc = docx.Document(docx_path)

            # 提取所有文本并合并
            text_lines = []
            for para in doc.paragraphs:
                text = para.text.strip()
                if text:
                    text_lines.append(text)

            # 解析题目
            self.questions = self.parse_questions(text_lines)
            self.filtered_questions = self.questions.copy()

            # 填充题目列表
            self.populate_question_list()

            # 显示第一题
            if self.questions:
                self.display_question(0)

            messagebox.showinfo("成功", f"题库加载成功！\n共 {len(self.questions)} 道题目")

        except Exception as e:
            messagebox.showerror("错误", f"加载Word文件失败：{str(e)}")

    def load_txt_file(self, txt_path):
        """加载文本文件"""
        try:
            if not txt_path.exists():
                messagebox.showerror("错误", "文件不存在！")
                return

            # 读取文本文件
            with open(txt_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 分割成行
            text_lines = [line.strip() for line in content.split('\n') if line.strip()]

            # 解析题目
            self.questions = self.parse_questions(text_lines)
            self.filtered_questions = self.questions.copy()

            # 填充题目列表
            self.populate_question_list()

            # 显示第一题
            if self.questions:
                self.display_question(0)

            messagebox.showinfo("成功", f"题库加载成功！\n共 {len(self.questions)} 道题目")

        except UnicodeDecodeError:
            # 尝试其他编码
            try:
                with open(txt_path, 'r', encoding='gbk') as f:
                    content = f.read()
                text_lines = [line.strip() for line in content.split('\n') if line.strip()]
                self.questions = self.parse_questions(text_lines)
                self.filtered_questions = self.questions.copy()
                self.populate_question_list()
                if self.questions:
                    self.display_question(0)
                messagebox.showinfo("成功", f"题库加载成功！\n共 {len(self.questions)} 道题目")
            except Exception as e:
                messagebox.showerror("错误", f"文件编码错误：{str(e)}")
        except Exception as e:
            messagebox.showerror("错误", f"加载文本文件失败：{str(e)}")

    def parse_questions(self, lines):
        """解析题目文本"""
        questions = []
        current_question = {}

        i = 0
        while i < len(lines):
            line = lines[i]

            # 检测题目开始
            question_match = re.match(r'^(\d+)\.\s*(.*)', line)
            if question_match:
                # 保存上一题
                if current_question:
                    questions.append(current_question)

                # 开始新题
                current_question = {
                    'number': int(question_match.group(1)),
                    'question': question_match.group(2),
                    'options': [],
                    'answer': '',
                    'analysis': '',
                    'type': '未知'
                }

            # 检测选项
            elif re.match(r'^[A-D]\.\s*', line):
                if current_question:
                    # 分离选项字母和内容
                    parts = line.split('.', 1)
                    if len(parts) == 2:
                        option = {
                            'letter': parts[0],
                            'text': parts[1].strip()
                        }
                        current_question['options'].append(option)

            # 检测答案和解析
            elif line.startswith('答案：'):
                if current_question:
                    # 合并答案和解析
                    answer_text = line.replace('答案：', '').strip()

                    # 查看下一行是否有解析
                    if i + 1 < len(lines) and lines[i + 1].startswith('解析：'):
                        i += 1
                        analysis_text = lines[i].replace('解析：', '').strip()
                        # 合并答案和解析
                        current_question['answer_analysis'] = f"{answer_text}\n\n解析：{analysis_text}"
                    else:
                        current_question['answer_analysis'] = answer_text

                    # 单独保存答案
                    current_question['answer'] = answer_text

            # 检测单独的解析（用于其他格式）
            elif line.startswith('解析：'):
                if current_question:
                    analysis_text = line.replace('解析：', '').strip()
                    i += 1
                    while i < len(lines) and not lines[i].startswith(('答案：', '解析：', str(len(questions) + 1) + '.')):
                        if lines[i].strip() and not re.match(r'^\d+\.\s*', lines[i]):
                            analysis_text += '\n' + lines[i].strip()
                        i += 1
                    i -= 1
                    if 'answer_analysis' in current_question:
                        current_question['answer_analysis'] += '\n\n' + analysis_text
                    else:
                        current_question['answer_analysis'] = analysis_text

            i += 1

        # 保存最后一题
        if current_question:
            questions.append(current_question)

        # 根据选项和答案判断题型
        for q in questions:
            q['type'] = self.determine_question_type(q)

        return questions

    def determine_question_type(self, question):
        """根据选项和答案判断题型"""
        # 根据选项数量判断
        if len(question['options']) == 0:
            # 没有选项，可能是判断题
            if question.get('answer', '') in ['正确', '错误']:
                return '判断题'
            else:
                return '判断题'  # 默认认为是判断题

        # 根据答案格式判断
        answer = question.get('answer', '')
        if '、' in answer:
            # 答案包含顿号，是多选题
            return '多选题'
        elif answer in ['A', 'B', 'C', 'D'] or len(answer) == 1:
            # 单个字母，单选题
            return '单选题'
        else:
            # 默认为单选题
            return '单选题'

    def populate_question_list(self):
        """填充题目列表"""
        self.question_listbox.delete(0, tk.END)
        for q in self.filtered_questions:
            status = "✓" if q.get('answered_correct', False) else "✗" if q.get('answered', False) else "○"
            self.question_listbox.insert(tk.END, f"{status} 第{q['number']}题 {q['type']}")

    def display_question(self, index):
        """显示题目"""
        if not self.filtered_questions or index < 0 or index >= len(self.filtered_questions):
            return

        self.current_question_index = index
        self.is_answered = False
        self.selected_options = set()
        self.option_vars = []  # 重置选项变量
        self.option_widgets = []  # 重置选项widget

        question = self.filtered_questions[index]

        # 更新进度
        self.progress_var.set(f"题目: {index + 1}/{len(self.filtered_questions)}")

        # 更新题目类型
        self.type_label.config(text=f"{question['type']} - 第{question['number']}题")

        # 显示题目内容
        self.question_text.config(state='normal')
        self.question_text.delete('1.0', 'end')
        self.question_text.insert('1.0', question['question'])
        self.question_text.config(state='disabled')

        # 清除旧的结果显示
        for widget in self.result_frame.winfo_children():
            widget.destroy()
        self.result_frame.pack_forget()

        # 清除旧的选项
        for widget in self.options_container.winfo_children():
            widget.destroy()

        # 创建选项
        if question['type'] == '判断题' or len(question['options']) == 0:
            # 判断题或无选项题目
            self.create_option_frame('正确', 0, None)
            self.create_option_frame('错误', 1, None)
        else:
            # 有选项的选择题
            for i, option in enumerate(question['options']):
                self.create_option_frame(option['text'], i, option['letter'])

        # 更新列表选中状态
        self.question_listbox.selection_clear(0, tk.END)
        self.question_listbox.selection_set(index)
        self.question_listbox.see(index)

        # 更新按钮状态
        self.prev_btn.config(state='normal' if index > 0 else 'disabled')
        self.next_btn.config(state='normal' if index < len(self.filtered_questions) - 1 else 'disabled')
        self.submit_btn.config(state='normal')

    def create_option_frame(self, text, index, letter=None):
        """创建可点击的选项框架（无装饰）"""
        # 创建选项变量
        if self.filtered_questions[self.current_question_index]['type'] == '多选题':
            var = tk.BooleanVar()
        else:
            var = tk.IntVar()

        self.option_vars.append(var)

        # 创建选项框架（整个可点击）
        option_frame = tk.Frame(self.options_container,
                               bg=self.colors['option_bg'],
                               cursor='hand2',
                               relief='solid',
                               bd=1)
        option_frame.pack(fill='x', pady=5)

        # 保存原始背景色
        option_frame.original_bg = self.colors['option_bg']
        option_frame.index = index
        option_frame.var = var

        # 创建选项标签（无圆点方块）
        option_label = tk.Label(option_frame,
                               text=f"{letter}. {text}" if letter else text,
                               font=self.fonts['option'],
                               bg=self.colors['option_bg'],
                               fg=self.colors['text'],
                               cursor='hand2')
        option_label.pack(side='left', padx=15, pady=12)

        # 保存引用
        self.option_widgets.append((option_frame, option_label))

        # 绑定点击事件（框架和标签都要绑定）
        click_command = lambda e=None, i=index: self.click_option(i)
        option_frame.bind('<Button-1>', click_command)
        option_label.bind('<Button-1>', click_command)

        # 绑定鼠标悬停事件
        def on_enter(e):
            if not self.is_answered:
                option_frame.config(bg=self.colors['hover'])
                option_label.config(bg=self.colors['hover'])

        def on_leave(e):
            if not self.is_answered:
                # 根据选中状态决定背景色
                if self.is_option_selected(index):
                    option_frame.config(bg=self.colors['option_selected'])
                    option_label.config(bg=self.colors['option_selected'])
                else:
                    option_frame.config(bg=self.colors['option_bg'])
                    option_label.config(bg=self.colors['option_bg'])

        option_frame.bind('<Enter>', on_enter)
        option_frame.bind('<Leave>', on_leave)
        option_label.bind('<Enter>', on_enter)
        option_label.bind('<Leave>', on_leave)

    def is_option_selected(self, index):
        """检查选项是否被选中"""
        if self.filtered_questions[self.current_question_index]['type'] == '多选题':
            return self.option_vars[index].get()
        else:
            return self.option_vars[index].get() == index

    def click_option(self, index):
        """点击选项"""
        if self.is_answered:
            return

        question_type = self.filtered_questions[self.current_question_index]['type']

        if question_type == '多选题':
            # 多选题切换选中状态
            var = self.option_vars[index]
            var.set(not var.get())
            if var.get():
                self.selected_options.add(index)
            else:
                self.selected_options.discard(index)
        else:
            # 单选题和判断题
            self.selected_options.clear()
            self.selected_options.add(index)

            # 更新所有选项的状态
            for i, (frame, label) in enumerate(self.option_widgets):
                if i == index:
                    self.option_vars[i].set(index)
                    frame.config(bg=self.colors['option_selected'])
                    label.config(bg=self.colors['option_selected'])
                else:
                    self.option_vars[i].set(-1)
                    frame.config(bg=self.colors['option_bg'])
                    label.config(bg=self.colors['option_bg'])

    def toggle_option(self, index, var):
        """切换选项（已弃用）"""
        pass

    def select_radio_option(self, index):
        """选择单选选项（已弃用）"""
        pass

    def on_option_select(self, index, selected):
        """处理选项选择（已弃用）"""
        pass

    def on_question_select(self, event):
        """处理题目列表选择"""
        selection = self.question_listbox.curselection()
        if selection:
            self.display_question(selection[0])

    def submit_answer(self):
        """提交答案"""
        if self.is_answered:
            return

        if not self.selected_options:
            messagebox.showwarning("提示", "请选择答案后再提交")
            return

        self.is_answered = True
        self.total_answered += 1

        question = self.filtered_questions[self.current_question_index]
        is_correct = self.check_answer(question)

        if is_correct:
            self.correct_count += 1
            question['answered_correct'] = True
        question['answered'] = True

        # 显示结果
        self.show_result(question, is_correct)

        # 更新题目列表
        self.populate_question_list()
        self.question_listbox.selection_set(self.current_question_index)

        # 禁用提交按钮
        self.submit_btn.config(state='disabled')

    def disable_all_options(self):
        """禁用所有选项"""
        for frame, label in self.option_widgets:
            frame.config(cursor='')
            label.config(cursor='')

    def check_answer(self, question):
        """检查答案是否正确"""
        if question['type'] == '判断题':
            if len(self.selected_options) == 1:
                selected_index = list(self.selected_options)[0]
                selected_answer = '正确' if selected_index == 0 else '错误'
                return selected_answer == question.get('answer', '')

        elif question['type'] == '多选题':
            selected_letters = sorted([chr(65 + i) for i in self.selected_options])
            correct_letters = sorted([c.strip() for c in question.get('answer', '').split('、')])
            return selected_letters == correct_letters

        elif question['type'] == '单选题':
            if len(self.selected_options) == 1:
                selected_index = list(self.selected_options)[0]
                selected_letter = chr(65 + selected_index)
                return selected_letter == question.get('answer', '')

        return False

    def show_result(self, question, is_correct):
        """显示答题结果"""
        # 清除之前的结果
        for widget in self.result_frame.winfo_children():
            widget.destroy()

        # 创建分隔线
        separator = tk.Frame(self.result_frame, height=1, bg=self.colors['border'])
        separator.pack(fill='x', pady=20)

        # 创建结果标题
        result_text = "✓ 回答正确！" if is_correct else "✗ 回答错误"
        result_color = self.colors['success'] if is_correct else self.colors['error']

        result_label = tk.Label(self.result_frame,
                               text=result_text,
                               font=('Microsoft YaHei UI', 16, 'bold'),
                               fg=result_color,
                               bg=self.colors['card_bg'])
        result_label.pack(pady=(0, 10))

        # 显示答案和解析（合并显示）
        if 'answer_analysis' in question:
            # 创建答案解析文本框
            answer_text = tk.Text(self.result_frame,
                                 wrap='word',
                                 font=self.fonts['option'],
                                 bg=self.colors['option_bg'],
                                 fg=self.colors['text'],
                                 borderwidth=1,
                                 relief='solid',
                                 padx=15,
                                 pady=10)
            answer_text.pack(fill='x', pady=(0, 10))
            answer_text.insert('1.0', question['answer_analysis'])
            answer_text.config(state='disabled')
        else:
            # 如果没有合并的答案解析，只显示答案
            answer_label = tk.Label(self.result_frame,
                                   text=f"正确答案：{question.get('answer', '')}",
                                   font=self.fonts['option'],
                                   fg=self.colors['text'],
                                   bg=self.colors['card_bg'])
            answer_label.pack()

        self.result_frame.pack(fill='x', pady=(20, 0))

        # 禁用所有选项
        self.disable_all_options()

    def prev_question(self):
        """上一题"""
        if self.current_question_index > 0:
            self.display_question(self.current_question_index - 1)

    def next_question(self):
        """下一题"""
        if self.current_question_index < len(self.filtered_questions) - 1:
            self.display_question(self.current_question_index + 1)

    def random_question(self):
        """随机题目"""
        if self.filtered_questions:
            index = random.randint(0, len(self.filtered_questions) - 1)
            self.display_question(index)

    def filter_questions(self, event=None):
        """筛选题目"""
        filter_type = self.filter_var.get()

        if filter_type == "全部":
            self.filtered_questions = self.questions.copy()
        else:
            self.filtered_questions = [q for q in self.questions if q['type'] == filter_type]

        # 重新填充列表
        self.populate_question_list()

        # 显示第一题
        if self.filtered_questions:
            self.display_question(0)
        else:
            self.question_text.config(state='normal')
            self.question_text.delete('1.0', 'end')
            self.question_text.insert('1.0', "没有符合条件的题目")
            self.question_text.config(state='disabled')

    def reset_quiz(self):
        """重置答题进度"""
        if messagebox.askyesno("确认", "确定要重置所有答题记录吗？"):
            # 清除所有答题状态
            for q in self.questions:
                q['answered'] = False
                q['answered_correct'] = False

            # 重置统计
            self.correct_count = 0
            self.total_answered = 0

            # 重新显示当前题目
            if self.filtered_questions:
                self.display_question(self.current_question_index)

            # 更新列表
            self.populate_question_list()
            self.question_listbox.selection_set(self.current_question_index)

    def on_closing(self):
        """窗口关闭事件"""
        if messagebox.askokcancel("退出", "确定要退出刷题系统吗？"):
            self.root.destroy()


def main():
    root = tk.Tk()
    app = ModernQuizApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()