import arcade
from icecream import ic

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Platformer"

CHARACTER_SCALING = 0.4
TILE_SCALING = 0.25
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

PLAYER_MOVEMENT_SPEED = 5 * CHARACTER_SCALING
GRAVITY = 0.25
PLAYER_JUMP_SPEED = 5

LEFT_VIEWPOINT_MARGIN = 250
RIGHT_VIEWPOINT_MARGIN = 250
BOTTOM_VIEWPOINT_MARGIN = 50
TOP_VIEWPOINT_MARGIN = 100

TEXTURE_LEFT = 0
TEXTURE_RIGHT = 1


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__()

        self.scale = CHARACTER_SCALING
        self.textures = []
        self.mirrored = False
        self.frame = 0
        self._jump = 0


        self.jump_texture = arcade.load_texture(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_jump.png")
        self.fall_texture = arcade.load_texture(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_fall.png")
        self.idle_texture = arcade.load_texture(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png")
        # self.textures.append(texture)
        for x in range(6):
            texture = arcade.load_texture(
                f":resources:images/animated_characters/female_adventurer/femaleAdventurer_walk{x}.png")
            self.textures.append(texture)

        self.texture = self.idle_texture

    @property
    def jump(self):
        return self._jump

    @jump.setter
    def jump(self, value):
        self._jump = ic(value)

    def update(self):
        if self.frame + 1 == len(self.textures):
            self.frame = 0
        else:
            self.frame += 1

        self.center_x += self.change_x
        self.center_y += self.change_y

        if self.change_y > 0:
            self.texture = self.jump_texture
        elif self.change_y < 0:
            self.texture = self.fall_texture
        elif self.change_x < 0:
            if self.texture_transform.v == [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]:
                self.texture_transform.scale(-1, 1)
            self.texture = self.textures[self.frame]
        elif self.change_x > 0:
            if self.texture_transform.v == [-1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]:
                self.texture_transform.scale(-1, 1)
            self.texture = self.textures[self.frame]

        if self.velocity == [0, 0]:
            self.texture = self.idle_texture
            self.number_of_jumps = 0


class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.coin_list = None
        self.wall_list = None
        self.player_list = None

        self.player_sprite = None

        self.physics_engine = None

        self.view_bottom = 0
        self.view_left = 0

        self.score = 0

        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

        arcade.set_background_color(arcade.csscolor.SKY_BLUE)

    def setup(self):
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()

        self.view_bottom = 0
        self.view_left = 0

        self.score = 0

        self.player_sprite = Player()
        self.player_sprite.center_x = 128
        self.player_sprite.center_y = 200
        self.player_list.append(self.player_sprite)

        map_name = "Maps/map.tmx"
        platforms_layer_name = 'Platforms'
        coins_layer_name = 'Coins'

        my_map = arcade.tilemap.read_tmx(map_name)

        self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=platforms_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)

        self.coin_list = arcade.tilemap.process_layer(my_map, coins_layer_name, TILE_SCALING)

        # for x in range(0, 1250, 64):
        #     wall = arcade.Sprite(":resources:images/tiles/grassMid.png", TILE_SCALING)
        #     wall.center_x = x
        #     wall.center_y = 32
        #     self.wall_list.append(wall)

        # coordinate_list = [[512, 96], [256, 96], [768, 96]]
        #
        # for coordinate in coordinate_list:
        #     wall = arcade.Sprite(":resources:images/tiles/boxCrate_double.png", TILE_SCALING)
        #     wall.position = coordinate
        #     self.wall_list.append(wall)

        # for x in range(128, 1250, 256):
        #     coin = arcade.Sprite(":resources:images/items/coinGold.png", COIN_SCALING)
        #     coin.center_x = x
        #     coin.center_y = 96
        #     self.coin_list.append(coin)

        # self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite, self.wall_list, GRAVITY)
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             GRAVITY)

    def on_draw(self):
        arcade.start_render()
        self.wall_list.draw()
        self.coin_list.draw()
        self.player_list.draw()

        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom,
                         arcade.csscolor.WHITE, 18)

    def on_key_press(self, key, modifiers):
        if key == arcade.key.UP or key == arcade.key.W:
            if self.player_sprite.jump < 1:
                self.player_sprite.jump += 1
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.R:
            self.setup()

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = -0

    def on_update(self, delta_time: float):
        self.physics_engine.update()

        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.coin_list)

        for coin in coin_hit_list:
            coin.remove_from_sprite_lists()
            arcade.play_sound(self.collect_coin_sound)
            self.score += 1

        changed = False

        left_boundary = self.view_left + LEFT_VIEWPOINT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True

        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPOINT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed = True

        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPOINT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed = True

        bottom_boundary = self.view_bottom + BOTTOM_VIEWPOINT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed = True

        if changed:
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)

        if self.physics_engine.can_jump() and self.player_sprite.jump != 0:
            self.player_sprite.jump = 0

        self.player_list.update()


def main():
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == '__main__':
    main()
