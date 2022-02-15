import socket
from typing import Literal

import constants
import game_data


class Player:
    """
    Player is the base class for different type of game players (bot, human).

    Attributes
    ----------
    host: str
        The ip of the server.
    port: int
        The port of the server.
    player_name: str
        The name associated with this player.

    Methods
    -------
    run()
        Start this entity.
    end()
        Terminate this entity.
    """

    def __init__(self, host: str, port: int, player_name: str) -> None:
        self.status = "Lobby"
        self.player_name = player_name
        # Init socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        # Start connection
        self.socket.send(game_data.ClientPlayerAddData(player_name).serialize())
        data = self.socket.recv(constants.DATASIZE)
        data = game_data.GameData.deserialize(data)
        if type(data) is game_data.ServerPlayerConnectionOk:
            print("Connection accepted by the server. Welcome " + player_name)
        print(f"[{player_name}-{self.status}]: ", end="")

    def _start_game(self):
        self.socket.send(
            game_data.ClientPlayerStartRequest(self.player_name).serialize()
        )

    def _player_ready(self):
        self.socket.send(game_data.ClientPlayerReadyData(self.player_name).serialize())
        self.status = "Game"

    def _get_infos(self):
        self.socket.send(
            game_data.ClientGetGameStateRequest(self.player_name).serialize()
        )

    def _discard(self, card: int):
        self.socket.send(
            game_data.ClientPlayerDiscardCardRequest(self.player_name, card).serialize()
        )

    def _play(self, card: int):
        self.socket.send(
            game_data.ClientPlayerPlayCardRequest(self.player_name, card).serialize()
        )

    def _give_hint(self, player: str, hint_type: Literal["color", "value"], hint):
        self.socket.send(
            game_data.ClientHintData(
                self.player_name, player, hint_type, hint
            ).serialize()
        )

    def _disconnect(self):
        self.socket.shutdown(2)

    def run(self) -> None:
        """Start the threads to manage the game"""

    def end(self) -> None:
        """Terminate all threads and close socket to finish the game"""
        self.socket.close()
