# **📍 Place Wrapper Service**
A FastAPI-based microservice that integrates with the **Google Places API**, normalizes responses, caches results in **Redis**, and forwards data to a **Recommendation Service**.

---

## **🌟 Table of Contents**
- [Overview](#-overview)
- [Architecture](#-architecture)
- [Technologies Used](#-technologies-used)
- [Setup & Installation](#-setup--installation)
- [Environment Variables](#-environment-variables)
- [API Endpoints](#-api-endpoints)
- [Data Flow](#-data-flow)
- [Next Steps](#-next-steps)

---

## **📌 Overview**
The **Place Wrapper Service** serves as an intermediary between:
1. **Google Places API** (fetches places based on location & keyword).
2. **Recommendation Service** (processes normalized data).

### **🔹 Features**
✔ Fetches **places** from Google API  
✔ **Normalizes** API responses into a consistent format  
✔ Uses **Redis** caching to improve performance  
✔ **Forwards data** to the Recommendation Service  

---

## **🔼 Architecture**
```plaintext
User → Place Wrapper → Google Places API
                        ↓
                   Normalize Data
                        ↓
                    Cache in Redis
                        ↓
       Forward Data → Recommendation Service
```

### **🛠️ Service Components**
- **FastAPI** (`main.py`) - Handles HTTP requests.
- **Redis** (`redis_client.py`) - Caches API responses.
- **Google API Client** (`google_client.py`) - Calls Google Places API.
- **Data Forwarding** (`forward_service.py`) - Sends data to Recommendation Service.

---

## **🛠️ Technologies Used**
| **Technology** | **Usage** |
|---------------|----------|
| Python 3.12  | Backend |
| FastAPI      | API Framework |
| Uvicorn      | ASGI Server |
| Redis       | Caching |
| Docker      | Containerization |
| HTTPX       | Async API Calls |
| Pydantic    | Data Validation |

---

## **🚀 Setup & Installation**
### **1️⃣ Clone the Repository**
```sh
git clone https://github.com/your-org/place-wrapper.git
cd place-wrapper
```

### **2️⃣ Create a Virtual Environment (Optional)**
```sh
python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate     # On Windows
```

### **3️⃣ Install Dependencies**
```sh
pip install -r requirements.txt
```

### **4️⃣ Set Up Environment Variables**
Create a `.env` file:
```ini
GOOGLE_MAPS_API_KEY=your_api_key
RECOMMENDATION_SERVICE_URL=http://recommendation-service:8080/process
```

### **5️⃣ Run the Service**
#### **Locally**
```sh
uvicorn app.main:app --reload --port 8080
```
#### **Using Docker**
```sh
docker-compose up --build
```

---

## **📀 Environment Variables**
| Variable | Description |
|----------|------------|
| `GOOGLE_MAPS_API_KEY` | Google API Key for Places API |
| `RECOMMENDATION_SERVICE_URL` | URL of the Recommendation Service |

---

## **🛠️ API Endpoints**
### **📍 Fetch Places from Google API**
#### **`GET /places/`**
Fetches places near a given location and forwards results to the Recommendation Service.

#### **Request Parameters**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `location` | `string` | ✅ | Latitude,Longitude (e.g., `37.7749,-122.4194`) |
| `radius` | `int` | ❌ | Search radius in meters (default: `500`) |
| `keyword` | `string` | ❌ | Search term (e.g., `"cafe"`) |

#### **Example Request**
```sh
curl -X GET "http://localhost:8080/places/?location=37.7749,-122.4194&radius=1000&keyword=cafe"
```

#### **Example Response**
```json
{
  "normalized_places": [
    {
      "id": "ChIJN1t_tDeuEmsRUsoyG83frY4",
      "name": "Awesome Coffee Shop",
      "location": { "lat": 37.7749, "lng": -122.4194 },
      "rating": 4.5,
      "types": ["cafe", "food", "establishment"],
      "address": "123 Market St, San Francisco, CA",
      "price_level": 2,
      "opening_hours": true
    }
  ]
}
```

---

## **🔀 Data Flow**
1. User calls `/places/?location=37.7749,-122.4194&radius=1000&keyword=cafe`
2. Service **checks Redis** for cached response.
3. If not cached, service **fetches data** from Google API.
4. Response is **normalized** to a standard format.
5. Data is **cached in Redis** for efficiency.
6. Normalized response is **forwarded to the Recommendation Service**.
7. User receives the structured response.

---