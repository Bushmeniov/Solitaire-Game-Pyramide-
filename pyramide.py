from PyQt5 import QtCore, QtGui, QtWidgets
import os,random

class PyramideCard(QtWidgets.QLabel):

	card_suits = ['♠', '♥', '♦', '♣']
	card_ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'B', 'D', 'K']
	card_values = {rank: value for value, rank in enumerate(card_ranks, 1)}

	def __init__(self,rank,suit):
		#----------------Backend_data---------------------
		self.__suit = suit
		self.__rank = rank
		self.__value = PyramideCard.card_values[rank]

		# ----------------State-------------------------
		self.visible = False # if true we see card else we see BackGround

		#----------------Visual_parameters----------------
		QtWidgets.QLabel.__init__(self)
		self.setGeometry(QtCore.QRect(0, 0, 100, 150))
		self.setObjectName(self.__rank + self.__suit)
		self.setStyleCSS()

		#-----------RELATIONSHIPS-----------------
		self.parents=[]
		self.childs=[]

	def getVal(self):
		return self.__value

	def setStyleCSS(self):
		if self.visible :
			self.setStyleSheet(
				"QLabel{{background-image: url({});border-radius:60px;overflow:hidden;background-color: transparent !important }}".format(
					'./pack/' + self.__rank + self.__suit+'.png'))

		else :
			self.setStyleSheet(
				"QLabel{{background-image: url({});border-radius:60px;overflow:hidden;background-color: transparent !important }}".format(
					'./pack/back.png' ))

	def change_visible(self):
		if self.visible :
			self.visible = False
			self.setStyleCSS()
		else :
			self.visible = True
			self.setStyleCSS()

	def is_visible(self):
		return True if self.visible else False

	def __str__(self):
		return self.__rank + self.__suit

	def __add__(self, other):
		return self.__value + other.__value

class PyramideDeckIterator():
	'''
	Iterator class
	'''
	def __init__(self,deck):
		self.deck=deck
		self.currentIndex = 0

	def currentIndexChange(self,refresh=0):
		'''
		doing new circle -> Index = 0
		:param refresh:  if 1 -> currentIndex=0
		:change: increase index +1
		'''
		self.currentIndex=(self.currentIndex+1)*(1-refresh)

	def nextCard(self):
		'''
		:return: next card or current card
		'''

		try :
			self.currentIndexChange()
			return self.deck.cards[self.currentIndex]
		except IndexError:

			self.currentIndexChange(refresh=1)
			return self.deck.cards[self.currentIndex]


	def removedCard__(self):
		#importand for our indexing afteer removing card from the deck
		self.currentIndex-=1


class MinikenCard(QtWidgets.QLabel):
	#signalChangeDeckCard = QtCore.pyqtSignal()
	def __init__(self,cards,iteratorClassReference):

		# ----------------Visual_parameters----------------
		QtWidgets.QLabel.__init__(self)
		self.setGeometry(QtCore.QRect(0, 0, 100, 150))
		self.setObjectName("DeckCard")

		self.setStyleSheet("QLabel{{background-image: url({});border-radius:60px;overflow:hidden;background-color: transparent !important }}".format(
			'./pack/back.png'))

		#list of cards in Deck
		self.cards=cards

		self.iterator = self.createIterator(iteratorClassReference)
		# we see it near the Deck on the board
		self.activeCard = self.cards[0]
		self.tune_visible_parameters()
		#self.tune_corners()


	def tune_visible_parameters(self):
		for i in range(1,len(self.cards)):
			self.cards[i].setVisible(False) # hide
			self.cards[i].change_visible() # to back

		self.activeCard.change_visible()


	def get_deckCard(self):
		return self.activeCard

	def createIterator(self,iteratorClassReference):
		'''create object of Deck iterator'''
		return iteratorClassReference(self)

	def takeNextCard(self):
		'''iterator generate for us the next card'''
		return self.iterator.nextCard()

	def changeActiveCard(self):
		if self.activeCard.isVisible():
			self.activeCard.setVisible(False)
		if not self.isCardsInDeck():
			self.activeCard=self.takeNextCard()
			self.activeCard.setVisible(True)
			return 1


	def isCardsInDeck(self):
		return True if not self.cards else False


	def playDeckCard(self):
		'''
		pop played card from the deck
		may be it must work  with QtSignal (Player took this activate card
		and it give 13 with another card )
		or
		this two cards must be deleted in the strategy interface
		'''
		self.cards.remove(self.activeCard)
		#"signal" to classIterator
		self.iterator.removedCard__()


