import scrapy
import json
import os
from scrapy.crawler import CrawlerProcess

# List of top cities
top_cities = [
    "Mont Saint Michel", "St Malo", "Bayeux", "Le Havre", "Rouen", "Paris", "Amiens", "Lille", "Strasbourg",
    "Chateau du Haut Koenigsbourg", "Colmar", "Eguisheim", "Besancon", "Dijon", "Annecy", "Grenoble", "Lyon",
    "Gorges du Verdon", "Bormes les Mimosas", "Cassis", "Marseille", "Aix en Provence", "Avignon", "Uzes",
    "Nimes", "Aigues Mortes", "Saintes Maries de la mer", "Collioure", "Carcassonne", "Ariege", "Toulouse",
    "Montauban", "Biarritz", "Bayonne", "La Rochelle"
]

BASE_URL = "https://www.booking.com/searchresults.html?ss={}"
OUTPUT_DIR = "src"
JSON_FILE = os.path.join(OUTPUT_DIR, "hotels.json")

# Check if directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Remove existing JSON file
if os.path.exists(JSON_FILE):
    os.remove(JSON_FILE)

# Define global list to store results
hotels_list = []

class BookingSpider(scrapy.Spider):
    name = "booking_spider"
    allowed_domains = ["booking.com"]

    def start_requests(self):
        """Generate search requests for each city."""
        headers = {"User-Agent": self.custom_settings["USER_AGENT"]}
        for city in top_cities:
            search_url = BASE_URL.format(city.replace(" ", "+"))
            yield scrapy.Request(url=search_url, callback=self.parse_search_results, headers=headers, meta={'city': city})

    def parse_search_results(self, response):
        """Extract hotel listings and follow details page."""
        for hotel in response.css("div[data-testid='property-card']"):
            hotel_name = hotel.css("div[data-testid='title']::text").get(default="No Name").strip()
            hotel_url = response.urljoin(hotel.css("a[data-testid='property-card-desktop-single-image']::attr(href)").get() or "")

            if hotel_url:
                yield response.follow(hotel_url, self.parse_hotel_details, meta={
                    "hotel_name": hotel_name,
                    "hotel_url": hotel_url,
                    "search_city": response.meta.get("city", "Unknown City")
                })

    def parse_hotel_details(self, response):
        """Extract detailed hotel information."""
        gps_data = response.css("a[data-atlas-latlng]::attr(data-atlas-latlng)").get()
        lat, lng = gps_data.split(",") if gps_data else (None, None)

        hotel_data = {
            "hotel_name": response.meta["hotel_name"],
            "hotel_url": response.meta["hotel_url"],
            "search_city": response.meta["search_city"],
            "rating": (response.css("div.a3b8729ab1.d86cee9b25::text").get() or "No Rating").strip(),
            "latitude": lat,
            "longitude": lng,
            "description": (response.css("p[data-testid='property-description']::text").get() or "No description").strip()
        }
        
        hotels_list.append(hotel_data)

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "LOG_LEVEL": "INFO"
    }

# Run the spider synchronously
process = CrawlerProcess()
process.crawl(BookingSpider)
process.start()

# Save the final result to JSON
with open(JSON_FILE, "w", encoding="utf8") as f:
    json.dump(hotels_list, f, ensure_ascii=False, indent=4)

# Print the JSON file path
print(f"Scraped data saved in {JSON_FILE}")
