import tkinter as tk
from tkinter import messagebox
import random


class SudokuGame:
    """Tkinter tabanlı Etkileşimli Sudoku Oyunu ve Jeneratörü/Çözücüsü."""

    def __init__(self, master):
        self.master = master
        master.title("Etkileşimli Sudoku Oyunu")

        self.puzzle_board = []  # Başlangıç bulmacası (sabit sayılar)
        self.solved_board = []  # Çözülmüş tahta (kontrol ve çözüm için)
        self.entries = {}  # Tkinter Entry widget'ları sözlüğü
        self.current_mode = None  # 'oyna' veya 'çöz'

        # Tkinter giriş doğrulama komutunu hazırla
        self.vcmd = (master.register(self.validate_input), '%P')

        # Başlangıç menüsünü göster
        self.show_start_menu()

    # --- Temel GUI Yöneticileri ---

    def clear_frame(self, frame):
        """Bir çerçevedeki tüm widget'ları temizler."""
        for widget in frame.winfo_children():
            widget.destroy()

    def show_start_menu(self):
        """Kullanıcıya 'Oyna' veya 'Çöz' seçeneklerini sunar."""
        self.clear_frame(self.master)

        menu_frame = tk.Frame(self.master, padx=50, pady=50)
        menu_frame.pack(pady=50)

        tk.Label(menu_frame, text="Ne yapmak istersiniz?", font=('Arial', 16, 'bold')).pack(pady=20)

        play_button = tk.Button(menu_frame,
                                text="1. Sudoku Oyna (Yeni Bulmaca)",
                                font=('Arial', 14),
                                command=lambda: self.start_game('oyna'))
        play_button.pack(pady=10, ipadx=10, ipady=5)

        solve_button = tk.Button(menu_frame,
                                 text="2. Sudoku Çöz (Elle Giriş)",
                                 font=('Arial', 14),
                                 command=lambda: self.start_game('çöz'))
        solve_button.pack(pady=10, ipadx=10, ipady=5)

    def start_game(self, mode):
        """Seçilen moda göre oyunu başlatır."""
        self.current_mode = mode
        self.clear_frame(self.master)
        self.entries = {}  # Yeni tahta için Entry'leri temizle

        # Tahta çerçevesini oluştur
        self.board_frame = tk.Frame(self.master, borderwidth=5, relief="raised")
        self.board_frame.pack(padx=20, pady=20)

        self.create_grid()
        self.create_buttons()

        if mode == 'oyna':
            self.generate_new_game()
        elif mode == 'çöz':
            self.prepare_solver_mode()

    # --- GUI (Arayüz) Oluşturma ---

    def create_grid(self):
        """Sudoku tahtasını Tkinter Entry widget'ları ile oluşturur."""
        for r in range(9):
            for c in range(9):
                entry = tk.Entry(self.board_frame,
                                 width=2,
                                 font=('Arial', 18, 'bold'),
                                 justify='center',
                                 borderwidth=1,
                                 relief="solid",
                                 validate='key',
                                 validatecommand=self.vcmd)  # Doğrulama komutu

                # 3x3 kutuları ayıran kalın çizgiler için padding
                pad_x = (3, 3) if c % 3 == 2 and c != 8 else (1, 1)
                pad_y = (3, 3) if r % 3 == 2 and r != 8 else (1, 1)

                entry.grid(row=r, column=c, padx=pad_x, pady=pad_y, ipady=5)
                self.entries[(r, c)] = entry

                # Oynama modunda anlık kontrolü etkinleştir
                entry.bind('<KeyRelease>', lambda event, r=r, c=c: self.check_input(event, r, c))

    def create_buttons(self):
        """Moda özgü butonları oluşturur."""
        button_frame = tk.Frame(self.master)
        button_frame.pack(pady=10)

        # Geri Dön Butonu (Her modda sabit)
        tk.Button(button_frame, text="Ana Menüye Dön", command=self.show_start_menu).pack(side=tk.RIGHT, padx=10)

        if self.current_mode == 'oyna':
            tk.Button(button_frame, text="Yeni Oyun Başlat", command=self.generate_new_game).pack(side=tk.LEFT, padx=10)
            tk.Button(button_frame, text="Çözümü Göster", command=self.solve_current_game).pack(side=tk.LEFT, padx=10)

        elif self.current_mode == 'çöz':
            tk.Button(button_frame, text="Sudoku'yu Çöz", command=self.solve_current_game).pack(side=tk.LEFT, padx=10)
            tk.Button(button_frame, text="Temizle", command=self.prepare_solver_mode).pack(side=tk.LEFT,
                                                                                           padx=10)  # Aynı işlev

    def populate_grid(self):
        """Oluşturulan bulmacayı GUI'ye yerleştirir ve eski girişleri siler."""
        for r in range(9):
            for c in range(9):
                value = self.puzzle_board[r][c]
                entry = self.entries[(r, c)]

                entry.config(state='normal', bg='white', fg='black')
                entry.delete(0, tk.END)

                if value != 0:
                    # Sabit başlangıç sayıları (Oynama modu)
                    entry.insert(0, str(value))
                    entry.config(state='readonly', fg='black', bg='#E0E0E0')
                else:
                    # Kullanıcının dolduracağı boş kutular
                    entry.config(state='normal', fg='black', bg='white')

    # --- Kontrol ve Etkileşim ---

    def validate_input(self, P):
        """Tkinter'ın validatecommand'ı tarafından çağrılır. Sadece 1-9 arası rakamlara izin verir."""
        if P.isdigit() and P != '0' and len(P) <= 1:
            return True
        if P == "":  # Silme (backspace) işlemine izin ver
            return True
        return False

    def check_input(self, event, r, c):
        """Kullanıcının girdiği sayının doğruluğunu anlık olarak kontrol eder (Sadece OYNA modunda)."""
        if self.current_mode != 'oyna' or not self.solved_board or not self.solved_board[0][0]:
            return  # Çözme modunda veya çözülmüş tahta yoksa anlık kontrol yapma

        entry = self.entries[(r, c)]
        current_val = entry.get().strip()

        # Boşaltılmışsa rengi sıfırla
        if current_val == "":
            entry.config(bg='white', fg='black')
            return

        # Giriş doğrulandı (validate_input), sadece kontrol kaldı
        num = int(current_val)

        if num == self.solved_board[r][c]:
            # Doğru
            entry.config(bg='#D4EDDA', fg='green')
            self.check_win()
        else:
            # Yanlış
            entry.config(bg='#F8D7DA', fg='red')

    def check_win(self):
        """Oyunun tamamlanıp tamamlanmadığını kontrol eder."""
        for r in range(9):
            for c in range(9):
                value = self.entries[(r, c)].get().strip()
                # Eğer boşsa veya doğru değilse
                if not value or int(value) != self.solved_board[r][c]:
                    return

        messagebox.showinfo("Tebrikler!", "Sudoku'yu başarıyla çözdünüz!")

    # --- Jeneratör (Bulmaca Oluşturucu) Fonksiyonları ---

    def _get_removal_count(self, difficulty='medium'):
        """Zorluğa göre kaldırılacak sayı sayısını döndürür."""
        if difficulty == 'easy':
            return random.randint(35, 40)
        elif difficulty == 'hard':
            return random.randint(55, 60)
        return random.randint(45, 50)  # 'medium'

    def _is_safe(self, board, row, col, num):
        """Verilen sayının geçerli olup olmadığını kontrol eder (satır, sütun ve 3x3 kutu)."""
        # Satır ve Sütun kontrolü
        for i in range(9):
            if board[row][i] == num or board[i][col] == num:
                return False
        # 3x3 kutu kontrolü
        start_row, start_col = row - row % 3, col - col % 3
        for i in range(3):
            for j in range(3):
                if board[start_row + i][start_col + j] == num:
                    return False
        return True

    def _find_empty_location(self, board):
        """Tahtadaki ilk boş (0) hücreyi bulur."""
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return i, j
        return None, None

    def _fill_board(self, board):
        """Backtracking kullanarak tahtayı çözer veya oluşturur."""
        row, col = self._find_empty_location(board)
        if row is None:
            return True  # Çözüldü

        nums = list(range(1, 10))
        random.shuffle(nums)  # Rastgele çözümü/oluşturmayı sağlamak için

        for num in nums:
            if self._is_safe(board, row, col, num):
                board[row][col] = num
                if self._fill_board(board):
                    return True
                board[row][col] = 0  # Geri izleme (backtrack)

        return False

    def _remove_numbers(self):
        """Çözülmüş tahtadan rastgele sayıları kaldırarak bulmacayı oluşturur."""
        cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(cells)
        removed_count = 0

        for r, c in cells:
            if removed_count >= self._get_removal_count():
                break
            # NOT: Bu basit kaldırma tek çözüm garantisi vermez, ancak hızlı bulmaca oluşturur.
            self.puzzle_board[r][c] = 0
            removed_count += 1

    def generate_new_game(self):
        """Yeni bir Sudoku oyunu oluşturur ve başlatır."""
        self.base_board = [[0] * 9 for _ in range(9)]
        self._fill_board(self.base_board)
        self.solved_board = [row[:] for row in self.base_board]

        self.puzzle_board = [row[:] for row in self.solved_board]
        self._remove_numbers()

        self.populate_grid()  # GUI'yi güncelle

    # --- Sudoku Çözücü Modu Fonksiyonları ---

    def prepare_solver_mode(self):
        """Çözme modu için tahtayı tamamen boş ve düzenlenebilir hale getirir."""
        self.puzzle_board = [[0] * 9 for _ in range(9)]
        self.solved_board = [[0] * 9 for _ in range(9)]

        for r in range(9):
            for c in range(9):
                entry = self.entries[(r, c)]
                # Tamamen düzenlenebilir (normal state), beyaz arka plan
                entry.config(state='normal', bg='white', fg='black')
                entry.delete(0, tk.END)

    def get_current_board(self):
        """GUI'deki mevcut tahta durumunu bir 9x9 listeye alır."""
        current_board = [[0] * 9 for _ in range(9)]
        for r in range(9):
            for c in range(9):
                entry = self.entries[(r, c)]
                value = entry.get().strip()
                if value.isdigit() and value != '0':
                    current_board[r][c] = int(value)
                else:
                    current_board[r][c] = 0
        return current_board

    def solve_current_game(self):
        """Mevcut tahtayı almaya çalışır, çözer ve sonucu gösterir."""

        current_board = self.get_current_board()
        solving_board = [row[:] for row in current_board]

        # Oynama modunda çözüm tahtasını kullanıyoruz
        if self.current_mode == 'oyna':
            solving_board = [row[:] for row in self.puzzle_board]

        if self._fill_board(solving_board):

            if self.current_mode == 'oyna':
                messagebox.showinfo("Çözüm Gösterildi", "İşte bu bulmacanın çözümü.")
            else:
                messagebox.showinfo("Çözüldü", "Sudoku başarıyla çözüldü!")

            self.display_solved_board(solving_board)
            self.solved_board = solving_board  # Kontrol/Çözüm için solved_board'u güncelle
        else:
            messagebox.showerror("Hata",
                                 "Mevcut tahta geçerli bir Sudoku çözümüne sahip değil. Lütfen girdiğiniz sayıları kontrol edin.")

    def display_solved_board(self, solved_board):
        """Verilen çözümü GUI'deki Entry'lere yazar."""
        for r in range(9):
            for c in range(9):
                entry = self.entries[(r, c)]
                value = solved_board[r][c]

                entry.config(state='normal')
                entry.delete(0, tk.END)
                entry.insert(0, str(value))

                # Çözülen hücreleri vurgula ve düzenlemeye kapat
                entry.config(bg='#FFF3CD', fg='black', state='readonly')


            # --- Programı Başlatma ---


if __name__ == "__main__":
    root = tk.Tk()
    game = SudokuGame(root)

    root.mainloop()
