import random,math
import matplotlib.pyplot as plt


class Player:
	def __init__(self, startingMoney):
		self.startingMoney = startingMoney
		self.balance = self.startingMoney
		self.inventory = []
		self.location = [0,0]

		self.doubles = False
		self.doubleCount = 0

		self.data = []
		self.propertyData = []
		self.dataGathered = False
		self.boughtProperties = []

	def move(self):
		self.doubles = False
		dice1 = random.randint(1,6)
		dice2 = random.randint(1,6)

		if dice1 == dice2: #if player threw doubles, roll again
			self.doubles = True
			self.doubleCount += 1

		if self.doubleCount == 3: #if player throws 3 doubles in a row, go to jail
			self.location = [1,0]

		diceRoll = dice1 + dice2

		#if players location[0] is over 10 it means he changes the side of the board he is on (board has 4 sides)
		if self.location[1] + diceRoll >= 10:
			self.location[0] += 1

			if self.location[0] == 4: #if the player crosses the start-square
				self.balance += 200
				self.location[0] = 0

			#move the player the appropriate amount on the new side that he is now on
			self.location[1] = (self.location[1] + diceRoll)%10

		else:
			self.location[1] += diceRoll

		if self.location == [3,0]: #go to jail square
			self.location = [1,0]

	def addMoney(self,amount):
		self.balance += amount
		#print("amount added:",amount)

	def removeMoney(self,amount):
		self.balance -= amount
		#print("amount removed:",amount)

	def addToInventory(self,property_):
		self.inventory.append(property_)

	def buyProperty(self,property_):
		#print("property bought")
		property_.changeOwner(self)
		self.removeMoney(property_.price)
		self.addToInventory(property_)
		self.boughtProperties.append(property_)

	def payRent(self,property_):
		propertyOwner = property_.owner			#owner of the property that is visited
		rent = property_.rent(propertyOwner)	#rent amount for that property
		self.removeMoney(rent)					#remove the rent amount from visiting player (this player)

		if self.hasLost():
			#if the paying player runs out of money, only add the players remaining amount of money to the propertyOwner
			propertyOwner.addMoney(rent + self.balance)

			#give all the properties to the player who eliminated this player
			for lostProperty in self.inventory:
				lostProperty.houses = 0
				lostProperty.changeOwner(propertyOwner)
				propertyOwner.addToInventory(lostProperty)
			self.inventory = []
		else:
			propertyOwner.addMoney(rent) 		#if the payer has enough money to pay, then add the rent to the propertyOwner

	#returns True if player has ran out of money and hence lost the game, else returns False
	def hasLost(self):
		if self.balance < 0:
			return True
		else:
			return False

	def printInventory(self):
		sortedInv = sorted(self.inventory, key=lambda x: x.color, reverse=True)
		for p in sortedInv: 
			print(p.color)

	def filterBoughtData(self):
		stationCount = 0
		data = [[],0] #data[0] is for property colors and data[1] is for number of stations
		for property_ in self.boughtProperties:
			if isinstance(property_,Property):
				if property_.ownsFullSet(self) and property_.color not in data[0]:
					data[0].append(property_.color)
			else:
				stationCount += 1

		data[1] = stationCount
		
		return data

	def dataCheck(self):
		for property_ in self.boughtProperties:
			if isinstance(property_,Property):
				if property_.ownsFullSet(self) and property_.color not in self.data:
					self.data.append(property_.color)




