import tkinter as tk

# Class GameObject
class GameObject:
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


# Class Ball
class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 5
        self.speed_increment = 0.1  # Tambahan kecepatan setiap update
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='yellow')  # Warna bola diubah jadi kuning
        super().__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        if coords[0] <= 0 or coords[2] >= width:  # Pantulan di sisi kiri/kanan
            self.direction[0] *= -1
        if coords[1] <= 0:  # Pantulan di sisi atas
            self.direction[1] *= -1
        
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

        # Tingkatkan kecepatan bola secara bertahap
        self.speed += self.speed_increment

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) / 2

        if len(game_objects) > 1:  # Pantulan jika menyentuh lebih dari 1 objek
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()

            if x > coords[2]:  # Pantulan di sisi kanan objek
                self.direction[0] = 1
            elif x < coords[0]:  # Pantulan di sisi kiri objek
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):  # Jika menyentuh Brick, kena hit
                game_object.hit()


# Class Paddle
class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 80
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#FFB643')  # Warna Paddle (oranye terang)
        super().__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:  # Gerakan Paddle
            super().move(offset, 0)
            if self.ball is not None:  # Bola bergerak bersama Paddle sebelum start
                self.ball.move(offset, 0)


# Class Brick
class Brick(GameObject):
    COLORS = {1: '#4535AA', 2: '#ED639E', 3: '#8FE1A2'}  # Warna sesuai jumlah hit

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')  # Bentuk dan warna Brick
        super().__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:  # Hancurkan jika hit mencapai 0
            self.delete()
        else:
            self.canvas.itemconfig(self.item,
                                   fill=Brick.COLORS[self.hits])  # Ubah warna setelah hit


# Class Game
class Game(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.lives = 3
        self.width = 610
        self.height = 400
        self.canvas = tk.Canvas(self, bg='pink',  # Background diganti jadi pink
                                width=self.width,
                                height=self.height)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 326)
        self.items[self.paddle.item] = self.paddle

        for x in range(5, self.width - 5, 75):  # Menambahkan Brick ke layar
            self.add_brick(x + 37.5, 50, 3)
            self.add_brick(x + 37.5, 70, 2)
            self.add_brick(x + 37.5, 90, 1)

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-20))  # Gerakan Paddle ke kiri
        self.canvas.bind('<Right>', lambda _: self.paddle.move(20))  # Gerakan Paddle ke kanan

    def setup_game(self):
        self.add_ball()  # Tambahkan bola baru
        self.update_lives_text()
        self.text = self.draw_text(300, 200, 'Tekan Spasi untuk mulai')  # Instruksi dalam bahasa Indonesia
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        if self.ball is not None:  # Hapus bola lama jika ada
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) / 2
        self.ball = Ball(self.canvas, x, 310)  # Posisi bola di atas Paddle
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)  # Tambahkan Brick baru
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        font = ('Forte', size)
        return self.canvas.create_text(x, y, text=text, font=font)

    def update_lives_text(self):
        text = f'Nyawa: {self.lives}'  # Tulisan nyawa dalam bahasa Indonesia
        if self.hud is None:
            self.hud = self.draw_text(50, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')  # Hapus bind spasi saat game mulai
        self.canvas.delete(self.text)  # Hapus teks instruksi
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()  # Periksa tabrakan
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:  # Menang jika semua Brick hancur
            self.ball.speed = None
            self.draw_text(300, 200, 'Kamu Menang! Hebat!')
        elif self.ball.get_position()[3] >= self.height:  # Bola jatuh ke bawah
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:  # Game Over jika nyawa habis
                self.draw_text(300, 200, 'Game Over!')
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()  # Update posisi bola
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)  # Periksa tabrakan bola dengan objek lain


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Hancurkan Brick!')  # Judul game dalam bahasa Indonesia
    game = Game(root)
    game.mainloop()