class PyramideCardsCreator() :
	'''create cards fpr Pyramide game'''
	def __init__(self,cls_card):
		#cls card reference
		self.cls_card=cls_card

	def create_cards_for_game(self) -> list :
		'''
		:return: list of all the game cards
		'''
		suits = self.cls_card.card_suits
		ranks = self.cls_card.card_ranks

		return [ self.cls_card(rank,suit)
				 	for suit in suits
				 		for rank in ranks ]

	def optional_components(self):
		'''
		:return: tuple(deck_cards,playing_layers-cards in the field)
		'''
		cards = self.create_cards_for_game()
		random.shuffle(cards)

		playing_cards = cards[:28]
		deck_cards = cards[28:]

		pyramide_layers = self.createPiramideCardsLayers(playing_cards)

		pyramide_layers_with_relationships=self.createrelationships(pyramide_layers)
		return deck_cards,pyramide_layers_with_relationships

	def createrelationships(self,pyramide_layers):
		'''
		:param pyramide_layers: our playing cards layers
		:return: Same structure with additionals relationships attributes in CardObjects
		'''
		pyramideLayers=pyramide_layers.copy()
		pyramideLayers.reverse()
		num_layers=len(pyramide_layers)
		for n_layer in range(num_layers-1):
			for n_card in range(len(pyramideLayers[n_layer])):
				child1=pyramideLayers[n_layer + 1][n_card]
				child2=pyramideLayers[n_layer + 1][n_card + 1]
				pyramideLayers[n_layer][n_card].childs.append(child1)
				pyramideLayers[n_layer][n_card].childs.append(child2)
				child1.parents.append(pyramideLayers[n_layer][n_card])
				child2.parents.append(pyramideLayers[n_layer][n_card])
		pyramideLayers.reverse()
		return pyramide_layers

	def createPiramideCardsLayers(self,cards):
		'''
		emit from optional_components
		:param cards: all cards in the game
		:return: list of card in the field : [[0],[0,1]..[0,1,2,4,5]]
		'''
		f = 0
		playing_layers = []
		for layer in range(6, -1, -1):
			playing_layers.append(cards[f:f + layer + 1])
			f += layer + 1
		return playing_layers

class ScoreLabel(QtWidgets.QLabel):

	def __init__(self):

		# ----------------Visual_parameters----------------
		QtWidgets.QLabel.__init__(self)
		self.setGeometry(QtCore.QRect(0, 0, 145, 40))
		self.setObjectName("ScoreLabel")
		self.setFont(QtGui.QFont('SansSerif', 16))
		self.setStyleSheet("QLabel{overflow:hidden;background-color: transparent !important; }")

		self.score = 0
		text = f"<font color='white'>Score &nbsp;&nbsp;-> {self.score}</font>"
		self.setText(text)

	def add1(self):
		self.score+=1
		text = f"<font color='white'>Score &nbsp;&nbsp;-> {self.score}</font>"
		self.setText(text)

	def get_score(self):
		return self.score


class HighScoreLabel(QtWidgets.QLabel):
	def __init__(self):

		# ----------------Visual_parameters----------------
		QtWidgets.QLabel.__init__(self)
		self.setGeometry(QtCore.QRect(0, 0, 145, 40))
		self.setObjectName("HighScoreLabel")
		self.setFont(QtGui.QFont('SansSerif', 16))
		self.setStyleSheet("QLabel{overflow:hidden;background-color: transparent !important; }")
		self.best_score=self.get_best_score()
		self.setText(f"<font color='white'>Record -> {self.best_score}</font>")

	def save_score(self,new_score):
		if new_score<self.best_score:
			file=open("pack/best_score.txt","w+")
			file.write(str(new_score))
			file.close()

	def get_best_score(self):
		file=open("pack/best_score.txt","r")
		best_score=int(file.read())
		file.close()
		return best_score