class Property:
	def __init__(self, name,color, price,housePrice, house0,house1,house2,house3,house4,hotel):
		self.name = name
		self.color = color

		self.price = price
		self.housePrice = housePrice

		self.house0 = house0
		self.house1 = house1
		self.house2 = house2
		self.house3 = house3
		self.house4 = house4
		self.hotel = hotel

		self.owner = None
		self.houses = 0

		self.sameSet = None


	def ownsFullSet(self,player):
		found = 0				#this gathers the count of found properties of the same color
		foundProperties = [] 	#this gathers the properties themselves
		for propertyOwned in player.inventory:
			if isinstance(propertyOwned,Property):
				if propertyOwned.color == self.color:
					found += 1
					foundProperties.append(propertyOwned)

				if self.color == "darkblue" or self.color == "brown": #these colors have only 2 properties
					if found == 2:
						self.sameSet = foundProperties
						return True
				else:
					if found == 3:
						self.sameSet = foundProperties
						return True

		return False

	#returns true if player has all the properties of this color else false.
	#so simply determines if a house can be bought on this property
	def canBuyHouse(self,player):

		#this method checks if given properties have the same amount or more houses than this property
		#if they have more houses than this, then a new house can be bought on this property
		def houseCountChecker(foundProperties):
			for property_ in foundProperties:
				if property_.houses < self.houses:
					return False

			if property_.houses < 5: #can't buy more than 5 houses
				return True
			else:
				return False

		found = 0				#this gathers the count of found properties of the same color
		foundProperties = [] 	#this gathers the properties themselves
		for propertyOwned in player.inventory:
			if isinstance(propertyOwned,Property):
				if propertyOwned.color == self.color:
					found += 1
					foundProperties.append(propertyOwned)

				if self.color == "darkblue" or self.color == "brown": #these colors have only 2 properties
					if found == 2:
						if player.balance >= self.housePrice:
							return houseCountChecker(foundProperties)
						else:
							return False
				else:
					if found == 3:
						if player.balance >= self.housePrice:
							return houseCountChecker(foundProperties)
						else:
							return False

		return False

	def buyHouse(self,player):
		if self.canBuyHouse(player):
			if player.balance >= self.housePrice:
				if self.houses < 5:
					player.removeMoney(self.housePrice)
					self.houses += 1

				else:
					print("You can't buy any more houses on this property!")
			else:
				print("You don't have enough money!")
		else:
			print("You need to have all the properties of this color before you can buy a house!")


	def changeOwner(self,player):
		self.owner = player

	def rent(self,player):
		match self.houses:
			case 0:
				if self.ownsFullSet(player):
					return self.house0*2
				else:
					return self.house0
			case 1:
				return self.house1
			case 2:
				return self.house2
			case 3:
				return self.house3
			case 4:
				return self.house4
			case 5:
				return self.hotel

class Station:
	owner = None
	def __init__(self,name,price):
		self.name = name
		self.price = price
		self.color = "station"


	def changeOwner(self,player):
		self.owner = player

	def rent(self,player):
		owned = 0 #gathers how many stations the given player owns
		for property_ in player.inventory:
			if isinstance(property_,Station):
				owned += 1

		match owned:
			case 0:
				return 0
			case 1:
				return 25
			case 2:
				return 50
			case 3:
				return 100
			case 4:
				return 200

class TaxSquare:
	def __init__(self,taxAmount):
		self.taxAmount = taxAmount

	def rent(self):
		return self.taxAmount

