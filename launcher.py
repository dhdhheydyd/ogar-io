from customtkinter import *
from random import randint, choice


class ConnectWindow(CTk):
    def __init__(self):
        super().__init__()

        self.name = None
        self.host = None
        self.port = None
        self.skin = 0

        self.title('AGARIO LAUNCHER')
        self.geometry('600x540')
        self.resizable(False, False)

        self.bg_color = '#0D0D0D'
        self.configure(fg_color=self.bg_color)

        self.canvas = CTkCanvas(self, width=600, height=540, bg=self.bg_color, highlightthickness=0)
        self.canvas.place(x=0, y=0)

        colors = ['#00E676', '#2979FF', '#FF9100', '#FF1744', '#D500F9', '#C6FF00', '#00E5FF']
        for _ in range(28):
            r = randint(8, 22)
            x = randint(10, 590)
            y = randint(10, 530)
            color = choice(colors)
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline='')

        self.title_label = CTkLabel(
            self,
            text='⚡ AGARIO BATTLE ⚡',
            font=('Comic Sans MS', 32, 'bold'),
            text_color='#00E676',
            fg_color=self.bg_color
        )
        self.title_label.pack(pady=(30, 20))

        self.name_entry = CTkEntry(
            self,
            placeholder_text='👤 Ваш нікнейм',
            width=360,
            height=45,
            corner_radius=15,
            fg_color='#262626',
            border_color='#404040',
            text_color='white',
            placeholder_text_color='#9E9E9E',
            font=('Arial', 14)
        )
        self.name_entry.pack(pady=8)


        self.skins_map = {
            '🟢 Зелений неон': 0,
            '🔵 Кібер-синій': 1,
            '🟣 Фіолетовий космос': 2,
            '🟡 Золотий злиток': 3,
            '🔴 Кривавий рубін': 4,
            '🟠 Вогняна лава': 5,
            '⚪ Крижаний кристал': 6,
            '☢️Токсичний мутант': 7,
            'Мішень': 8,
            'глаз': 9,
            'Кавун': 10,
        }

        self.skin_menu = CTkOptionMenu(
            self,
            values=list(self.skins_map.keys()),
            width=360,
            height=45,
            corner_radius=15,
            fg_color='#262626',
            button_color='#00C853',
            button_hover_color='#00E676',
            text_color='white',
            font=('Arial', 14)
        )
        self.skin_menu.set('🟢 Зелений неон')
        self.skin_menu.pack(pady=8)

        self.host_entry = CTkEntry(
            self,
            placeholder_text='🌐 IP сервера',
            width=360,
            height=45,
            corner_radius=15,
            fg_color='#262626',
            border_color='#404040',
            text_color='white',
            placeholder_text_color='#9E9E9E',
            font=('Arial', 14)
        )
        self.host_entry.pack(pady=8)

        self.port_entry = CTkEntry(
            self,
            placeholder_text='🔌 Порт сервера',
            width=360,
            height=45,
            corner_radius=15,
            fg_color='#262626',
            border_color='#404040',
            text_color='white',
            placeholder_text_color='#9E9E9E',
            font=('Arial', 14)
        )
        self.port_entry.pack(pady=8)

        self.start_btn = CTkButton(
            self,
            text='🚀 Старт гри!',
            command=self.open_game,
            width=220,
            height=50,
            corner_radius=20,
            fg_color='#00C853',
            hover_color='#00E676',
            text_color='white',
            font=('Arial', 18, 'bold'),
            bg_color=self.bg_color
        )
        self.start_btn.pack(pady=(20, 20))

    def open_game(self):
        self.name = self.name_entry.get() or 'Player'
        self.host = self.host_entry.get() or 'localhost'
        self.skin = self.skins_map.get(self.skin_menu.get(), 0)
        try:
            self.port = int(self.port_entry.get())
        except ValueError:
            self.port = 1111
        self.destroy()
