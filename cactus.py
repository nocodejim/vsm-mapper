import random
import time

class Saguaro:
    """
    A class to represent the growth of a Saguaro cactus.
    
    The growth rates and arm development are based on general biological
    approximations for the Carnegiea gigantea.
    """
    def __init__(self):
        self.age = 0  # years
        self.height = 0.0  # inches
        self.arms = []  # list to hold arm lengths
        self.is_flowering = False

    def _get_growth_rate(self):
        """ Growth is very slow and varies with age. """
        if self.age <= 15:
            return random.uniform(0.5, 1.5)  # Very slow when young
        elif self.age <= 50:
            return random.uniform(2, 4)
        else:
            return random.uniform(1, 3) # Growth slows slightly in old age

    def grow(self, years=1):
        """ Simulates the cactus growing for a number of years. """
        for _ in range(years):
            self.age += 1
            self.height += self._get_growth_rate()

            # Saguaros typically start growing arms between 50 and 75 years old.
            if 50 <= self.age <= 100:
                # A small chance to grow a new arm each year.
                if random.random() < 0.1: # 10% chance
                    self.arms.append(0.1) # Add a new arm, starting at 0.1 ft

            # Arms also grow each year.
            for i in range(len(self.arms)):
                self.arms[i] += random.uniform(0.5, 1.5) # Arms grow slower than main trunk

            # Saguaros start flowering around age 35.
            if self.age >= 35:
                self.is_flowering = True


    def visualize(self):
        """ Creates a simple text-based visualization of the cactus. """
        print(f"Age: {self.age} years | Height: {self.height / 12:.2f} ft")
        
        # Display flowers at the top
        if self.is_flowering:
            print(" " * (int(self.height / 12) // 2) + "✿")

        # Display the main trunk
        trunk_height_scaled = max(1, int(self.height / 12))
        for i in range(trunk_height_scaled, 0, -1):
            segment = "|"
            
            # Add arms at appropriate heights
            # This is a simplified representation for visualization
            if len(self.arms) > 0 and i > trunk_height_scaled * 0.6:
                if len(self.arms) > 1 and i % 3 == 0:
                    segment = f"/{segment}\\"
                elif i % 2 == 0:
                    segment = f" {segment}/"
                else:
                    segment = f"\\{segment} "

            # The base becomes woody ("corking") with age
            if self.age > 80 and i < trunk_height_scaled * 0.2:
                segment = "#" # Use '#' to represent the tough, corked base

            print(" " * (int(self.height / 12) // 2) + segment)
        print("-" * (int(self.height / 12) + 2))
        print("\n")


# --- Simulation ---
my_saguaro = Saguaro()
target_age = 150 # Simulate until the cactus is 150 years old

print("--- Simulating Saguaro Growth ---")
time.sleep(2)

for year in range(target_age):
    my_saguaro.grow()
    if year % 10 == 0 or year == target_age - 1: # Display every 10 years
        print(f"\033[H\033[J") # Clears the console for a clean animation
        print("--- Simulating Saguaro Growth ---")
        my_saguaro.visualize()
        time.sleep(0.5)

print("Simulation complete. The saguaro has reached a mature age.")