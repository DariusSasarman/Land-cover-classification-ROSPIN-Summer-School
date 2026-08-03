Tech Approach:
 1. Mixture of Experts : we train models to specifically recognize a type of land and allow a "router" to decide which one's good for the task at hand
 2. Ensemble learning : separating models based on land types might leave out correlations between said types (i.e. Roads are usually parallel with rivers)
                         => several "mixed" models + pure "concentrated" models + weighted voting mechanism.

Business:
 1. Expansion of cities : we could time-series analyze the evolution of several cities. 
 Based on this we could identify which "free/green" land types would become city territories in the future.
 We could scrape old transactions and train our model to generate an expected ROI.
 2. Infrastructure demand forecasting : same principle, but adapted towards official authorities.
