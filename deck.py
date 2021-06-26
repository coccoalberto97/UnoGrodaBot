#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Telegram bot to play UNO in group chats
# Copyright (c) 2016 Jannes Höke <uno@jhoeke.de>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.


import operator
from player import Player
from random import shuffle
import logging
import json

import card as c
from card import Card
from errors import DeckEmptyError


class Deck(object):
    """ This class represents a deck of cards """

    def __init__(self):
        self.cards = list()
        self.graveyard = list()
        self.logger = logging.getLogger(__name__)
        self.current_decks = 1
        self.logger.debug(self.cards)

    def player_joined(self, players: list, game_started: bool):
        # attrs = vars(players) variabili di un oggetto per print
        # ', '.join(map(str, players)) stringify della classe e concateno separato da ,
        # ogni 10 giocatori aggiungo un mazzo
        decks: int = int(len(players)//11)

        if decks > self.current_decks:
            self.current_decks = decks
            ##se il gioco è iniziato creo un mazzo lo mischio e lo aggiungo al pool delle carte
            if game_started:
                self.logger.info("aggiungo un mazzo, mazzi correnti %d ", self.current_decks)
                new_deck = self.add_deck()
                self.shuffle(new_deck)
                self.cards.extend(new_deck)
                self.logger.info("carte correnti %d ", len(self.cards))


    def add_deck(self):
        """Add one Deck to the card Pool"""
        self.logger.debug("Adding Deck")
        cards: list = list()
        for color in c.COLORS:
            for value in c.VALUES:
                    cards.append(Card(color, value))
                    if not value == c.ZERO:
                        cards.append(Card(color, value))
            for special in c.SPECIALS:
                for _ in range(4):
                    cards.append(Card(None, None, special=special))  

        return cards;    


    def shuffle(self, cards: list):
        """Shuffles the deck"""
        self.logger.debug("Shuffling Deck")
        shuffle(cards)

    def draw(self):
        """Draws a card from this deck"""
        try:
            card = self.cards.pop()
            self.logger.debug("Drawing card " + str(card))
            return card
        except IndexError:
            if len(self.graveyard):
                while len(self.graveyard):
                    self.cards.append(self.graveyard.pop())
                self.shuffle()
                return self.draw()
            else:
                raise DeckEmptyError()

    def dismiss(self, card):
        """Returns a card to the deck"""
        self.graveyard.append(card)

    def _fill_classic_(self):
        # Fill deck with the classic card set

        self.logger.info("_fill_classic_")
        self.cards.clear()

        self.logger.info("Giochiamo con %d mazzi", self.current_decks)
        for index in range(self.current_decks):
            self.cards.extend(self.add_deck())  
            self.logger.info("Aggiunto mazzo numero %d", index)
             
        self.logger.info("Mischio tutto")
        self.shuffle(self.cards)

    def _fill_wild_(self):
        # Fill deck with a wild card set
        self.cards.clear()
        for color in c.COLORS:
            for value in c.WILD_VALUES:
                for _ in range(4):
                    self.cards.append(Card(color, value))
        for special in c.SPECIALS:
            for _ in range(6):
                self.cards.append(Card(None, None, special=special))
        self.shuffle()
