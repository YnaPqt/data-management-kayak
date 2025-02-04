import scrapy
import json
import os
from scrapy.crawler import CrawlerProcess

# List of cities to search for hotels

CITIES = [
    "Mont Saint Michel", "St Malo", "Bayeux", "Le Havre", "Rouen", "Paris", "Amiens", "Lille", "Strasbourg", 
    "Chateau du Haut Koenigsbourg", "Colmar", "Eguisheim", "Besancon", "Dijon", "Annecy", "Grenoble", "Lyon", 
    "Gorges du Verdon", "Bormes les Mimosas", "Cassis", "Marseille", "Aix en Provence", "Avignon", "Uzes", 
    "Nimes", "Aigues Mortes", "Saintes Maries de la mer", "Collioure", "Carcassonne", "Ariege", "Toulouse", 
    "Montauban", "Biarritz", "Bayonne", "La Rochelle"
]

BASE_URL = "https://www.booking.com/searchresults.html?ss={}"
OUTPUT_DIR = "src"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "hotels.json")

# Ensure output directory exists and create if it doesn’t exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Remove existing JSON file
if os.path.exists(OUTPUT_FILE):
    os.remove(OUTPUT_FILE) 

class BookingSpider(scrapy.Spider):
    name = "booking_spider"
    allowed_domains = ["booking.com"] #Restrict scraping to Booking.com

    """The User-Agent and the cities are defined in the start_requests so BookingSpider 
    generate it's own requests in case of multiple spiders in the same project. This makes the spider remains flexible,reusable and modular"""
    
    def start_requests(self):
        """Generate search URLs for each city."""
        headers = {"User-Agent": self.custom_settings["USER_AGENT"]}
        for city in CITIES:
            search_url = BASE_URL.format(city.replace(" ", "+"))
            yield scrapy.Request(url=search_url, callback=self.parse_search_results, headers=headers, meta={'city': city})

    def parse_search_results(self, response):
        """Extract hotel links and follow them."""
        for hotel in response.css("div[data-testid='property-card-container']"):
            hotel_name = hotel.css("div[data-testid='title']::text").get("No Name").strip()
            hotel_url = hotel.css("a[data-testid='title-link']::attr(href)").get()
            
            if hotel_url: #Ensure hotel URL exists before proceeding
                yield response.follow(hotel_url, self.parse_hotel_details, meta={
                    "hotel_name": hotel_name,
                    "hotel_url": response.urljoin(hotel_url),
                    "search_city": response.meta['city'] #Pass city name for reference
                })

    def parse_hotel_details(self, response):
        """Extract detailed hotel information."""
        gps_data = response.css("a[data-atlas-latlng]::attr(data-atlas-latlng)").get()
        lat, lng = gps_data.split(",") if gps_data else (None, None) #Split coordinates or set None
        
        hotel_data = {
            "hotel_name": response.meta["hotel_name"],
            "hotel_url": response.meta["hotel_url"],
            "search_city": response.meta["search_city"],
            "rating": response.css("div.a3b8729ab1.d86cee9b25::text").get("No Rating").strip(),
            "latitude": lat,
            "longitude": lng,
            "description": response.css("p[data-testid='property-description']::text").get("No description").strip()
        }
        
        self.save_data(hotel_data) #Call method to save data

    def save_data(self, data):
        """Save extracted data into JSON file efficiently."""
        try:
            with open(OUTPUT_FILE, "a", encoding="utf-8") as file: #Open file in append mode
                file.write(json.dumps(data, ensure_ascii=False) + "\n") #Append JSON object as a new line
        except Exception as e:
            self.logger.error(f"Error saving data: {e}") # Log error if something goes wrong

    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "LOG_LEVEL": "INFO"
    }

# Run the spider
process = CrawlerProcess()
process.crawl(BookingSpider)
process.start()
