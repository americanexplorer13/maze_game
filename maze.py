from abc import ABCMeta, abstractmethod
import random
import pickle
import json
import os

random.seed()


class Game:
    def __init__(self):
        self.sys_mapper = {'exit': Game.exit_game, 'load': SerializeToPickle.deserialize, 'save': SerializeToPickle.serialize}

    @abstractmethod
    def check_command(self, command: str):
        for i in self.sys_mapper:
            if command == i:
                self.sys_mapper[command](level=world)

    @staticmethod
    def show(matrix: list) -> int:
        for i in matrix:
            print(i)
        print()
        return 0

    @staticmethod
    def startup():
        pass

    @staticmethod
    def exit_game():
        exit()


class GameObject(object):
    __metaclass__ = ABCMeta

    def __init__(self, x: int, y: int, object_icon: int):
        self.x = x
        self.y = y
        self.object_icon = object_icon
        world[self.x][self.y] = self.object_icon


class Treasure(GameObject):
    pass


class Storage(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def serialize(self, level: list):
        raise NotImplementedError("Not implemented")

    @abstractmethod
    def deserialize(self):
        raise NotImplementedError("Not implemented")


class SerializeToPickle(Storage):
    @staticmethod
    def serialize(level: list):
        with open(f'{input("Enter the name for save file: ")}.xyz', 'wb') as output:
            pickle.dump(level, output, pickle.HIGHEST_PROTOCOL)

    @staticmethod
    def deserialize():
        return pickle.load(open(f'{input("Enter the name for load file: ")}.xyz', "rb"))


class SerializeToJSON(Storage):
    @staticmethod
    def serialize(level: list):
        json_file = open(f'{input("Enter the name for save file: ")}.json', "x")
        json_file.write(json.dumps(level, indent=4))
        json_file.close()

    @staticmethod
    def deserialize():
        with open(f'{input("Enter the name for load file: ")}.json') as json_data:
            d = json.loads(json_data)
            json_data.close()
            pprint(d)


class Maze(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def generate_maze(self):
        raise NotImplementedError("Not implemented")


class Debug_Maze(Maze):
    def generate_maze(self):
        world_matrix = [[0 for x in range(world_len)] for y in range(world_len)]

        x = 1  # start coord X
        y = 1  # start coord Y
        begin_coord = [x, y]  # saving coord for player

        # 1: init begin point
        world_matrix[x][y] = 0

        for i in range(len(world_matrix)):
            world_matrix[0][i] = 1
            world_matrix[i][0] = 1
            world_matrix[len(world_matrix) - 1][i] = 1
            world_matrix[i][len(world_matrix) - 1] = 1

        # 3: check neighbours
        return world_matrix, begin_coord


class Random_Maze(Maze):
    def generate_maze(self):
        world_matrix = [[1 for x in range(world_len)] for y in range(world_len)]
        mov_mapper = {1: [0, -2], 2: [0, 2], 3: [-2, 0], 4: [2, 0]}  # to place next point in matrix
        path_mapper = {1: [0, -1], 2: [0, 1], 3: [-1, 0], 4: [1, 0]}  # to create path between points in matrix

        x = 1  # start coord X
        y = 1  # start coord Y
        begin_coord = [x, y]  # saving coord for player

        # 1: init begin point
        world_matrix[x][y] = 0

        # 2: create win trajectory
        while True:
            step = random.randint(1, 4)
            try:
                world_matrix[x + int(path_mapper[step][0])][y + int(path_mapper[step][1])] = 0  # create path between two point
                x += int(mov_mapper[step][0])  # new coord X
                y += int(mov_mapper[step][1])  # new coord Y
                world_matrix[x][y] = 0  # create path
            except IndexError:
                world_matrix[x][y] = 4  # create exit
                break

        # 3: check neighbours

        return world_matrix, begin_coord


class GameEntity(object):
    __metaclass__ = ABCMeta

    def __init__(self, x: int, y: int, entity_icon: int):
        self.x = x
        self.y = y
        self.hp = 2
        self.entity_icon = entity_icon
        world[self.x][self.y] = self.entity_icon

    @abstractmethod
    def handler(self, future_step: int):
        raise NotImplementedError("Not implemented")

    @abstractmethod
    def move(self, command: str):
        raise NotImplementedError("Not implemented")


class Player(GameEntity):
    def __init__(self, x: int, y: int, entity_icon: int):
        super().__init__(x, y, entity_icon)
        self.mov_mapper = {'a': [0, -1], 'd': [0, 1], 'w': [-1, 0], 's': [1, 0]}  # mapper for moving in matrix
        self.is_treasure = False

    def handler(self, future_step):
        # if object is path
        if future_step == 0:
            return True

        # if object is wall
        if future_step == 1:
            print("[GAME]: step impossible, wall")
            return False

        # if object is treasure
        if future_step == 2:
            print("[GAME]: Treasure was acquired! Move to the end!!!")
            self.is_treasure = True
            return True

        # if object is bear
        if future_step == 3 and self.hp > 1:
            self.damage(1)
            print("[GAME]: You were injured by bear!")
            return True
        else:
            print("[GAME]: You died!")
            Game.exit_game()

        # if object is exit but no treasure
        if future_step == 4 and self.is_treasure is not True:
            print("[GAME]: You can't leave the maze without treasure")
            return False

        # if object is exit and treasure
        if future_step == 4 and self.is_treasure is True:
            print("[GAME]: You escaped the maze!!!")
            Game.exit_game()

        # if object is wormhole
        if future_step == 9:
            print("[GAME]: You step on wormhole!")
            return True

    def damage(self, dmg: int):
        self.hp -= dmg

    def move(self, command: str):
        for step in self.mov_mapper:
            if step == command:
                future_step = world[self.x + int(self.mov_mapper[step][0])][self.y + int(self.mov_mapper[step][1])]
                if self.handler(future_step) is True:
                    world[self.x][self.y] = 0

                    # moving through the world
                    self.x += int(self.mov_mapper[step][0])
                    self.y += int(self.mov_mapper[step][1])

                    world[self.x][self.y] = self.entity_icon


class Bear(GameEntity):
    def __init__(self, x: int, y: int, entity_icon: int):
        super().__init__(x, y, entity_icon)
        self.mov_mapper = {1: [0, -1], 2: [0, 1], 3: [-1, 0], 4: [1, 0]}  # mapper for moving in matrix

    def handler(self, future_step):
        # if object is path
        if future_step == 0:
            return True

        # if object is wall
        if future_step == 1:
            return False

        # if object is treasure
        if future_step == 2:
            return False

        # if object is exit but no treasure
        if future_step == 4:
            return False

        # if object is wormhole
        if future_step == 9:
            return True

    def move(self, command: str = None):
        step = random.randint(1, 4)
        future_step = world[self.x + int(self.mov_mapper[step][0])][self.y + int(self.mov_mapper[step][1])]

        # handler what to do if occurs interaction with object
        if self.handler(future_step) is True:

            world[self.x][self.y] = 0

            # moving through the world
            self.x += int(self.mov_mapper[step][0])
            self.y += int(self.mov_mapper[step][1])

            world[self.x][self.y] = self.entity_icon


if __name__ == '__main__':

    # create the world of maze
    world_len = int(input("But before we start, let's create Amazing Maze: "))
    world, coord_xy = Debug_Maze().generate_maze()

    # start the game
    print('Amazing Maze by Kirill: 8 = player, 2 = Treasure, 3 = Bear, 1 = Obstacle, 9 = Wormhole')
    print('Walk by w a s d')

    # init game objects
    game = Game()
    player = Player(x=coord_xy[0], y=coord_xy[1], entity_icon=8)
    bear_1 = Bear(x=4, y=4, entity_icon=3)
    bear_2 = Bear(x=5, y=4, entity_icon=3)
    treasure = Treasure(x=3, y=4, object_icon=2)

    # main cycle for the game
    while True:
        game.show(world)
        command_line = input().lower()
        game.check_command(command_line)
        bear_1.move()
        bear_2.move()
        player.move(command_line)