class Sattuma:
	def __init__(self):
		self.cards = [0,"prison",0,"pasila",-15,150,"start","erottaja",0,"hämeentie",-100,50,
									 "simonkatu",-100,0,"backwards3"]
		random.shuffle(self.cards)

	def draw(self,player,game):
		#helper function
		def propertyAction(currentLocation,currentPlayer):
			#check if the location is purchasable property
			if isinstance(currentLocation,Property) or isinstance(currentLocation,Station):

				if currentLocation.owner == None: 	#if the property is not owned, try to buy it
					if currentPlayer.balance >= currentLocation.price: #buy it if enough money
						currentPlayer.buyProperty(currentLocation)

				else: #if property is owned by another player, pay rent
					if currentLocation.owner != currentPlayer:
						currentPlayer.payRent(currentLocation)


			elif isinstance(currentLocation,TaxSquare): #if the location is tax-square, pay the tax
				currentPlayer.balance -= currentLocation.rent()

				#if the player runs out of money return all the players properties back to the game
				if currentPlayer.hasLost():
					for lostProperty in currentPlayer.inventory:
						if isinstance(lostProperty,Property): #(stations don't have houses)
							lostProperty.houses = 0
						lostProperty.changeOwner(None)

			elif isinstance(currentLocation, Sattuma):
				currentLocation.draw(currentPlayer,gameboard)

			elif isinstance(currentLocation,Yhteismaa):
				currentLocation.draw(currentPlayer)

			else: #else do nothing
				pass


		#draw a card
		card = self.cards.pop(random.randint(0, len(self.cards))-1)
		if isinstance(card,int):
			player.addMoney(card)
		else:
			match card:
				case "prison":
					player.location = [1,0]
				case "pasila":
					player.location = [0,5]
					player.addMoney(200)
					propertyAction(game.gameboard[player.location[0]][player.location[1]],player)
				case "start":
					player.location = [0,0]
					player.addMoney(200)
				case "erottaja":
					player.location = [3,9]
					propertyAction(game.gameboard[player.location[0]][player.location[1]],player)
				case "hämeentie":
					if player.location != [0,7]:
						player.addMoney(200)
					player.location = [1,1]
					propertyAction(game.gameboard[player.location[0]][player.location[1]],player)
				case "simonkatu":
					if player.location == [3,6]:
						player.addMoney(200)
					player.location = [2,4]
					propertyAction(game.gameboard[player.location[0]][player.location[1]],player)
				case "backwards3":
					match player.location:
						case [0,7]:
							player.location = [0,4]
							propertyAction(game.gameboard[player.location[0]][player.location[1]],player)
						case [2,2]:
							player.location = [1,9]
							propertyAction(game.gameboard[player.location[0]][player.location[1]],player)
						case [3,6]:
							player.location = [3,3]
							propertyAction(game.gameboard[player.location[0]][player.location[1]],player)
		
		if len(self.cards) == 0:
			self.reset()

	def reset(self):
		self.cards = [0,"prison",0,"pasila",-15,150,"start","erottaja",0,"hämeentie",-100,50,
									 "simonkatu",-100,0,"backwards3"]
		random.shuffle(self.cards)

class Yhteismaa:
	def __init__(self):
		self.cards = [100,"start","prison",-50,100,50,100,-50,200,10,10,20,-100,25,-100,0]
		random.shuffle(self.cards)

	def draw(self,player):
		card = self.cards.pop(random.randint(0, len(self.cards))-1)
		if isinstance(card,int):
			player.addMoney(card)
		else:
			if card == "start":
				player.location = [0,0]
				player.addMoney(200)

			elif card == "prison":
				player.location = [1,0]

			else:
				print("shouldnt be here")

		#if we run out of cards, shuffle the cards back in the pack
		if len(self.cards) == 0:
			self.reset()

	def reset(self):
		self.cards = [100,"start","prison",-50,100,50,100,-50,200,10,10,20,-100,25,-100,0]
		random.shuffle(self.cards)