class PyramideScene(QtWidgets.QGraphicsScene):
	EndGameSignal = QtCore.pyqtSignal()
	def __init__(self):
		QtWidgets.QGraphicsScene.__init__(self)
		#------------------------scene_parameters----------------------
		self.setBackgroundBrush(QtGui.QColor(92,117,97,alpha = 255))
		self.setSceneRect(0, 150, 995, 650)
		self.addRect(self.sceneRect())
		#---------------------fill_scene------------------
		self.__init_objects()


	def __init_objects(self):
		#------------------------creating_cards_backend-------------
		CardsCreatorObj=PyramideCardsCreator(PyramideCard)
		self.deck_cards, self.pyramide_layers = CardsCreatorObj.optional_components()

		# ------------------------adding_cards_to_the_scene_VISUAL-------------
		# put all the playing cards on the scene
		self.put_playing_cards()
		# put Deck card on the scene and DeckEmulator
		# see put_Deck_cards where maniken_card creates .
		# deck it's child widget of QGraphicsProxyWidget of maniken_card
		self.maniken_card,self.deck=self.put_Deck_cards()

		# -----------ACTIVATIONS_FLAGS--------------------
		self.current_card=0
		self.current_card_old_pos=0
		#--------------game over ---------------
		self.__img_end_game = os.path.join(r"pack\ground")
		#-----------------restart------------------------
		self.__img_restart=os.path.join(r"pack\restart")
		self.res_img=self.addPixmap(QtGui.QPixmap(self.__img_restart))
		self.res_img.setOffset(10,680)
		#---------------------Score Labels--------------------
		self.score_label = self.addWidget(ScoreLabel())
		self.score_label.setPos(800,155)
		self.score_widget=self.score_label.widget()

		self.record_score_label = self.addWidget(HighScoreLabel())
		self.record_score_label.setPos(800,200)
		self.record_score_widget=self.record_score_label.widget()


	def opening_next_card(self,action_item):
		'''
		after each deleting item we check state of the game
		and make visible parent if parent haven't any child
		:param action_item: item to delete
		'''
		if not action_item.widget().parents:
			self.game_over()
			return 1


		for parent in action_item.widget().parents:
			parent.childs.remove(action_item.widget())

			if not parent.childs:
				parent.change_visible()

	def restart(self):
		# restart scene
		self.clear()
		self.__init_objects()

	def game_over(self):

		score=self.score_widget.get_score()
		self.record_score_widget.save_score(score)
		# Phone photo
		self.addPixmap(QtGui.QPixmap(self.__img_end_game))
		finish_label=QtWidgets.QLabel()
		finish_label.setGeometry(QtCore.QRect(0, 0, 400, 150))
		finish_label.setFont(QtGui.QFont('SansSerif', 30))
		finish_label.setStyleSheet("QLabel{overflow:hidden;background-color: transparent !important; }")
		finish_label.setText(f"<font color='white'>Congratulations !<br>Your score is {score} ;)</font>")
		self.finish_label=self.addWidget(finish_label)
		self.finish_label.setPos(100,200)

		self.EndGameSignal.emit()


	def mousePressEvent(self, event):

		if event.button() == QtCore.Qt.LeftButton:
			scenePos = event.scenePos()
			items = self.items(scenePos)
			if not items:
				return
			clked_item=items[0]


			if isinstance(clked_item,QtWidgets.QGraphicsProxyWidget):
				if isinstance(clked_item.widget(),PyramideCard) and clked_item.widget().is_visible():

					if self.current_card :

						if self.current_card.widget()+clked_item.widget() == 13 :

							self.removeItem_(self.current_card)
							self.removeItem_(clked_item)
							self.score_widget.add1()

						else:
							self.deactivate_active_card_pos()
							self.current_card=0

					else :
						# if we have a king
						if clked_item.widget().getVal()==13:

							self.removeItem_(clked_item)
							self.score_widget.add1()
						else :
							self.current_card=clked_item
							self.activate_card(clked_item)
				elif  isinstance(clked_item.widget(),MinikenCard):
					self.clicked_ManikenCard()
					self.score_widget.add1()
				else :
					return
			elif isinstance(clked_item,QtWidgets.QGraphicsPixmapItem):
				self.restart()
			else:
				return

	def removeItem_(self,item):
		if item.widget()==self.deck.get_deckCard():
			self.removeDeckItem(item)
		else :
			self.removeFieldItem(item)

	def removeFieldItem(self,item):
		'''remove Item from the Piramide Field'''
		if self.opening_next_card(item): # if return 1 -> Gameover() -> mustn't do next action
			return

		self.removeItem(item)

	def removeDeckItem(self,item):
		'''Remove item from the deck'''
		self.deck.playDeckCard()

		if not self.deck.changeActiveCard():
			self.removeItem(self.maniken_card)

		self.removeItem(item)

	def clicked_ManikenCard(self):
		'''if we clicked on our Deck to change card'''
		if self.current_card:
			self.deactivate_active_card_pos()
			self.current_card = 0

		if not self.deck.changeActiveCard():
			self.removeItem(self.maniken_card)


	def put_Deck_cards(self):
		#creating deck emulator
		self.maniken_card = self.addWidget(MinikenCard(self.deck_cards, PyramideDeckIterator))
		self.maniken_card.setPos(30, 200)

		#adding playing cards to the pyramide
		for card in self.maniken_card.widget().cards:
			card_=self.addWidget(card)
			card_.setPos(135,200)
		#make deck card visible

		return self.maniken_card,self.maniken_card.widget()

	def deactivate_active_card_pos(self):
		self.current_card.setPos(self.current_card_old_pos)

	def activate_card(self,card):

		'''simulating activating the card'''
		card_pos=card.pos()
		self.current_card_old_pos=card_pos
		card.setPos(card_pos.x(),card_pos.y()+8)


	def put_playing_cards(self):

		layers =self.pyramide_layers

		# make the firs layer visible
		for card in layers[0]:
			card.change_visible()
		# starter point to put card in the field
		starter_x=635
		starter_x=560
		for layer in range(len(layers),-1,-1) :
			layer_length=7-layer
			starter_X = starter_x
			for card in range(layer_length) :
				card_in_the_field=self.addWidget(layers[layer][card])
				card_in_the_field.setPos(starter_X-(layer_length-card)*100,(layer_length+1)*80)
				starter_X+=12
			starter_x+=50

