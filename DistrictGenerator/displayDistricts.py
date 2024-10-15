from generator import DistrictGenerator


'''
init generator
 1st parameter: State to be redistricted. Entered as lowercase state abbreviation
 2nd parameter: Standard deviation
     Note: The smaller the SD is, the closer districts are in population
 3rd parameter: Steps
     Note: A higher step number yields better results but also increases
           the amount of time the algorithm needs to run.
           It is not recommended to exceed 10,000 steps.
 4th parameter: Number of maps to display

Example:
  Generate district maps of Arizona with a deviation of 0.008 and a step size of 1000
  my_generator = DistrictGenerator("az", 0.008, 1000)
'''
my_generator = DistrictGenerator("az", 0.008, 1000, 3)

# generate districts
districts = my_generator.run()