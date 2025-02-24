class Animal:
    def __init__(self, name, kind):
        self.name = name
        self.kind = kind
        self.treats_earned = 0  # Initialize treats count

    def speak(self):
        print(f"{self.name} the {self.kind} makes a sound.")

    def sit(self):
        self.treats_earned += 1
        print(f"{self.name} the {self.kind} sits and deserves a treat.")

    def giveTreat(self):
        if self.treats_earned > 0:
            self.treats_earned -= 1
            print(f"{self.name} the {self.kind} eats a treat. Still deserves {self.treats_earned} treats.")
        else:
            print(f"{self.name} the {self.kind} eats a treat. No treats left.")

class Bird(Animal):
	def takeFlight(self):
        	print(f"{self.name} the {self.kind} takes flight!")


# Creating objects
clyde = Animal("Clyde", "cat")
dave = Animal("Dave", "dog")
sam = Animal("Sam", "seal")
ben = Bird("Ben", "crow")

# Calling methods
clyde.speak()
dave.speak()
clyde.sit()
clyde.giveTreat()
sam.speak()
ben.takeFlight()
