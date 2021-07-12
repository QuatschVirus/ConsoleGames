import random, sys, os, time
from ConsoleBooster import \
    FancyText  # My own library for making the use of the console easier. This is currently not available to the open, this system will download it for itself.
# TODO: Add import cheking and downloading of my libs
from osplus import Logs, Configs  # My own library for helping with some stuff.
from colorama import init, Fore  # A library for making colorful texts

init(convert=True)  #Sets up colorama to work with th windows command line #TODO: Only use this on windows

log = Logs.Normal('main.log')  #Creating a log file to log the actions that the program has taken.
config = Configs.YAML('settings.yml')  #Creating a configuration for saving some settings
log.reset()  #Resets the log to be empty for every run of this program

field_size = int(config.get('size'))


class SnakeHead:  #The object that is used for the head of the snake.
    def __init__(self, letter=Fore.GREEN + config.get("letters")["SnakeHead"] + Fore.RESET):
        self.x = random.randint(0, field_size - 1)
        self.y = random.randint(0, field_size - 1)
        self.direction = "d"
        self.letter = letter
        grid.set(self.x, self.y, self.letter, surpress_length_warning=True)  #Using my ConsoleBooster.FancyText library, this accesses a sort of grid to display the tiles
        log.log("SnakeHead", "Initalization", f"Position={self.x}|{self.y}; Letter={self.letter}")  #Example of logging something with osplus
        if "dev" in sys.argv:
            print(f"Initalized SnakeHead at {self.x}|{self.y} with the letter {self.letter}")

    def move(self):
        if self.direction == config.get("moves")["up"]:
            self.y -= 1
        elif self.direction == config.get("moves")["left"]:
            self.x -= 1
        elif self.direction == config.get("moves")["down"]:
            self.y += 1
        elif self.direction == config.get("moves")["right"]:
            self.x += 1
        log.log("SnakeHead", "Move", f"Position={self.x}|{self.y}; Letter={self.letter}")
        if "dev" in sys.argv:
            print(f"Updated SnakeHead to {self.x}|{self.y}")

    def draw(self):
        try:
            grid.set(self.x, self.y, self.letter, surpress_length_warning=True)
        except FancyText.CoordsOutOfBoundryError:
            return True
        return False


class SnakeTail:  #Object for a tail of the Snake
    def __init__(self, x: int, y: int, letter=Fore.GREEN + config.get("letters")["SnakeTail"] + Fore.RESET):
        self.x = x
        self.y = y
        self.letter = letter
        grid.set(self.x, self.y, self.letter, surpress_length_warning=True)
        log.log("SnakeTail", "Initalization", f"Position={self.x}|{self.y}; Letter={self.letter}")
        if "dev" in sys.argv:
            print(f"Initalized SnakeTail at {x}|{y} with the letter {self.letter}")

    def move(self, x: int, y: int):
        out = self.x, self.y
        self.x = x
        self.y = y
        grid.set(x, y, self.letter, surpress_length_warning=True)
        log.log("SnakeTail", "Move", f"Position={self.x}|{self.y}; Letter={self.letter}")
        if "dev" in sys.argv:
            print(f"Updated SnakeTail to {self.x}|{self.y}")
        return out


class Apple:  #The object for the apple the Snake needs to eat
    def __init__(self, letter=Fore.RED + config.get("letters")["Apple"] + Fore.RESET):
        self.x = random.randint(0, field_size - 1)
        self.y = random.randint(0, field_size - 1)
        self.letter = letter
        grid.set(self.x, self.y, self.letter, surpress_length_warning=True)
        log.log("Apple", "Initalization", f"Position={self.x}|{self.y}; Letter={self.letter}")
        if "dev" in sys.argv:
            print(f"Initalized Apple at {self.x}|{self.y} with the letter {self.letter}")

    def update(self):
        grid.set(self.x, self.y, self.letter, surpress_length_warning=True)

    def eat(self):
        self.x = random.randint(0, field_size - 1)
        self.y = random.randint(0, field_size - 1)
        log.log("Apple", "Eaten", f"Position={self.x}|{self.y}; Letter={self.letter}")
        if "dev" in sys.argv:
            print(f"New Apple at {self.x}|{self.y}")
        return self.x, self.y


