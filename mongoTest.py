import json
import uuid
from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient


def entityMapper(entityid):
    ENTITY_MAP = {
        "60": "JOURNALEVENTS",
        "8": "MEETINGS",
        "12": "PERSONS",
        "15": "VISITORS",
    }
    return ENTITY_MAP.get(str(entityid), "UnknownEntity")


# Custom JSON encoder to handle datetime, ObjectId, etc.
def json_serializer(obj):
    if isinstance(obj, (datetime,)):
        return obj.isoformat()
    if isinstance(obj, ObjectId):
        return str(obj)
    return str(obj)  # fallback for other non-serializable types


def test_mongo_connection(entityid, ids):
    client = MongoClient("mongodb://sa:Nebula=2020@192.168.1.240:27017/")

    try:
        db = client["nebula"]
        collection_name = entityMapper(entityid)
        collection = db[collection_name]

        qry = {"_id": {"$in": ids}}
        cur = collection.find(qry)
        results = list(cur)

        # Convert ObjectId → str (redundant but safe)
        for r in results:
            if "_id" in r:
                r["_id"] = str(r["_id"])

        # Generate unique filename
        guid = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{collection_name}_{guid}_{timestamp}.json"

        # Write results safely
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False, default=json_serializer)

        print(f"✅ Results saved to: {filename}")
        return filename

    finally:
        client.close()


# Example usage
test_mongo_connection(60, [1, 1481, 1482])
