Here is the manual for interactions with airfrance.us

```search_lowest_fares
location_page: airfrance.us/search/flights/0
type: Flight search request
visual_element: Flight search form
trigger: Search submission with booking flow parameter
request: POST https://wwws.airfrance.us/gql/v1?bookingFlow=LEISURE
arguments: {
  "operationName": "SharedSearchLowestFareOffersForSearchQuery",
  "variables": {
    "lowestFareOffersRequest": {
      "bookingFlow": "LEISURE",
      "withUpsellCabins": true,
      "passengers": [
        {
          "id": 1,
          "type": "$passenger_type"
        }
      ],
      "commercialCabins": ["$cabin_class"],
      "fareOption": null,
      "type": "DAY",
      "requestedConnections": [
        {
          "departureDate": "$departure_date",
          "dateInterval": "$date_range",
          "origin": {
            "type": "CITY",
            "code": "$origin_city_code"
          },
          "destination": {
            "type": "CITY", 
            "code": "$destination_city_code"
          }
        }
      ]
    },
    "activeConnection": 0,
    "searchStateUuid": "$search_session_uuid",
    "bookingFlow": "LEISURE"
  },
  "extensions": {
    "persistedQuery": {
      "version": 1,
      "sha256Hash": "8dc693945bf8eadc1d5c80d2f3c82ce4b3f869b27e04ad356afb22516a1559e6"
    }
  }
}
effect: Displays available flight options with pricing across date range
returns: JSON with flight dates, prices, promo fares, and booking links
viewport_effect: Updates search results section with flight grid
example_return: {
  "data": {
    "lowestFareOffers": {
      "lowestOffers": [
        {
          "flightDate": "2025-07-29",
          "displayPrice": 729,
          "totalPrice": 729,
          "isPromoFare": true,
          "promoFareTitle": "Promo fare",
          "currency": "USD"
        }
      ]
    }
  }
}
```

```search_flights
location_page: airfrance.us/search/flights/0
type: Flight details request
visual_element: Flight selection interface
trigger: Click/select specific flight from search results
request: POST https://wwws.airfrance.us/gql/v1?bookingFlow=LEISURE
arguments: {
  "operationName": "SearchResultAvailableOffersQuery",
  "variables": {
    "activeConnectionIndex": 0,
    "bookingFlow": "LEISURE",
    "availableOfferRequestBody": {
      "commercialCabins": ["$cabin_class"],
      "passengers": [
        {
          "id": 1,
          "type": "$passenger_type"
        }
      ],
      "requestedConnections": [
        {
          "origin": {
            "code": "$origin_city_code",
            "type": "CITY"
          },
          "destination": {
            "code": "$destination_city_code",
            "type": "CITY"
          },
          "departureDate": "$departure_date"
        }
      ],
      "bookingFlow": "LEISURE"
    },
    "searchStateUuid": "$search_session_uuid"
  },
  "extensions": {
    "persistedQuery": {
      "version": 1,
      "sha256Hash": "5e6d73b6a1ba669269753a37a79e053e95f43e41da72a2833d12fc81d36e7e24"
    }
  }
}
effect: Displays detailed flight options with cabin classes and pricing
returns: JSON with complete flight itineraries, segments, aircraft details, and upsell options
viewport_effect: Updates flight details section with expanded flight information
example_return: {
  "data": {
    "availableOffers": {
      "offerItineraries": [
        {
          "activeConnection": {
            "segments": [
              {
                "marketingFlight": {
                  "carrier": {"code": "AF"},
                  "number": "0011"
                },
                "equipmentName": "Airbus A350-900",
                "origin": {"code": "JFK", "name": "John F. Kennedy International Airport"},
                "destination": {"code": "CDG", "name": "Paris-Charles de Gaulle airport"},
                "departureDateTime": "2025-07-29T01:00:00",
                "arrivalDateTime": "2025-07-29T14:15:00"
              }
            ]
          },
          "upsellCabinProducts": [
            {
              "connections": [
                {
                  "cabinClass": "PREMIUM",
                  "price": {"amount": 729, "currencyCode": "USD"},
                  "isPromo": true,
                  "promoTitle": "Promo fare"
                }
              ]
            }
          ]
        }
      ]
    }
  }
}
```