class Snake:  #The Snake as a whole
    def __init__(self):
        self.dead = False
        self.eaten = False
        self.score = 0
        self.head = SnakeHead()
        self.tails = []
        self.apple = Apple()

    def update(self):
        x = self.head.x
        y = self.head.y
        self.head.move()
        self.apple.update()
        self.dead = self.head.draw()
        if self.dead:
            return
        for tail in self.tails:
            x, y = tail.move(x, y)
        if self.eaten:
            self.eaten = False
            self.tails.append(SnakeTail(x, y))
        if self.head.x == self.apple.x and self.head.y == self.apple.y:
            self.eaten = True
            self.score += 1
            x, y = self.apple.eat()
            if "dev" in sys.argv:
                print(f"#{grid.get(x, y)}#")
            while grid.occupied(x, y):
                if "dev" in sys.argv:
                    print(f"#{grid.get(self.apple.x, self.apple.y)}#")
                x, y = self.apple.eat()
            self.apple.update()
        for tail in self.tails:
            if self.head.x == tail.x and self.head.y == tail.y:
                self.dead = True
                return

    def draw(self):
        if "dev" in sys.argv:
            print("-----CLS-----")
        else:
            os.system("cls")
        grid_out = grid.getOut(frame=config.get("letters")["Frame"])
        grid.reset()
        return f"Score: {self.score}\n" \
               f"{grid_out}"

    def loop(self):
        print(self.draw())
        self.head.direction = input("Next move: ")
        while not self.dead:
            self.update()
            if self.dead:
                break
            out = self.draw()
            print(out)
            self.head.direction = input("Next move: ")
            while self.head.direction not in (
                    config.get("moves")["up"], config.get("moves")["left"], config.get("moves")["down"],
                    config.get("moves")["right"]):
                os.system("cls")
                print(f"{Fore.RED}Invalid move: {self.head.direction}. Try again!{Fore.RESET}")
                print(out)
                self.head.direction = input("Next move: ")
        if "dev" in sys.argv:
            print("-----CLS-----")
        else:
            os.system("cls")
        print("You lost!")
        print(f"Score: {self.score}")


def game():  #This function controls the game itself
    global grid
    while True:
        grid = FancyText.Grid(field_size)
        snake = Snake()
        print("Welcome to Python Snake!\n")
        snake.loop()
        if input("Play again (y/n): ").lower() == "n":
            return


def settings():     #Tis function is used for changing the settings in the configuration file
    os.system("cls")
    print(f"""Size of the field: {config.get('size')}
Letter for the Head of the Snake: {config.get('letters')['SnakeHead']}
Letter for the Tail of the Snake: {config.get('letters')['SnakeTail']}
Letter for the Apple: {config.get('letters')['Apple']}
Letter for the Frame: {config.get('letters')['Frame']}
Character to move the snake up: {config.get('moves')['up']}
Character to move the snake left: {config.get('moves')['left']}
Character to move the snake down: {config.get('moves')['down']}
Character to move the snake right: {config.get('moves')['right']}""")
    size = input("Size of the field: ")
    if size == "":
        size = config.get("size")
    snakeHead = input("Letter for the Head of the Snake: ")
    if snakeHead == "":
        snakeHead = config.get('letters')['SnakeHead']
    snakeTail = input("Letter for the Tail of the Snake: ")
    if snakeTail == "":
        snakeTail = config.get('letters')['SnakeTail']
    apple = input("Letter for the Apple: ")
    if apple == "":
        apple = config.get('letters')['Apple']
    frame = input("Letter for the Frame: ")
    if frame == "":
        frame = config.get('letters')['Frame']
    up = input("Character to move the snake up: ")
    if up == "":
        up = config.get("moves")["up"]
    left = input("Character to move the snake left: ")
    if left == "":
        left = config.get("moves")["left"]
    down = input("Character to move the snake down: ")
    if down == "":
        down = config.get("moves")["down"]
    right = input("Character to move the snake right: ")
    if right == "":
        right = config.get("moves")["right"]
    config.set("size", size)
    config.set("letters", {"SnakeHead": snakeHead, "SnakeTail": snakeTail, "Apple": apple, "Frame": frame})
    config.set("moves", {"up": up, "left": left, "down": down, "right": right})
    os.system("cls")
    print(f"""Size of the field: {config.get('size')}
Letter for the Head of the Snake: {config.get('letters')['SnakeHead']}
Letter for the Tail of the Snake: {config.get('letters')['SnakeTail']}
Letter for the Apple: {config.get('letters')['Apple']}
Letter for the Frame: {config.get('letters')['Frame']}
Character to move the snake up: {config.get('moves')['up']}
Character to move the snake left: {config.get('moves')['left']}
Character to move the snake down: {config.get('moves')['down']}
Character to move the snake right: {config.get('moves')['right']}""")
    time.sleep(5)


def main():  #The main menu function
    os.system("cls")
    os.system("title ConsoleSnake - Made by QuatschVirus")
    print("""╔═══════════════════════════════════════╗
║ █████   █   █   █████   █   █   █████ ║
║ █       ██  █   █   █   █  █    █     ║
║ █       █ █ █   █   █   █ █     █     ║
║ █████   █  ██   █████   ██      █████ ║
║     █   █   █   █   █   █ █     █     ║
║     █   █   █   █   █   █  █    █     ║
║ █████   █   █   █   █   █   █   █████ ║
╚═══════════════════════════════════════╝
You can take the following actions: "start", "settings", "stop\"""")
    while True:
        command = input("What would you like to do? ").lower()
        if command == "start":
            game()
            break
        elif command == "settings":
            settings()
            break
        elif command == "stop":
            sys.exit("Quit")
        else:
            print(
                f"{Fore.RED}Invalid. Please try again! You can take the following actions: \"start\", \"settings\", \"stop\"{Fore.RESET}")


while __name__ == "__main__":
    main()