class Board:
	def __init__(self):
		#def __init__(self, name,color, price,housePrice, house0,house1,house2,house3,house4,hotel)
		korkeavuorenkatu = Property("Korkeavuorenkatu","brown", 60,50, 2,10,30,90,160,250)
		kasarminkatu = Property("Kasarminkatu","brown", 60,50, 4,20,60,180,320,450)

		tulovero = TaxSquare(200)
		pasilanasema = Station("Pasilan asema",200)

		rantatie = Property("Rantatie","lightblue", 100,50, 6,30,90,270,400,550)
		kauppatori = Property("Kauppatori","lightblue", 100,50, 6,30,90,270,400,550)
		esplanadi = Property("Esplanadi","lightblue", 120,50, 8,40,100,300,450,600)

		hameentie = Property("Hämeentie","pink", 140,100, 10,50,150,450,625,750)
		siltasaari = Property("Siltasaari","pink", 140,100, 10,50,150,450,625,750)
		kaisaniemenkatu = Property("Kaisaniemenkatu","pink", 160,100, 12,60,180,500,700,900)

		sornaistenasema = Station("Sörnäisten asmea",200)

		liisankatu = Property("Liisankatu","orange", 180,100, 14,70,200,550,750,950)
		snellmanninkatu = Property("Snellmanninkatu","orange", 180,100, 14,70,200,550,750,950)
		unioninkatu = Property("Unioninkatu","orange", 200,100, 16,80,220,600,800,1000)

		lonnrotinkatu = Property("Lönnrotinkatu","red", 220,150, 18,90,250,700,875,1050)
		annankatu = Property("Annankatu","red", 220,150, 18,90,250,700,875,1050)
		simonkatu = Property("Simonkatu","red", 240,150, 20,100,300,750,925,1100)

		rautatieasema = Station("Rautatieasema",200)

		mikonkatu = Property("Mikonkatu","yellow", 260,150, 22,110,330,800,975,1150)
		aleksanterinkatu = Property("Aleksanterinkatu","yellow", 260,150, 22,110,330,800,975,1150)
		keskuskatu = Property("Keskuskatu","yellow", 280,150, 24,120,360,850,1025,1200)

		tehtaankatu = Property("Tehtaankatu","green", 300,200, 26,130,390,900,1100,1275)
		eira = Property("Eira","green", 300,200, 26,130,390,900,1100,1275)
		bulevardi = Property("Bulevardi","green", 320,200, 28,150,450,1000,1200,1400)

		tavaraasema = Station("Tavara-asema",200)

		mannerheimintie = Property("Mannerheimintie","darkblue", 350,200, 35,175,500,1100,1300,1500)
		lisavero = TaxSquare(100)
		erottaja = Property("Erottaja","darkblue", 400,200, 50,200,600,1400,1700,2000)

		#Creating the gameboard
		self.gameboard = [[],[],[],[]]

		self.gameboard[0].append(0) #start-square
		self.gameboard[0].append(korkeavuorenkatu)
		self.gameboard[0].append(Yhteismaa())
		self.gameboard[0].append(kasarminkatu)
		self.gameboard[0].append(tulovero)
		self.gameboard[0].append(pasilanasema)
		self.gameboard[0].append(rantatie)
		self.gameboard[0].append(Sattuma())
		self.gameboard[0].append(kauppatori)
		self.gameboard[0].append(esplanadi)

		self.gameboard[1].append(0)	#jail
		self.gameboard[1].append(hameentie)
		self.gameboard[1].append(0)
		self.gameboard[1].append(siltasaari)
		self.gameboard[1].append(kaisaniemenkatu)
		self.gameboard[1].append(sornaistenasema)
		self.gameboard[1].append(liisankatu)
		self.gameboard[1].append(Yhteismaa())
		self.gameboard[1].append(snellmanninkatu)
		self.gameboard[1].append(unioninkatu)

		self.gameboard[2].append(0) #free parking
		self.gameboard[2].append(lonnrotinkatu)
		self.gameboard[2].append(Sattuma())
		self.gameboard[2].append(annankatu)
		self.gameboard[2].append(simonkatu)
		self.gameboard[2].append(rautatieasema)
		self.gameboard[2].append(mikonkatu)
		self.gameboard[2].append(aleksanterinkatu)
		self.gameboard[2].append(0)
		self.gameboard[2].append(keskuskatu)

		self.gameboard[3].append(0) #go to jail
		self.gameboard[3].append(tehtaankatu)
		self.gameboard[3].append(eira)
		self.gameboard[3].append(Yhteismaa())
		self.gameboard[3].append(bulevardi)
		self.gameboard[3].append(tavaraasema)
		self.gameboard[3].append(Sattuma())
		self.gameboard[3].append(mannerheimintie)
		self.gameboard[3].append(lisavero)
		self.gameboard[3].append(erottaja)

if __name__ == "__main__":
	data = [[],[]]
	startMoney = 1500
	miss = 0
	percent = 0
################################################
	simAmount = 1000000
