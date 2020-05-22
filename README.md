# LAPS Pathfinding

The Pathfinding part of LAPS, by bachelor Group 7 at University of Southeast-Norway. These modules are developed and investigated as methods for doing pathfinding on drone flightpaths using machine learning. Using pathfinding algorithms for finding paths on big node graphs does not scale well and require significant resources and processing time, in addition to the paths found are not flyable without further processing, which requires tampering with the path so that it is no longer the most optimal path.

Machine learning is hopefully a solution to this problem, with our main goals being shorter processing time and cheaper with regards to processing resources, in addition to skipping the post-processing part of the path.

Each module has its own directory, with version directories inside. The modules are:
* **Dijkstra** - A Dijkstra implementation, which does not take turn-radius into account. Used for comparison and data generation.
* **DeepStar** - Convolutional Neural Network approach to pathfinding.
* **GraphStar** - A Graph Neural Network based approach to pathfinding
* **Ariel** - Reinforced Learning approach (hence the name, RL - Ariel).

## Built With
* [PyTorch](https://pytorch.org/) - Machine learning framework
* [Redis](https://redislabs.com/) - Used for API calls