class Game(QtWidgets.QWidget):
	def __init__(self):
		QtWidgets.QWidget.__init__(self)
		self.setWindowTitle("Pyramide")
		self.setObjectName('MainWidget')
		self.setStyleSheet('''
				            #MainWidget {
		                background-color: #253;}   
		            ''')

		# parameters QWIndowWIdget

		self.setFixedSize(1030, 685)

		self.setLayout(self.Initialization())


	def Initialization(self):
		layout = QtWidgets.QGridLayout()

		self.PyramideView = QtWidgets.QGraphicsView()
		self.PyramideView.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
		layout.addWidget(self.PyramideView)
		self.PyramideScene = PyramideScene()
		self.PyramideView.setScene(self.PyramideScene)
		#parameters PyramideView
		self.PyramideView.setFixedSize(1000, 655)
		self.PyramideView.setRenderHints(QtGui.QPainter.Antialiasing)

		self.PyramideScene.EndGameSignal.connect(self.handler_EndGameSignal)
		return layout

	@QtCore.pyqtSlot()
	def handler_EndGameSignal(self):

		res = QtWidgets.QMessageBox.question(self, f"You won!", "Restart ? ",
											 QtWidgets.QMessageBox.Yes |
											 QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.Yes)
		if res == QtWidgets.QMessageBox.Yes:
			self.PyramideScene.restart()
		else:
			self.close()


def main():
	import sys
	app = QtWidgets.QApplication(sys.argv)
	Pyramide = Game()
	Pyramide.show()
	sys.exit(app.exec_())

if __name__ == '__main__':
	main()
