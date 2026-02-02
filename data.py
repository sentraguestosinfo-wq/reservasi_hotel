# data.py

# Hotel Coordinates (Mercure Bandung Nexa Supratman)
HOTEL_COORDS = {"lat": -6.9088, "lng": 107.6285}

ROOMS = [
    {
        "id": "superior",
        "price": 850000,
        "image": "https://images.unsplash.com/photo-1618773928121-c32242e63f39?q=80&w=2070&auto=format&fit=crop",
        "name": {
            "id": "Superior Room",
            "en": "Superior Room",
            "cn": "高级房"
        },
        "desc": {
            "id": "Kamar modern seluas 24 m² dengan desain kontemporer. Pilihan tempat tidur King atau Twin. Wi-Fi kecepatan tinggi gratis.",
            "en": "Modern 24 m² room with contemporary design. King or Twin bed options. Free high-speed Wi-Fi.",
            "cn": "24平方米的现代客房，设计时尚。提供特大床或双床选择。免费高速无线网络。"
        }
    },
    {
        "id": "deluxe",
        "price": 1250000,
        "image": "https://images.unsplash.com/photo-1591088398332-8a7791972843?q=80&w=1974&auto=format&fit=crop",
        "name": {
            "id": "Deluxe Room",
            "en": "Deluxe Room",
            "cn": "豪华房"
        },
        "desc": {
            "id": "Kamar luas 32 m² dengan pemandangan kota. Dilengkapi minibar gratis dan akses ke Executive Lounge.",
            "en": "Spacious 32 m² room with city views. Includes free minibar and access to Executive Lounge.",
            "cn": "32平方米的宽敞客房，享有城市景观。包括免费迷你吧和行政酒廊使用权。"
        }
    },
    {
        "id": "executive",
        "price": 2500000,
        "image": "https://images.unsplash.com/photo-1578683010236-d716f9a3f461?q=80&w=2070&auto=format&fit=crop",
        "name": {
            "id": "Executive Suite",
            "en": "Executive Suite",
            "cn": "行政套房"
        },
        "desc": {
            "id": "Suite mewah 48 m² dengan ruang tamu terpisah. Fasilitas premium dan sarapan gratis untuk 2 orang.",
            "en": "Luxury 48 m² suite with separate living area. Premium amenities and free breakfast for 2.",
            "cn": "48平方米的豪华套房，设有独立起居区。高档设施和2人免费早餐。"
        }
    }
]

FACILITIES = [
    {
        "icon": "fa-utensils",
        "name": {"id": "Nexa Resto", "en": "Nexa Resto", "cn": "Nexa 餐厅"},
        "desc": {"id": "Sajian Internasional & Lokal", "en": "International & Local Cuisine", "cn": "国际与当地美食"}
    },
    {
        "icon": "fa-spa",
        "name": {"id": "Spa & Wellness", "en": "Spa & Wellness", "cn": "水疗与健康"},
        "desc": {"id": "Pijat Tradisional & Modern", "en": "Traditional & Modern Massage", "cn": "传统与现代按摩"}
    },
    {
        "icon": "fa-swimming-pool",
        "name": {"id": "Indoor Pool", "en": "Indoor Pool", "cn": "室内泳池"},
        "desc": {"id": "Kolam renang air hangat", "en": "Heated Swimming Pool", "cn": "温水游泳池"}
    },
    {
        "icon": "fa-users",
        "name": {"id": "Ballroom", "en": "Ballroom", "cn": "宴会厅"},
        "desc": {"id": "Kapasitas hingga 500 orang", "en": "Capacity up to 500 people", "cn": "可容纳多达500人"}
    },
    {
        "icon": "fa-wifi",
        "name": {"id": "High-Speed WiFi", "en": "High-Speed WiFi", "cn": "高速WiFi"},
        "desc": {"id": "Akses internet cepat di seluruh area", "en": "Fast internet access in all areas", "cn": "全覆盖高速互联网接入"}
    }
]

MALLS = [
    {
        "name": "Trans Studio Mall (TSM)",
        "coords": "-6.926123, 107.636543",
        "distance": "3.5 km",
        "desc": {
            "id": "Pusat perbelanjaan terintegrasi dengan taman hiburan indoor.",
            "en": "Integrated shopping center with indoor theme park.",
            "cn": "集室内主题公园于一体的综合购物中心。"
        }
    },
    {
        "name": "Cihampelas Walk (Ciwalk)",
        "coords": "-6.896543, 107.605678",
        "distance": "4.2 km",
        "desc": {
            "id": "Mall dengan konsep ruang terbuka hijau yang asri.",
            "en": "Mall with a beautiful green open space concept.",
            "cn": "拥有美丽绿色开放空间概念的购物中心。"
        }
    },
    {
        "name": "Paris Van Java (PVJ)",
        "coords": "-6.889765, 107.596234",
        "distance": "5.1 km",
        "desc": {
            "id": "Resort lifestyle place dengan nuansa Eropa.",
            "en": "Resort lifestyle place with European nuances.",
            "cn": "充满欧洲风情的度假生活方式场所。"
        }
    },
    {
        "name": "Bandung Indah Plaza (BIP)",
        "coords": "-6.908234, 107.610987",
        "distance": "2.0 km",
        "desc": {
            "id": "Mall legendaris di pusat kota Bandung.",
            "en": "Legendary mall in the center of Bandung city.",
            "cn": "万隆市中心的传奇购物中心。"
        }
    },
    {
        "name": "23 Paskal Shopping Center",
        "coords": "-6.914567, 107.596789",
        "distance": "4.8 km",
        "desc": {
            "id": "Mall modern dengan berbagai brand internasional.",
            "en": "Modern mall with various international brands.",
            "cn": "拥有各种国际品牌的现代购物中心。"
        }
    }
]

ATMS = [
    {
        "name": "ATM BCA (Indomaret Supratman)",
        "coords": "-6.908543, 107.629123",
        "desc": {"id": "24 Jam", "en": "24 Hours", "cn": "24小时"}
    },
    {
        "name": "ATM Mandiri (Cabang Supratman)",
        "coords": "-6.907654, 107.628987",
        "desc": {"id": "Lengkap dengan setor tunai", "en": "Complete with cash deposit", "cn": "配备现金存款功能"}
    },
    {
        "name": "ATM BNI (SPBU Supratman)",
        "coords": "-6.909876, 107.627890",
        "desc": {"id": "Akses mudah parkir", "en": "Easy parking access", "cn": "停车方便"}
    },
    {
        "name": "ATM BRI",
        "coords": "-6.908999, 107.628456",
        "desc": {"id": "Dekat lobi hotel", "en": "Near hotel lobby", "cn": "靠近酒店大堂"}
    }
]
