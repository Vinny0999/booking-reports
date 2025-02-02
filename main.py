import datetime
from typing import List, Tuple


class Service:
    def __init__(self, name: str, departure_date: datetime.date):
        self.name = name
        self.departure_date = departure_date
        self.legs: List[Leg] = []
        self.ods: List[OD] = []

    @property
    def day_x(self):
        return (datetime.date.today() - self.departure_date).days

    @property
    def itinerary(self) -> List['Station']:
        if not self.legs:
            return []
        stations = [self.legs[0].origin]
        for leg in self.legs:
            stations.append(leg.destination)
        return stations

    def load_itinerary(self, itinerary: List['Station']) -> None:
        self.legs = []
        for i in range(len(itinerary) - 1):
            self.legs.append(Leg(self, itinerary[i], itinerary[i + 1]))

        self.ods = []
        for i in range(len(itinerary)):
            for j in range(i + 1, len(itinerary)):
                self.ods.append(OD(self, itinerary[i], itinerary[j]))

    def load_passenger_manifest(self, passengers: List['Passenger']) -> None:
        for od in self.ods:
            od.passengers = []
        
        for passenger in passengers:
            matching_od = next(
                od for od in self.ods 
                if od.origin == passenger.origin and od.destination == passenger.destination
            )
            matching_od.passengers.append(passenger)

class Station:
    def __init__(self, name: str):
        self.name = name

class Leg:
    def __init__(self, service: Service, origin: Station, destination: Station):
        self.service = service
        self.origin = origin
        self.destination = destination

    @property
    def passengers(self) -> List['Passenger']:
        all_passengers = []
        for od in self.service.ods:
            if self in od.legs:
                all_passengers.extend(od.passengers)
        return all_passengers

class OD:
    def __init__(self, service: Service, origin: Station, destination: Station):
        self.service = service
        self.origin = origin
        self.destination = destination
        self.passengers: List[Passenger] = []

    @property
    def legs(self) -> List[Leg]:
        itinerary = self.service.itinerary
        origin_index = itinerary.index(self.origin)
        destination_index = itinerary.index(self.destination)
        return self.service.legs[origin_index:destination_index]

    def history(self) -> List[List]:
        if not self.passengers:
            return []
        
        sorted_passengers = sorted(self.passengers, key=lambda p: p.sale_day_x)
        
        history = []
        current_bookings = 0
        current_revenue = 0.0
        current_day = None
        
        for passenger in sorted_passengers:
            if passenger.sale_day_x != current_day:
                if current_day is not None:
                    history.append([current_day, current_bookings, current_revenue])
                current_day = passenger.sale_day_x
            current_bookings += 1
            current_revenue += passenger.price
        
        if current_day is not None:
            history.append([current_day, current_bookings, current_revenue])
        
        return history

class Passenger:
    def __init__(self, origin: Station, destination: Station, sale_day_x: int, price: float):
        self.origin = origin
        self.destination = destination
        self.sale_day_x = sale_day_x
        self.price = price

def max_path_finder(matrix: List[List[int]]) -> Tuple[int, List[Tuple[int, int]]]:
    if not matrix or not matrix[0]:
        return (0, [])
    
    rows, cols = len(matrix), len(matrix[0])
    
    dp = [[0] * cols for _ in range(rows)]
    path = [[None] * cols for _ in range(rows)]
    
    dp[0][0] = matrix[0][0]
    
    for j in range(1, cols):
        dp[0][j] = dp[0][j-1] + matrix[0][j]
        path[0][j] = (0, j-1)
    
    for i in range(1, rows):
        dp[i][0] = dp[i-1][0] + matrix[i][0]
        path[i][0] = (i-1, 0)
    
    for i in range(1, rows):
        for j in range(1, cols):
            if dp[i-1][j] > dp[i][j-1]:
                dp[i][j] = dp[i-1][j] + matrix[i][j]
                path[i][j] = (i-1, j)
            else:
                dp[i][j] = dp[i][j-1] + matrix[i][j]
                path[i][j] = (i, j-1)
    
    current = (rows-1, cols-1)
    final_path = [current]
    while path[current[0]][current[1]] is not None:
        current = path[current[0]][current[1]]
        final_path.append(current)
    
    return (dp[rows-1][cols-1], list(reversed(final_path)))