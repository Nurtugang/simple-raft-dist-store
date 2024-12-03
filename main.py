from store import RaftDistributedStore

from pycountry import countries 
import time

if __name__ == "__main__":

    countries_set = set(countries)

    store = RaftDistributedStore(num_nodes=3)
    
    try:
        while countries_set is not None:
            country = countries_set.pop()
            store.put(country.alpha_3, country.name)

            time.sleep(2)

    except KeyboardInterrupt:
        print("Simulation stopped.")