################################################
	colorDataTotal = {"brown":0,"lightblue":0,"pink":0,"orange":0,"red":0,"yellow":0,"green":0,"darkblue":0}
	colorDataWins = {"brown":0,"lightblue":0,"pink":0,"orange":0,"red":0,"yellow":0,"green":0,"darkblue":0}
	for _ in range(simAmount):

		if _%int(simAmount/10) == 0:
			percent += 10
			print(f"{percent}%")

		player1 = Player(startMoney)
		player2 = Player(startMoney)
		#player3 = Player(startMoney)
		#player4 = Player(startMoney)

		originalPlayers = [player1, player2]
		players = [player1, player2]

		game = Board()

		turn = 0
		draw = False
		while len(players) > 1:
			currentTurn = turn%len(players)
			currentPlayer = players[currentTurn]
			currentPlayer.move()
			currentLocation = game.gameboard[currentPlayer.location[0]][currentPlayer.location[1]]

			#check if the location is purchasable property
			if isinstance(currentLocation,Property) or isinstance(currentLocation,Station):

				if currentLocation.owner == None: 	#if the property is not owned, then try to buy it
					if currentPlayer.balance >= currentLocation.price: #buy it if enough money
						currentPlayer.buyProperty(currentLocation)

				else: #if property is owned by another player, pay rent
					if currentLocation.owner != currentPlayer:
						currentPlayer.payRent(currentLocation)


			elif isinstance(currentLocation,TaxSquare): #if the location is tax-square, pay the tax
				currentPlayer.balance -= currentLocation.rent()

				#if the player runs out of money return all the players properties back to the game
				if currentPlayer.hasLost():
					for lostProperty in currentPlayer.inventory:
						if isinstance(lostProperty,Property): #(stations don't have houses)
							lostProperty.houses = 0
						lostProperty.changeOwner(None)


			elif isinstance(currentLocation, Sattuma):
				currentLocation.draw(currentPlayer,game)

			elif isinstance(currentLocation,Yhteismaa):
				currentLocation.draw(currentPlayer)

			else:
				pass


			#every turn if it's possible to buy houses, the player buys them
			for property_ in currentPlayer.inventory:
				if isinstance(property_,Property):
					if property_.canBuyHouse(currentPlayer):
						property_.buyHouse(currentPlayer)

			#if player has lost, remove him from the game
			if currentPlayer.hasLost():
				players.remove(currentPlayer)

			if not currentPlayer.doubles or currentPlayer.doubleCount == 3:
				turn += 1
				currentPlayer.doubleCount = 0

			#end game if it lasts too long
			if turn >= 500:
				draw = True
				break

		if draw:
			pass
		else:

			for player in originalPlayers:
				player.dataCheck()
				#print(player.data)
				for color in player.data:
					colorDataTotal[color] += 1
			#print()
			winner = players[0]
			for color in winner.data:
				colorDataWins[color] += 1


	colorWinPercentages = {"brown":0,"lightblue":0,"pink":0,"orange":0,"red":0,"yellow":0,"green":0,"darkblue":0}

	for color in colorWinPercentages.keys():
		colorWinPercentages[color] = round((colorDataWins[color] / colorDataTotal[color])*100,2)


	colorWinPercentagesSorted = dict(sorted(colorWinPercentages.items(), key=lambda x:x[1],reverse=True))
	print(colorWinPercentagesSorted.items())


	#plt.bar(colorCountSorted.keys(), list(colorCountSorted.values()), align="center")
	plt.bar(colorWinPercentagesSorted.keys(), list(colorWinPercentagesSorted.values()), align="center")
	plt.title("If player got to buy the whole set, how likely was he to win")
	plt.xlabel("Sets")
	plt.ylabel("Win percent")
	plt.show()

	minValue = 999
	for value in colorWinPercentagesSorted.values():
		if value < minValue:
			minValue = value

	for color in colorWinPercentagesSorted.keys():
		colorWinPercentagesSorted[color] = colorWinPercentagesSorted[color] - minValue


	plt.bar(colorWinPercentagesSorted.keys(), list(colorWinPercentagesSorted.values()), align="center")
	plt.title("Same graph scaled by the smallest win percent")
	plt.show()