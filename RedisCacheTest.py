import os
import json
import requests
import redis
import urllib3
from fabric.build.lib.encryption.nebulaEncryption import NebulaEncryption

# Disable SSL warning (dev only)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class NebulaVaultClient:
    def __init__(self):

        self.base_url = os.getenv("NEBULA_VAULT_URL", "https://192.168.1.236:8443")
        self.username = os.getenv("NEBULA_VAULT_USERNAME", "admin")
        self.password = os.getenv("NEBULA_VAULT_PASSWORD", "admin")
        self.secret_key = os.getenv("NEBULA_SECRET_KEY", "NEBULA")
        self.secret_salt = os.getenv("NEBULA_SECRET_SALT", "2022")

        # =======================
        # REDIS CONFIG
        # =======================
        self.redis = redis.Redis(
            host=os.getenv("REDIS_HOST", "192.168.1.235"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=os.getenv("REDIS_DB", 0),
            username=os.getenv("REDIS_USERNAME", "sa"),
            password=os.getenv("REDIS_PASSWORD", "Nebula=2020"),
            decode_responses=True
        )

        self.cache_ttl = int(os.getenv("CACHE_TTL", 3000000))  # seconds

        # =======================
        # INIT
        # =======================
        self.token = None
        self.encryption = NebulaEncryption(self.secret_key, self.secret_salt)

    # =======================
    # AUTH
    # =======================
    def login(self):
        url = f"{self.base_url}/api/login"

        payload = {
            "username": self.username,
            "password": self.password
        }

        response = requests.post(url, json=payload, verify=False)
        response.raise_for_status()

        self.token = response.json()["token"]
        print("✅ Logged in")

    def logout(self):
        url = f"{self.base_url}/api/logout"
        response = requests.post(url, headers=self._headers(), verify=False)
        response.raise_for_status()
        print("✅ Logged out")

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.token}"
        }

    # =======================
    # COMMON HELPERS
    # =======================
    def _decrypt_and_parse(self, response):
        encrypted = response.json()["data"]
        decrypted = self.encryption.decrypt(encrypted)

        if isinstance(decrypted, str):
            return json.loads(decrypted)
        return decrypted

    def _get_cache(self, key):
        data = self.redis.get(key)
        if data:
            print(f"⚡ Cache hit → {key}")
            return json.loads(data)
        return None

    def _set_cache(self, key, value):
        self.redis.setex(key, self.cache_ttl, json.dumps(value))

    def _invalidate_cache(self, pattern="vault:*"):
        for key in self.redis.scan_iter(pattern):
            self.redis.delete(key)
        print("🧹 Cache invalidated")

    # =======================
    # VAULT APIs (CACHED)
    # =======================
    def get_all_entries(self):
        cache_key = "vaultAllEntries"

        cached = self._get_cache(cache_key)
        if cached:
            return cached

        print("🌐 Fetching from API → all entries")

        url = f"{self.base_url}/api/vault/entries"
        response = requests.get(url, headers=self._headers(), verify=False)

        data = self._decrypt_and_parse(response)

        self._set_cache(cache_key, data)
        return data

    def get_entries_by_category(self, category):
        cache_key = f"vaultEntriesByCategory:{category}"

        cached = self._get_cache(cache_key)
        if cached:
            return cached

        print(f"🌐 Fetching from API → category={category}")

        url = f"{self.base_url}/api/vault/entries/category/{category}"
        response = requests.get(url, headers=self._headers(), verify=False)

        data = self._decrypt_and_parse(response)

        self._set_cache(cache_key, data)
        return data

    def get_entry(self, key):
        cache_key = f"vaultEntryByKey:{key}"

        cached = self._get_cache(cache_key)
        if cached:
            return cached

        print(f"🌐 Fetching from API → key={key}")

        url = f"{self.base_url}/api/vault/entries/{key}"
        response = requests.get(url, headers=self._headers(), verify=False)

        data = self._decrypt_and_parse(response)

        self._set_cache(cache_key, data)
        return data

    # =======================
    # WRITE APIs (Invalidate Cache)
    # =======================
    def create_entry(self, entry):
        url = f"{self.base_url}/api/vault/entries"
        response = requests.post(url, json=entry, headers=self._headers(), verify=False)

        data = self._decrypt_and_parse(response)

        self._invalidate_cache()
        return data

    def update_entry(self, key, entry):
        url = f"{self.base_url}/api/vault/entries/{key}"
        response = requests.put(url, json=entry, headers=self._headers(), verify=False)

        data = self._decrypt_and_parse(response)

        self._invalidate_cache()
        return data

    def delete_entry(self, key):
        url = f"{self.base_url}/api/vault/entries/{key}"
        response = requests.delete(url, headers=self._headers(), verify=False)

        data = self._decrypt_and_parse(response)

        self._invalidate_cache()
        return data

    # =======================
    # HEALTH
    # =======================
    def health_check(self):
        url = f"{self.base_url}/health"
        response = requests.get(url, verify=False)
        return response.status_code == 200


# =======================
# USAGE
# =======================
if __name__ == "__main__":
    client = NebulaVaultClient()

    client.login()
    print("\n📂 Categories:")
    print(client.get_entries_by_category("Redis"))
    print(client.get_entry("REDISHOST"))
    client.logout()